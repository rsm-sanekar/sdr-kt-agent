"""LLM skill: synthesize a post-certification onboarding debrief.

Standalone tool — invoked by `/offboarding/synthesize` on workflow_server.py
(route name kept for stability). After an SDR passes certification they answer a
short set of process/experience questions; this skill synthesizes their answers
into a manager-facing debrief — what worked, what was confusing, barriers to
ramp, and concrete suggestions to improve the onboarding program. RAG context
from the territory + vertical playbook grounds any program references. Low
confidence triggers manager review.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

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


class ElementFeedback(BaseModel):
    element: str = Field(min_length=2)  # e.g. Onboarding plan, AI Tutor, Cold-call sim, Coaching, Territory playbook
    what_worked: str = Field(min_length=5)
    what_to_improve: str = Field(min_length=5)


class DebriefDoc(BaseModel):
    summary: str = Field(min_length=40)
    elements: list[ElementFeedback] = Field(min_length=1, max_length=6)
    ramp_barriers: list[str] = Field(min_length=1, max_length=5)
    program_strengths: list[str] = Field(min_length=1, max_length=5)
    suggested_improvements: list[str] = Field(min_length=1, max_length=5)
    confidence: float = Field(ge=0, le=1)


ElementFeedback.model_rebuild()
DebriefDoc.model_rebuild()


BASE_SYSTEM_PROMPT = (
    "You are a Salesforce enablement specialist synthesizing a "
    "post-certification onboarding debrief from a newly-certified SDR's "
    "self-assessment of their 12-week ramp. The debrief is read by the SDR's "
    "Manager and the enablement team to improve the onboarding program — it is "
    "NOT a customer/account handoff. "
    "You MUST return a JSON object with the required fields (summary, elements, "
    "ramp_barriers, program_strengths, suggested_improvements, confidence) "
    "filled with real content — never echo the schema definition itself.\n"
    "\n"
    "Synthesis rules:\n"
    "- elements: for each onboarding component the SDR spoke to (Onboarding plan, "
    "AI Tutor, Cold-call simulation, Coaching, Territory/vertical playbook), give "
    "the element name, what_worked (concrete, from their answers), and "
    "what_to_improve (a specific, actionable gap — no platitudes). 1-6 elements.\n"
    "- ramp_barriers: 1-5 concrete things that slowed the SDR's ramp "
    "(process, knowledge, tooling, confidence) — only what the answers support.\n"
    "- program_strengths: 1-5 parts of the program worth keeping.\n"
    "- suggested_improvements: 1-5 specific, actionable changes the enablement "
    "team could make next cohort.\n"
    "- summary: a 3-5 sentence memo for the Manager tying the debrief together.\n"
    "- confidence: float 0-1. Lower it if the answers were sparse, generic, or "
    "contradicted each other."
)


def _load_interview(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("interview file must be a JSON object")
    rep_info = data.get("rep_info")
    qa_pairs = data.get("qa_pairs")
    if not isinstance(rep_info, dict):
        raise ValueError("interview file missing 'rep_info' object")
    if not isinstance(qa_pairs, list) or not qa_pairs:
        raise ValueError("interview file missing or empty 'qa_pairs' list")
    return data


def _format_context(chunks) -> str:
    sections = [f"### {c.doc_name}\n{c.text}" for c in chunks]
    return (
        "Reference internal documents (use these when relevant; do not invent "
        "details that contradict them):\n\n" + "\n\n".join(sections)
    )


def _system_prompt(chunks) -> str:
    if not chunks:
        return BASE_SYSTEM_PROMPT
    return f"{BASE_SYSTEM_PROMPT}\n\n{_format_context(chunks)}"


def _format_qa(qa_pairs: list[dict]) -> str:
    blocks = []
    for qa in qa_pairs:
        q = qa.get("question", f"Question {qa.get('question_id', '?')}")
        a = (qa.get("answer") or "").strip() or "(no answer given)"
        blocks.append(f"Q{qa.get('question_id', '?')}: {q}\nA: {a}")
    return "\n\n".join(blocks)


def _build_user_prompt(rep_info: dict, qa_pairs: list[dict]) -> str:
    lines = [
        f"Newly-certified SDR: {rep_info.get('name', 'unknown')}",
        f"Territory: {rep_info.get('territory', 'unknown')}",
        f"Vertical: {rep_info.get('vertical', 'unknown')}",
        "",
        "Post-certification debrief answers (verbatim):",
        "",
        _format_qa(qa_pairs),
        "",
        "Produce the onboarding debrief as JSON matching the schema.",
    ]
    return "\n".join(lines)


def _render_markdown(rep_info: dict, doc: DebriefDoc, review_reasons: list[str]) -> str:
    lines = [
        f"# Onboarding debrief — {rep_info.get('name', 'SDR')}",
        "",
        (
            f"_{rep_info.get('territory', '?')} · "
            f"{rep_info.get('vertical', '?')} · newly certified_"
        ),
        f"_Synthesis confidence: {doc.confidence}_",
        "",
        "## Summary",
        "",
        doc.summary,
        "",
        "## Experience by element",
        "",
    ]
    for el in doc.elements:
        lines += [
            f"### {el.element}",
            "",
            f"- **What worked:** {el.what_worked}",
            f"- **What to improve:** {el.what_to_improve}",
            "",
        ]

    lines += ["## Barriers to ramp", ""]
    lines += [f"- {item}" for item in doc.ramp_barriers]
    lines += ["", "## What worked well", ""]
    lines += [f"- {item}" for item in doc.program_strengths]
    lines += ["", "## Suggested improvements", ""]
    lines += [f"- {item}" for item in doc.suggested_improvements]
    if review_reasons:
        lines += ["", "## Why manager review is required", ""]
        lines += [f"- {r}" for r in review_reasons]
    return "\n".join(lines) + "\n"


def do_work(args) -> dict:
    interview_file = getattr(args, "interview_file", None)
    if not interview_file:
        return make_envelope(
            status="error",
            error={"code": "interview_file_missing", "message": "--interview-file is required"},
        )

    interview_path = Path(interview_file)
    if not interview_path.exists():
        return make_envelope(
            status="error",
            error={"code": "interview_file_missing", "message": f"{interview_path} not found"},
        )

    try:
        bundle = _load_interview(interview_path)
    except (json.JSONDecodeError, ValueError) as exc:
        return make_envelope(
            status="error",
            error={"code": "interview_file_invalid", "message": str(exc)},
        )

    rep_info = bundle["rep_info"]
    qa_pairs = bundle["qa_pairs"]

    rag_query = (
        f"onboarding program ramp territory {rep_info.get('territory', '')} "
        f"vertical {rep_info.get('vertical', '')} coaching certification "
        "trailhead playbook tutor simulation"
    )
    context_chunks = retrieve(rag_query, build_index(), top_k=4)
    system_prompt = _system_prompt(context_chunks)

    user_prompt = _build_user_prompt(rep_info, qa_pairs)

    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock is not None:
        doc = DebriefDoc.model_validate_json(mock)
    else:
        doc = ask_json(
            user_prompt,
            schema=DebriefDoc,
            system=system_prompt,
            model="claude-sonnet-4-6",
        )

    review_reasons: list[str] = []
    if needs_human_review(doc.confidence, threshold=0.65):
        review_reasons.append(
            f"confidence {doc.confidence:.2f} is below the 0.65 threshold"
        )
    review_required = bool(review_reasons)

    run_dir = ensure_run_dir(args.out_dir, args.workflow_run_id)
    (run_dir / "01_handoff_doc.md").write_text(
        _render_markdown(rep_info, doc, review_reasons)
    )

    return make_envelope(
        status="needs_review" if review_required else "ok",
        next_action="done",
        confidence=doc.confidence,
        review_required=review_required,
        artifact_refs=["01_handoff_doc.md"],
        outputs={
            "rep_name": rep_info.get("name"),
            "territory": rep_info.get("territory"),
            "vertical": rep_info.get("vertical"),
            "n_elements": len(doc.elements),
            "elements": [el.model_dump() for el in doc.elements],
            "ramp_barriers": list(doc.ramp_barriers),
            "program_strengths": list(doc.program_strengths),
            "suggested_improvements": list(doc.suggested_improvements),
            "review_reasons": review_reasons,
            "retrieved_docs": [c.doc_name for c in context_chunks],
            "sources": build_sources(context_chunks),
        },
    )


def main() -> int:
    parser = make_skill_parser(
        "LLM skill: synthesize a post-certification onboarding debrief"
    )
    parser.add_argument("--interview-file", required=False)
    args = parser.parse_args()
    return run_step(args, do_work)


if __name__ == "__main__":
    raise SystemExit(main())
