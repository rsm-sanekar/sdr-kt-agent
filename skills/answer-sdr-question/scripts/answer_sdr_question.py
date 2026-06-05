"""LLM skill: answer a free-form SDR question with citation-grounded sources.

Standalone Q&A capability — NOT part of the 4-step chain. The envelope's
``next_action`` is always ``"done"``; this skill never hands off to another step.

Retrieval uses the embedding-based retriever in ``rag/embeddings_retrieval.py``
(ChromaDB + DefaultEmbeddingFunction), NOT the BM25 retriever used by the
chain. Free-form human questions need semantic match; machine-generated
chain queries don't.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from rag.embeddings_retrieval import (  # noqa: E402
    LOW_CONFIDENCE_THRESHOLD,
    EmbedChunk,
    build_sources,
    ensure_index,
    retrieve,
)
from utils.connect import ask_json  # noqa: E402
from utils.sdr_common import (  # noqa: E402
    make_envelope,
    make_skill_parser,
    run_step,
)

BASE_SYSTEM_PROMPT = (
    "You are an SDR onboarding tutor at Salesforce. You MUST return a JSON "
    "object with the required fields (answer, next_step, confidence) filled "
    "in with real content — never echo the schema definition itself.\n\n"
    "Answer the question using ONLY the numbered sources below. Cite sources "
    "inline with [n] where the claim appears. Keep your answer under 200 "
    "words, in plain language a brand-new SDR can follow.\n\n"
    "`next_step` MUST be a verb-noun action the SDR can do in the next hour. "
    "Name WHO to message (Trail Guide, AE, IT, SDR manager, People Ops), "
    "WHICH channel (a specific Slack channel like #sdr-help, or a named "
    "tool), and WHAT to send or ask. Generic phrasings like 'ask your "
    "manager', 'talk to your AE', or 'review the docs' without specifics "
    "fail this rule.\n\n"
    "Any specific identifier (module IDs like TRAIL-XXX-NNN, policy codes "
    "like LMG-NNNN, person names, dollar figures, dates, channel names) "
    "MUST appear verbatim in one of the numbered sources. If you cannot "
    "point to a source for an identifier, omit it and answer at one level "
    "of abstraction higher.\n\n"
    "BEFORE answering, decide whether the question is too broad — a question "
    "is too broad if a reasonable answer could go five different directions "
    "(e.g. 'how do I get better at my job?', 'what should I know?'). For a "
    "too-broad question you MUST NOT dump general advice. Instead, the "
    "`answer` must (a) state the question is too broad to answer from the "
    "knowledge base directly, (b) propose 2-3 narrower questions, and "
    "(c) recommend a 1:1 with their Trail Guide or SDR manager. The "
    "`next_step` must still be specific (e.g. 'Slack [name] in #sdr-help "
    "with one of the narrower questions above').\n\n"
    "If the sources do not contain the answer, say so explicitly and "
    "recommend who to ask (a Trail Guide, the SDR manager, or People Ops). "
    "Even when refusing, the answer must cite at least one [n] from the "
    "sources you DID retrieve (to show what was checked), and `next_step` "
    "must still be a specific verb-noun action."
)


class TutorAnswer(BaseModel):
    answer: str = Field(min_length=20)
    next_step: str = Field(min_length=5)
    confidence: float = Field(ge=0, le=1)


def _format_sources(chunks: list[EmbedChunk]) -> str:
    sections = []
    for i, c in enumerate(chunks, start=1):
        sections.append(f"[{i}] (source: {c.doc_name}, relevance: {c.score:.2f})\n{c.passage}")
    return "\n\n".join(sections)


def _build_user_prompt(question: str, chunks: list[EmbedChunk]) -> str:
    if chunks:
        return (
            f"SDR Question: {question}\n\n"
            f"Sources:\n\n{_format_sources(chunks)}\n\n"
            "Answer the question, citing [n] inline. End with one concrete next step."
        )
    return (
        f"SDR Question: {question}\n\n"
        "No relevant sources were found in the knowledge base. "
        "Say that explicitly and recommend who to ask."
    )


def do_work(args) -> dict:
    question = (getattr(args, "question", "") or "").strip()
    if not question:
        return make_envelope(
            status="error",
            error={"code": "question_missing", "message": "--question is required for the tutor skill"},
        )

    ensure_index()
    chunks = retrieve(question, top_k=5)
    best_score = max((c.score for c in chunks), default=0.0)
    flagged = best_score < LOW_CONFIDENCE_THRESHOLD

    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock is not None:
        result = TutorAnswer.model_validate_json(mock)
    else:
        result = ask_json(
            _build_user_prompt(question, chunks),
            schema=TutorAnswer,
            system=BASE_SYSTEM_PROMPT,
            model="claude-sonnet-4-6",
        )

    review_required = flagged or result.confidence < 0.60

    sources = build_sources(chunks)

    return make_envelope(
        status="needs_review" if review_required else "ok",
        next_action="done",
        confidence=result.confidence,
        review_required=review_required,
        artifact_refs=[],
        outputs={
            "question": question,
            "answer": result.answer,
            "next_step": result.next_step,
            "sources": sources,
            "confidence_score": round(best_score, 4),
            "flagged": flagged,
        },
    )


def main() -> int:
    parser = make_skill_parser("LLM skill: answer a free-form SDR question with citations (AI Tutor)")
    parser.add_argument("--question", default="", help="The SDR's free-form question.")
    args = parser.parse_args()
    return run_step(args, do_work)


if __name__ == "__main__":
    raise SystemExit(main())
