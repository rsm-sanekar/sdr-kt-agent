from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from embeddings import query
from prompts import TUTOR_RAG_TEMPLATE, TUTOR_SYSTEM

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Lazy client — initialized on first call so a missing key raises a clear
# RuntimeError at call time rather than a cryptic KeyError at import time.
_anthropic: anthropic.Anthropic | None = None


def _get_anthropic() -> anthropic.Anthropic:
    global _anthropic
    if _anthropic is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set — check .env at project root")
        _anthropic = anthropic.Anthropic(api_key=key)
    return _anthropic


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GAP_TRACKER_PATH = os.path.join(_PROJECT_ROOT, "data", "gap_tracker.json")

# Answers below this cosine similarity are flagged for human review.
# The threshold is intentionally conservative — it's better to surface
# a gap than to confidently return a bad answer to a new SDR.
_CONFIDENCE_THRESHOLD = 0.4


def answer_question(question: str) -> dict:
    """
    Full RAG pipeline for the AI Tutor feature (Step 4 of onboarding).

    Retrieves the top-5 most relevant chunks from ChromaDB, builds a
    numbered context block so claude-sonnet-4-6 can cite sources inline,
    calls the model, and returns a structured dict the /tutor/ask endpoint
    can forward to the frontend.

    Returns token_count and model so the ApprovalCard can display them.
    Low-confidence answers set flagged=True; the endpoint decides whether
    to call log_gap().
    """
    chunks = query(question, k=5)

    best_score = chunks[0]["score"] if chunks else 0.0
    flagged = best_score < _CONFIDENCE_THRESHOLD

    # Numbered references let Claude write citations like [1], [2] that
    # map directly back to the source metadata we return.
    context_lines = [
        f"[{i + 1}] (source: {c['source']}, type: {c['type']})\n{c['content']}"
        for i, c in enumerate(chunks)
    ]
    context_block = "\n\n".join(context_lines)

    user_message = TUTOR_RAG_TEMPLATE.format(
        context=context_block,
        question=question,
    )

    response = _get_anthropic().messages.create(
        model="claude-sonnet-4-6",
        system=TUTOR_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
        temperature=0.2,
        max_tokens=512,
    )

    answer_text = response.content[0].text.strip()

    sources = [
        {"source": c["source"], "type": c["type"], "score": c["score"]}
        for c in chunks
    ]

    return {
        "answer": answer_text,
        "sources": sources,
        "confidence_score": best_score,
        "flagged": flagged,
        "model": "claude-sonnet-4-6",
        "token_count": response.usage.input_tokens + response.usage.output_tokens,
    }


def log_gap(question: str) -> None:
    """
    Append a low-confidence or unanswered question to the gap tracker.

    The gap_tracker.json is reviewed periodically by a human who fills
    the gaps manually. Approved answers re-enter ChromaDB via add_qa_pair(),
    closing the self-improving loop described in CLAUDE.md.
    """
    entry = {
        "question": question,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if os.path.exists(_GAP_TRACKER_PATH):
        with open(_GAP_TRACKER_PATH, "r") as f:
            gaps = json.load(f)
    else:
        gaps = []

    gaps.append(entry)

    with open(_GAP_TRACKER_PATH, "w") as f:
        json.dump(gaps, f, indent=2)
