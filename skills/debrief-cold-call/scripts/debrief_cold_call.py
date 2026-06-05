"""LLM skill: debrief a Cold Call Simulation conversation using Coaching Rubric v3.1.

Mirrors the four-dimension rubric used by skills/score-cold-call (opening,
discovery, objection handling, close) but consumes a simulation chat
transcript instead of a recorded sales call. Stateless — the UI POSTs the
full message log and the persona id; the skill replays it for Claude and
produces a structured debrief.

Server-side recompute of the weighted total + review-reasons logic is
duplicated from score-cold-call so the two skills stay self-contained.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from utils.connect import ask_json  # noqa: E402
from utils.sdr_common import (  # noqa: E402
    ensure_run_dir,
    make_envelope,
    make_skill_parser,
    needs_human_review,
    run_step,
)

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

PERSONAS_PATH = REPO_ROOT / "data" / "raw" / "sim_personas.json"


def _find_persona(persona_id: str) -> dict | None:
    if not PERSONAS_PATH.exists():
        return None
    for p in json.loads(PERSONAS_PATH.read_text(encoding="utf-8")):
        if p.get("id") == persona_id:
            return p
    return None


def _system_prompt(persona: dict | None) -> str:
    context = ""
    if persona:
        context = (
            f"The trainee was practicing a cold call against a {persona['vertical']} "
            f"persona — {persona['name']}, {persona['role']} at {persona['company']}. "
            f"Persona personality: {persona['personality']}\n\n"
        )
    return (
        "You are a senior SDR coach debriefing a cold-call simulation. "
        "The trainee just finished a practice run against a role-played "
        "prospect persona. Treat the simulation transcript as if it were a "
        "real call for scoring purposes — Coaching Rubric v3.1 applies the "
        "same way.\n"
        "\n"
        f"{context}"
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
        "Be encouraging — this is practice. Lead with what worked, then make "
        "the critique specific and actionable. The trainee is a learner.\n"
        "\n"
        "You MUST return a JSON object with these fields filled in with real "
        "content — never echo the schema definition itself:\n"
        "  - opening_and_framing:   {score: int 1-10, rationale: one sentence}\n"
        "  - discovery_quality:     {score: int 1-10, rationale: one sentence}\n"
        "  - objection_handling:    {score: int 1-10, rationale: one sentence}\n"
        "  - close_and_next_step:   {score: int 1-10, rationale: one sentence}\n"
        "  - weighted_total:        float 1-10, computed with the weights above\n"
        "  - what_worked:           1-3 bullets (what the trainee did well in THIS practice)\n"
        "  - what_to_improve:       1-3 bullets (concrete, actionable critique)\n"
        '  - language_alternatives: EXACTLY 2 "replace X with Y" rewrites of '
        "specific phrases the trainee used\n"
        "  - confidence:            float 0-1 (your confidence in this scoring)"
    )


def _format_messages(messages: list[dict], persona_name: str) -> str:
    if not messages:
        return "(no turns)"
    lines = []
    for m in messages:
        role = m.get("role", "trainee")
        text = m.get("text", "")
        speaker = persona_name.upper() if role == "prospect" else "TRAINEE"
        lines.append(f"{speaker}: {text}")
    return "\n\n".join(lines)


def _build_user_prompt(persona: dict | None, messages: list[dict]) -> str:
    persona_name = persona["name"] if persona else "Prospect"
    return (
        f"Simulation transcript:\n\n{_format_messages(messages, persona_name)}\n\n"
        "Produce the debrief as JSON matching the schema."
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
    persona: dict | None,
    note: CoachingNote,
    weighted_total: float,
    review_reasons: list[str],
) -> str:
    def dim_block(label: str, ds: DimensionScore) -> list[str]:
        return [f"### {label} — {ds.score}/10", "", ds.rationale, ""]

    persona_line = (
        f"_Practice vs. **{persona['name']}** ({persona['role']}, "
        f"{persona['company']} — {persona['vertical']})_"
        if persona
        else "_Practice run debrief_"
    )

    lines = [
        "# Cold Call Simulation debrief",
        "",
        persona_line,
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
        lines += ["", "## Why review is suggested", ""]
        lines += [f"- {r}" for r in review_reasons]
    return "\n".join(lines) + "\n"


def do_work(args) -> dict:
    persona_id = getattr(args, "persona_id", None)
    persona = _find_persona(persona_id) if persona_id else None

    messages_file = getattr(args, "messages_file", None)
    if not messages_file:
        return make_envelope(
            status="error",
            error={"code": "messages_file_missing", "message": "--messages-file is required"},
        )

    messages_path = Path(messages_file)
    if not messages_path.exists():
        return make_envelope(
            status="error",
            error={"code": "messages_file_missing", "message": f"{messages_path} not found"},
        )

    try:
        messages = json.loads(messages_path.read_text(encoding="utf-8"))
        if not isinstance(messages, list):
            raise ValueError("messages-file must contain a JSON array")
    except (json.JSONDecodeError, ValueError) as exc:
        return make_envelope(
            status="error",
            error={"code": "messages_file_invalid", "message": str(exc)},
        )

    if not messages:
        return make_envelope(
            status="error",
            error={"code": "empty_conversation", "message": "no turns to debrief"},
        )

    system_prompt = _system_prompt(persona)
    user_prompt = _build_user_prompt(persona, messages)

    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock is not None:
        note = CoachingNote.model_validate_json(mock)
    else:
        note = ask_json(
            user_prompt,
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
            f"weighted total {recomputed_total:.2f} is below 4 — below-bar practice run"
        )
    if min_dim < 3:
        review_reasons.append(
            f"lowest dimension scored {min_dim} (below 3) — focus area for next practice"
        )
    if total_drift > 1.0:
        review_reasons.append(
            f"LLM weighted_total ({note.weighted_total:.2f}) drifted {total_drift:.2f} "
            f"from server-recomputed value ({recomputed_total:.2f})"
        )
    review_required = bool(review_reasons)

    run_dir = ensure_run_dir(args.out_dir, args.workflow_run_id)
    (run_dir / "01_simulation_debrief.md").write_text(
        _render_markdown(persona, note, recomputed_total, review_reasons)
    )

    return make_envelope(
        status="needs_review" if review_required else "ok",
        next_action="done",
        confidence=note.confidence,
        review_required=review_required,
        artifact_refs=["01_simulation_debrief.md"],
        outputs={
            "persona_id": persona["id"] if persona else None,
            "persona_name": persona["name"] if persona else None,
            "n_turns": len(messages),
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
        },
    )


def main() -> int:
    parser = make_skill_parser("LLM skill: debrief a Cold Call Simulation against Coaching Rubric v3.1")
    parser.add_argument("--persona-id", required=False)
    parser.add_argument("--messages-file", required=False)
    args = parser.parse_args()
    return run_step(args, do_work)


if __name__ == "__main__":
    raise SystemExit(main())
