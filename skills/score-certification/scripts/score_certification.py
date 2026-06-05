"""LLM skill: 5-dimension certification gap analysis for an SDR.

Reads the SDR's persisted journey record at ``data/sdr_records/<sdr_id>.json``,
resolves the linked simulation transcript(s) and certification exam artifact,
RAG-retrieves the rubric from ``rag/knowledge_base/certification_rubric.md``,
and scores against the 5 rubric dimensions with the 7/5-6/<=4 banding.

Caches the full envelope to ``data/sdr_records/<sdr_id>/gap_analysis.json`` so
the certification roster endpoint can read it without invoking the LLM.

The five dimensions and bands are LOCKED to the rubric document — do not
deviate. See SKILL.md for the contract.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Literal

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

SDR_RECORDS_DIR = REPO_ROOT / "data" / "sdr_records"

DIMENSIONS: tuple[str, ...] = (
    "product_knowledge_accuracy",
    "objection_handling",
    "meddic_application",
    "salesforce_value_messaging",
    "discovery_and_questioning",
)

DIMENSION_LABELS: dict[str, str] = {
    "product_knowledge_accuracy": "Product knowledge accuracy",
    "objection_handling": "Objection handling (Defuse, Discover, Deliver)",
    "meddic_application": "MEDDIC framework application",
    "salesforce_value_messaging": "Salesforce value messaging",
    "discovery_and_questioning": "Discovery and questioning",
}


class CertDimensionFinding(BaseModel):
    score: int = Field(ge=1, le=10)
    evidence_quote: str = Field(min_length=10)
    rationale: str = Field(min_length=10)
    gap_to_close: str = Field(min_length=10)
    coaching_action: str = Field(min_length=5)
    verdict: Literal["pass", "borderline", "fail"]


class CertificationGapAnalysis(BaseModel):
    product_knowledge_accuracy: CertDimensionFinding
    objection_handling: CertDimensionFinding
    meddic_application: CertDimensionFinding
    salesforce_value_messaging: CertDimensionFinding
    discovery_and_questioning: CertDimensionFinding
    overall_recommendation: Literal["PASS", "BORDERLINE", "FAIL"]
    overall_rationale: str = Field(min_length=20)
    confidence: float = Field(ge=0, le=1)


CertificationGapAnalysis.model_rebuild()


def compute_overall(scores: list[int]) -> str:
    """Server-side band logic — the source of truth for PASS/BORDERLINE/FAIL.

    Matches certification_rubric.md exactly:
    - any score <= 4  → FAIL
    - any score in 5-6 → BORDERLINE
    - all scores >= 7 → PASS
    """
    if any(s <= 4 for s in scores):
        return "FAIL"
    if any(s in (5, 6) for s in scores):
        return "BORDERLINE"
    return "PASS"


def verdict_for(score: int) -> str:
    if score <= 4:
        return "fail"
    if score <= 6:
        return "borderline"
    return "pass"


def _load_sdr_record(sdr_id: str) -> dict | None:
    path = SDR_RECORDS_DIR / f"{sdr_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_artifact(rel_path: str) -> str | None:
    """Resolve an artifact path (relative to data/sdr_records/) to its file contents."""
    if not rel_path:
        return None
    full = SDR_RECORDS_DIR / rel_path
    if not full.exists():
        return None
    return full.read_text(encoding="utf-8")


def _gather_primary_artifacts(record: dict) -> tuple[list[dict], list[dict]]:
    """Pull simulation + exam events from the record and resolve their MD files.

    Returns (simulations, exams) where each is a list of dicts:
      {"event": <event dict>, "content": <markdown text or None>}
    """
    simulations: list[dict] = []
    exams: list[dict] = []
    for event in record.get("events", []):
        phase = event.get("phase")
        if phase == "simulation":
            content = _resolve_artifact(event.get("transcript_file", ""))
            simulations.append({"event": event, "content": content})
        elif phase == "exam":
            content = _resolve_artifact(event.get("qa_file", ""))
            exams.append({"event": event, "content": content})
    return simulations, exams


def _system_prompt(rubric_chunks) -> str:
    rubric_block = ""
    if rubric_chunks:
        sections = [f"### {c.doc_name}\n{c.text}" for c in rubric_chunks]
        rubric_block = (
            "\n\nReference rubric (treat as the single source of truth — do not invent "
            "criteria or change weights):\n\n" + "\n\n".join(sections)
        )
    return (
        "You are a senior Salesforce sales trainer conducting an SDR certification "
        "review (Decision Gate 1). You score the candidate against the 5-dimension "
        "rubric below. The trainer makes the final pass/fail call — your output is "
        "advisory.\n"
        "\n"
        "Score each of the 5 dimensions on a 1-10 scale:\n"
        "  1. product_knowledge_accuracy — Salesforce clouds, business outcomes, no "
        "feature dumps, no invented capabilities.\n"
        "  2. objection_handling — Defuse / Discover / Deliver method; acknowledge "
        "first, surface the real concern, reframe to value.\n"
        "  3. meddic_application — Metrics, Economic Buyer, Decision Criteria, "
        "Decision Process, Identify Pain, Champion; weighted heavily because poor "
        "qualification is the most common cause of failed handoffs.\n"
        "  4. salesforce_value_messaging — leads with business outcome, quantifies "
        "value, frames product as investment with return rather than cost.\n"
        "  5. discovery_and_questioning — open-ended questions, listens and builds "
        "on prospect answers, gathers MEDDIC inputs.\n"
        "\n"
        "Scoring bands (LOCKED to the rubric — do not deviate):\n"
        "  - 7-10  passes the dimension\n"
        "  - 5-6   borderline; trainer review required\n"
        "  - 1-4   fails the dimension regardless of others\n"
        "\n"
        "Overall recommendation:\n"
        "  - All dimensions >= 7 → PASS\n"
        "  - Any dimension in 5-6, none below 5 → BORDERLINE\n"
        "  - Any dimension <= 4 → FAIL\n"
        "\n"
        "You MUST return a JSON object with these fields filled in with real "
        "content — never echo the schema definition itself. For each dimension "
        "provide:\n"
        "  - score: int 1-10\n"
        "  - evidence_quote: a direct quote (at least 10 characters) from the SDR's "
        "exam answers or simulation transcript that justifies the score\n"
        "  - rationale: one sentence explaining why this score given the rubric\n"
        "  - gap_to_close: the specific gap (from the rubric's 'common gap' framing)\n"
        "  - coaching_action: the next coaching step (from the rubric's 'coaching action')\n"
        "  - verdict: 'pass' | 'borderline' | 'fail' (will be recomputed server-side)\n"
        "\n"
        "Plus overall_recommendation (PASS|BORDERLINE|FAIL), overall_rationale "
        "(2-3 sentences), confidence (0-1)."
        f"{rubric_block}"
    )


def _format_artifact_block(label: str, content: str | None, event: dict) -> str:
    if not content:
        return f"### {label}\n(no content — artifact file missing)\n"
    date = event.get("date", "unknown date")
    return f"### {label} (recorded {date})\n\n{content.strip()}\n"


def _build_user_prompt(record: dict, simulations: list[dict], exams: list[dict]) -> str:
    sdr_id = record.get("sdr_id", "?")
    name = record.get("name", "?")
    cohort = record.get("cohort", "?")
    territory = record.get("territory", "?")
    level = record.get("experience_level", "?")

    sections: list[str] = []
    sections.append(
        f"Candidate: {name} ({sdr_id})\n"
        f"Cohort: {cohort}\n"
        f"Territory: {territory}\n"
        f"Experience level: {level}\n"
    )
    sections.append("## Certification exam — written assessment\n")
    for i, ex in enumerate(exams, start=1):
        sections.append(_format_artifact_block(f"Exam {i}", ex["content"], ex["event"]))
    sections.append("## Simulation transcripts — practice cold calls\n")
    for i, sim in enumerate(simulations, start=1):
        sections.append(
            _format_artifact_block(
                f"Simulation call {sim['event'].get('call', i)}",
                sim["content"],
                sim["event"],
            )
        )
    sections.append(
        "Produce the gap analysis as JSON matching the CertificationGapAnalysis "
        "schema. Quote evidence directly from the artifacts above."
    )
    return "\n\n".join(sections)


def _findings_for(analysis: CertificationGapAnalysis) -> dict[str, CertDimensionFinding]:
    return {
        "product_knowledge_accuracy": analysis.product_knowledge_accuracy,
        "objection_handling": analysis.objection_handling,
        "meddic_application": analysis.meddic_application,
        "salesforce_value_messaging": analysis.salesforce_value_messaging,
        "discovery_and_questioning": analysis.discovery_and_questioning,
    }


def _weakest_dimension(findings: dict[str, CertDimensionFinding]) -> str:
    return min(findings.items(), key=lambda kv: kv[1].score)[0]


def _render_markdown(
    record: dict,
    findings: dict[str, CertDimensionFinding],
    overall: str,
    overall_rationale: str,
    confidence: float,
    review_reasons: list[str],
    retrieved_docs: list[str],
) -> str:
    badge = {"PASS": "🟢 PASS", "BORDERLINE": "🟡 BORDERLINE", "FAIL": "🔴 FAIL"}[overall]
    lines = [
        f"# Certification gap analysis — {record.get('name', '?')} ({record.get('sdr_id', '?')})",
        "",
        f"**Cohort:** {record.get('cohort', '?')}  •  "
        f"**Territory:** {record.get('territory', '?')}  •  "
        f"**Experience:** {record.get('experience_level', '?')}",
        "",
        f"## Overall recommendation: {badge}",
        "",
        overall_rationale,
        "",
        f"_AI confidence: {confidence:.2f}. The trainer makes the final decision._",
        "",
        "## Dimension scores",
        "",
    ]
    for dim_id in DIMENSIONS:
        f = findings[dim_id]
        verdict_badge = {"pass": "🟢", "borderline": "🟡", "fail": "🔴"}[f.verdict]
        lines += [
            f"### {DIMENSION_LABELS[dim_id]} — {f.score}/10  {verdict_badge} {f.verdict.upper()}",
            "",
            f"**Evidence:** {f.evidence_quote}",
            "",
            f"**Rationale:** {f.rationale}",
            "",
            f"**Gap to close:** {f.gap_to_close}",
            "",
            f"**Coaching action:** {f.coaching_action}",
            "",
        ]
    if review_reasons:
        lines += ["## Why trainer review is required", ""]
        lines += [f"- {r}" for r in review_reasons]
        lines += [""]
    if retrieved_docs:
        lines += ["## Sources retrieved (RAG)", ""]
        lines += [f"- {d}" for d in retrieved_docs]
        lines += [""]
    return "\n".join(lines)


def _write_cache(sdr_id: str, envelope: dict) -> None:
    """Cache the full envelope at data/sdr_records/<sdr_id>/gap_analysis.json."""
    sdr_dir = SDR_RECORDS_DIR / sdr_id
    sdr_dir.mkdir(parents=True, exist_ok=True)
    cache_path = sdr_dir / "gap_analysis.json"
    cache_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")


def do_work(args) -> dict:
    sdr_id = getattr(args, "sdr_id", None)
    if not sdr_id:
        return make_envelope(
            status="error",
            error={"code": "sdr_id_missing", "message": "--sdr-id is required"},
        )

    record = _load_sdr_record(sdr_id)
    if record is None:
        return make_envelope(
            status="error",
            error={
                "code": "sdr_not_found",
                "message": f"data/sdr_records/{sdr_id}.json not found",
            },
        )

    simulations, exams = _gather_primary_artifacts(record)
    if not exams or not any(ex["content"] for ex in exams):
        return make_envelope(
            status="error",
            error={
                "code": "missing_required_artifacts",
                "message": (
                    f"SDR {sdr_id} has no exam artifact — gap analysis requires at "
                    "least one 'exam' event with a readable qa_file."
                ),
            },
        )

    rag_query = (
        "SDR certification rubric product knowledge objection handling MEDDIC value "
        f"messaging discovery questioning {record.get('experience_level', '')}"
    )
    rubric_chunks = retrieve(rag_query, build_index(), top_k=5)
    system_prompt = _system_prompt(rubric_chunks)
    user_prompt = _build_user_prompt(record, simulations, exams)

    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock is not None:
        analysis = CertificationGapAnalysis.model_validate_json(mock)
    else:
        analysis = ask_json(
            user_prompt,
            schema=CertificationGapAnalysis,
            system=system_prompt,
            model="claude-sonnet-4-6",
        )

    findings = _findings_for(analysis)
    scores = [findings[d].score for d in DIMENSIONS]
    computed_overall = compute_overall(scores)

    # Server-side: overwrite per-dimension verdict from score (defensive)
    for dim_id, f in findings.items():
        f.verdict = verdict_for(f.score)  # type: ignore[assignment]

    review_reasons: list[str] = []
    if computed_overall != "PASS":
        review_reasons.append(
            f"server-computed overall recommendation is {computed_overall} — trainer review required"
        )
    if needs_human_review(analysis.confidence, threshold=0.65):
        review_reasons.append(
            f"confidence {analysis.confidence:.2f} is below the 0.65 threshold"
        )
    if analysis.overall_recommendation != computed_overall:
        review_reasons.append(
            f"LLM overall_recommendation ({analysis.overall_recommendation}) differs from "
            f"server-computed ({computed_overall}) — using computed value"
        )

    review_required = bool(review_reasons)

    run_dir = ensure_run_dir(args.out_dir, args.workflow_run_id)
    artifact_name = "01_certification_gap_analysis.md"
    (run_dir / artifact_name).write_text(
        _render_markdown(
            record,
            findings,
            computed_overall,
            analysis.overall_rationale,
            analysis.confidence,
            review_reasons,
            [c.doc_name for c in rubric_chunks],
        )
    )

    dimension_findings = {
        dim_id: {
            "score": f.score,
            "verdict": f.verdict,
            "evidence_quote": f.evidence_quote,
            "rationale": f.rationale,
            "gap_to_close": f.gap_to_close,
            "coaching_action": f.coaching_action,
            "label": DIMENSION_LABELS[dim_id],
        }
        for dim_id, f in findings.items()
    }

    envelope = make_envelope(
        status="needs_review" if review_required else "ok",
        next_action="done",
        confidence=analysis.confidence,
        review_required=review_required,
        artifact_refs=[artifact_name],
        outputs={
            "sdr_id": sdr_id,
            "sdr_name": record.get("name"),
            "cohort": record.get("cohort"),
            "territory": record.get("territory"),
            "overall_recommendation": computed_overall,
            "llm_overall_recommendation": analysis.overall_recommendation,
            "overall_rationale": analysis.overall_rationale,
            "weakest_dimension": _weakest_dimension(findings),
            "dimension_findings": dimension_findings,
            "review_reasons": review_reasons,
            "retrieved_docs": [c.doc_name for c in rubric_chunks],
            "sources": build_sources(rubric_chunks),
        },
    )

    _write_cache(sdr_id, envelope)
    return envelope


def main() -> int:
    parser = make_skill_parser(
        "LLM skill: 5-dimension SDR certification gap analysis from persisted artifacts"
    )
    parser.add_argument("--sdr-id", required=True, help="SDR identifier (e.g. SDR-001)")
    args = parser.parse_args()
    return run_step(args, do_work)


if __name__ == "__main__":
    raise SystemExit(main())
