"""LLM skill: score a cold-call transcript against Coaching Rubric v3.1.

Standalone tool — invoked by the `/coaching/score` endpoint (manager uploads
transcript) and by the orchestrator only if score-cold-call is re-added to a
chain. It is no longer wired into the default 3-step onboarding chain.

Schema mirrors `rag/knowledge_base/cold_call_quality_rubric.md`: four
dimensions (opening, discovery, objection handling, close) each scored 1-10
with a one-sentence rationale, plus a weighted overall on 1-10. The script
re-computes the weighted total server-side and flags drift as a review reason.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import polars as pl
from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from rag.retrieval import build_index, build_sources, retrieve  # noqa: E402
from utils.connect import ask_json  # noqa: E402
from utils.sdr_common import (  # noqa: E402
    ensure_run_dir,
    make_envelope,
    make_skill_parser,
    needs_human_review,
    run_step,
)

# Weights match cold_call_quality_rubric.md (Coaching Rubric v3.1).
WEIGHTS: dict[str, float] = {
    "opening_and_framing": 0.20,
    "discovery_quality": 0.35,
    "objection_handling": 0.25,
    "close_and_next_step": 0.20,
}


class DimensionScore(BaseModel):
    score: int = Field(ge=1, le=10)
    rationale: str = Field(min_length=10)


class CoachingNote(BaseModel):
    opening_and_framing: DimensionScore
    discovery_quality: DimensionScore
    objection_handling: DimensionScore
    close_and_next_step: DimensionScore
    weighted_total: float = Field(ge=1, le=10)
    what_worked: list[str] = Field(min_length=1, max_length=3)
    what_to_improve: list[str] = Field(min_length=1, max_length=3)
    language_alternatives: list[str] = Field(min_length=2, max_length=2)
    confidence: float = Field(ge=0, le=1)


CoachingNote.model_rebuild()


_TONE_BY_LEVEL = {
    "entry": (
        "The hire is brand-new to sales. Lead with what they did well, keep critique "
        "concrete and actionable, and avoid jargon. Be encouraging."
    ),
    "mid": (
        "The hire has 1-3 years of sales experience. Be direct and specific; "
        "assume they know the basics."
    ),
    "senior": (
        "The hire is a senior SDR or transitioning AE. Skip basics, focus on "
        "advanced tactics (discovery depth, multi-threading, advanced objection "
        "handling). Be pointed."
    ),
}


def _system_prompt(experience_level: str) -> str:
    tone = _TONE_BY_LEVEL.get(experience_level, _TONE_BY_LEVEL["mid"])
    return (
        "You are a senior SDR coach reviewing a cold-call transcript. "
        f"{tone} "
        "Score the call against Salesforce Coaching Rubric v3.1, which scores "
        "FOUR dimensions on a 1-10 scale and collapses them into a weighted total:\n"
        "  - opening_and_framing  (weight 0.20) — did the rep state who/why and "
        "earn 30 more seconds in the first 15?\n"
        "  - discovery_quality    (weight 0.35) — how many qualified questions, "
        "and how well did the rep follow up on prospect answers?\n"
        "  - objection_handling   (weight 0.25) — did the rep use the "
        "Acknowledge-Reframe-Redirect pattern?\n"
        "  - close_and_next_step  (weight 0.20) — was a specific, calendared next "
        "step proposed and accepted?\n"
        "\n"
        "Apply common rubric deductions: talking past prospect (-1 to -2), "
        "pitch dumping (-2), unapproved claims / named-competitor comparisons "
        "(-3 and escalate), skipping the verbal recap of next steps (-1).\n"
        "\n"
        "You MUST return a JSON object with these fields filled in with real "
        "content — never echo the schema definition itself:\n"
        "  - opening_and_framing:   {score: int 1-10, rationale: one sentence}\n"
        "  - discovery_quality:     {score: int 1-10, rationale: one sentence}\n"
        "  - objection_handling:    {score: int 1-10, rationale: one sentence}\n"
        "  - close_and_next_step:   {score: int 1-10, rationale: one sentence}\n"
        "  - weighted_total:        float 1-10, computed with the weights above\n"
        "  - what_worked:           1-3 bullets (what the rep did well in THIS call)\n"
        "  - what_to_improve:       1-3 bullets (concrete, actionable critique)\n"
        '  - language_alternatives: EXACTLY 2 "replace X with Y" rewrites of '
        "specific phrases the rep used\n"
        "  - confidence:            float 0-1 (your confidence in this scoring)"
    )


def _format_context(chunks) -> str:
    sections = [f"### {c.doc_name}\n{c.text}" for c in chunks]
    return (
        "Reference internal documents (use these when relevant; do not invent "
        "details that contradict them):\n\n" + "\n\n".join(sections)
    )


def _system_prompt_with_context(experience_level: str, chunks) -> str:
    base = _system_prompt(experience_level)
    if not chunks:
        return base
    return f"{base}\n\n{_format_context(chunks)}"


def _format_transcript(messages: list[dict]) -> str:
    lines = []
    for m in messages:
        role = m.get("role", "?").upper()
        text = m.get("text", "")
        lines.append(f"{role}: {text}")
    return "\n\n".join(lines)


def _build_user_prompt(hire: dict, transcript: dict) -> str:
    context = transcript.get("call_context")
    context_line = f"Call context: {context}\n" if context else ""
    return (
        f"Hire: {hire['name']} ({hire['hire_id']}), "
        f"{hire['experience_level']} SDR in {hire['vertical']} / {hire['territory']}.\n"
        f"Call outcome: {transcript.get('outcome', 'unknown')}\n"
        f"{context_line}\n"
        "Transcript:\n"
        f"{_format_transcript(transcript.get('messages', []))}\n\n"
        "Produce the coaching note as JSON matching the schema."
    )


def _compute_weighted_total(note: CoachingNote) -> float:
    total = (
        note.opening_and_framing.score * WEIGHTS["opening_and_framing"]
        + note.discovery_quality.score * WEIGHTS["discovery_quality"]
        + note.objection_handling.score * WEIGHTS["objection_handling"]
        + note.close_and_next_step.score * WEIGHTS["close_and_next_step"]
    )
    return round(total, 2)


def _min_dimension(note: CoachingNote) -> int:
    return min(
        note.opening_and_framing.score,
        note.discovery_quality.score,
        note.objection_handling.score,
        note.close_and_next_step.score,
    )


def _render_markdown(
    hire: dict,
    transcript: dict,
    note: CoachingNote,
    weighted_total: float,
    review_reasons: list[str],
) -> str:
    def dim_block(label: str, ds: DimensionScore) -> list[str]:
        return [f"### {label} — {ds.score}/10", "", ds.rationale, ""]

    lines = [
        f"# Coaching note — {hire['name']} ({hire['hire_id']})",
        "",
        f"**Outcome:** {transcript.get('outcome', 'unknown')}",
        f"**Overall score (weighted):** {weighted_total:.2f}/10",
        f"**Coach confidence:** {note.confidence}",
        "",
        "## Dimension scores",
        "",
    ]
    lines += dim_block("Opening & framing (0.20)", note.opening_and_framing)
    lines += dim_block("Discovery quality (0.35)", note.discovery_quality)
    lines += dim_block("Objection handling (0.25)", note.objection_handling)
    lines += dim_block("Close & next step (0.20)", note.close_and_next_step)
    lines += ["## What worked", ""]
    lines += [f"- {item}" for item in note.what_worked]
    lines += ["", "## What to improve", ""]
    lines += [f"- {item}" for item in note.what_to_improve]
    lines += ["", "## Language alternatives", ""]
    lines += [f"- {item}" for item in note.language_alternatives]
    if review_reasons:
        lines += ["", "## Why manager review is required", ""]
        lines += [f"- {r}" for r in review_reasons]
    return "\n".join(lines) + "\n"


def do_work(args) -> dict:
    profiles_path = Path(args.data_dir) / "raw" / "sdr_profiles.csv"
    if not profiles_path.exists():
        return make_envelope(
            status="error",
            error={"code": "profiles_missing", "message": f"{profiles_path} not found"},
        )

    sdrs = pl.read_csv(profiles_path)
    row = sdrs.filter(pl.col("hire_id") == args.hire_id)
    if row.is_empty():
        return make_envelope(
            status="error",
            error={
                "code": "hire_not_found",
                "message": f"hire_id {args.hire_id!r} not present in {profiles_path}",
            },
        )
    hire = row.row(0, named=True)

    transcript_path = Path(args.transcript_file)
    if not transcript_path.exists():
        return make_envelope(
            status="error",
            error={
                "code": "transcript_not_found",
                "message": f"{transcript_path} not found",
            },
        )
    transcript = json.loads(transcript_path.read_text())

    rag_query = (
        f"cold call coaching rubric scoring opening discovery objection close "
        f"{hire['vertical']} {transcript.get('outcome', '')}"
    )
    context_chunks = retrieve(rag_query, build_index(), top_k=3)
    system_prompt = _system_prompt_with_context(hire["experience_level"], context_chunks)

    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock is not None:
        note = CoachingNote.model_validate_json(mock)
    else:
        note = ask_json(
            _build_user_prompt(hire, transcript),
            schema=CoachingNote,
            system=system_prompt,
            model="claude-sonnet-4-6",
        )

    recomputed_total = _compute_weighted_total(note)
    total_drift = abs(note.weighted_total - recomputed_total)
    min_dim = _min_dimension(note)

    review_reasons: list[str] = []
    if needs_human_review(note.confidence, threshold=0.70):
        review_reasons.append(
            f"confidence {note.confidence:.2f} is below the 0.70 threshold"
        )
    if recomputed_total < 4.0:
        review_reasons.append(
            f"weighted total {recomputed_total:.2f} is below 4 — below-bar performance per rubric v3.1"
        )
    if min_dim < 3:
        review_reasons.append(
            f"lowest dimension scored {min_dim} (below 3) — investigate that single dimension"
        )
    if total_drift > 1.0:
        review_reasons.append(
            f"LLM weighted_total ({note.weighted_total:.2f}) drifted {total_drift:.2f} "
            f"from server-recomputed value ({recomputed_total:.2f})"
        )
    review_required = bool(review_reasons)

    run_dir = ensure_run_dir(args.out_dir, args.workflow_run_id)
    (run_dir / "04_coaching_note.md").write_text(
        _render_markdown(hire, transcript, note, recomputed_total, review_reasons)
    )

    return make_envelope(
        status="needs_review" if review_required else "ok",
        next_action="done",
        confidence=note.confidence,
        review_required=review_required,
        artifact_refs=["04_coaching_note.md"],
        outputs={
            "hire_id": hire["hire_id"],
            "weighted_total": recomputed_total,
            "llm_weighted_total": round(note.weighted_total, 2),
            "weighted_total_drift": round(total_drift, 2),
            "dimension_scores": {
                "opening_and_framing": {
                    "score": note.opening_and_framing.score,
                    "rationale": note.opening_and_framing.rationale,
                    "weight": WEIGHTS["opening_and_framing"],
                },
                "discovery_quality": {
                    "score": note.discovery_quality.score,
                    "rationale": note.discovery_quality.rationale,
                    "weight": WEIGHTS["discovery_quality"],
                },
                "objection_handling": {
                    "score": note.objection_handling.score,
                    "rationale": note.objection_handling.rationale,
                    "weight": WEIGHTS["objection_handling"],
                },
                "close_and_next_step": {
                    "score": note.close_and_next_step.score,
                    "rationale": note.close_and_next_step.rationale,
                    "weight": WEIGHTS["close_and_next_step"],
                },
            },
            "what_worked": note.what_worked,
            "what_to_improve": note.what_to_improve,
            "language_alternatives": note.language_alternatives,
            "review_reasons": review_reasons,
            "outcome": transcript.get("outcome"),
            "retrieved_docs": [c.doc_name for c in context_chunks],
            "sources": build_sources(context_chunks),
        },
    )


def main() -> int:
    parser = make_skill_parser("LLM skill: score a cold-call transcript with coaching feedback")
    parser.add_argument(
        "--transcript-file",
        default="tests/skills/fixtures/sample_transcript.json",
    )
    args = parser.parse_args()
    return run_step(args, do_work)


if __name__ == "__main__":
    raise SystemExit(main())
