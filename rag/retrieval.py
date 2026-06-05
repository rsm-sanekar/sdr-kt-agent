"""Keyword/BM25 retrieval over the proprietary knowledge base.

The retriever splits every Markdown doc in ``rag/knowledge_base/`` into
paragraph-level chunks, tokenizes them with a small stopword filter, and
scores queries with rank-bm25. No embeddings, no API calls — deterministic
and offline-testable.

Usage::

    from rag.retrieval import build_index, retrieve

    index = build_index()
    for chunk in retrieve("HIPAA compliance", index, top_k=3):
        print(chunk.doc_name, chunk.score, chunk.text[:80])

CLI::

    uv run python rag/retrieval.py "what is the SDR quota ramp schedule?"
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from rank_bm25 import BM25Okapi

KB_DIR = Path(__file__).resolve().parent / "knowledge_base"

_STOPWORDS = frozenset(
    {
        "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "but",
        "is", "are", "was", "were", "be", "been", "being", "have", "has",
        "had", "do", "does", "did", "will", "would", "could", "should",
        "may", "might", "can", "this", "that", "these", "those", "with",
        "from", "by", "at", "as", "it", "its",
    }
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass
class Chunk:
    doc_name: str
    chunk_id: int
    text: str
    score: float


@dataclass
class Index:
    """In-memory BM25 index over a list of chunks."""

    chunks: list[Chunk]
    bm25: BM25Okapi


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, drop stopwords."""
    lowered = text.lower()
    return [tok for tok in _TOKEN_RE.findall(lowered) if tok not in _STOPWORDS]


def _strip_frontmatter(text: str) -> str:
    """Drop a leading YAML frontmatter block delimited by ``---`` lines."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    after = text[end + 4 :]
    return after.lstrip("\n")


def _chunk_document(text: str) -> list[str]:
    """Split a Markdown doc into paragraph chunks on blank lines."""
    body = _strip_frontmatter(text)
    paragraphs = re.split(r"\n\s*\n", body)
    return [p.strip() for p in paragraphs if p.strip()]


def build_index(kb_dir: str | Path = KB_DIR) -> Index:
    """Read every ``.md`` under ``kb_dir`` (recursive, except README.md), chunk, and index.

    Subdirectory files (e.g. ``scraped/meddic.md``) are picked up with their
    relative path as the ``doc_name`` so the source-provenance is clear in
    the UI (top-level KB docs stay as bare filenames).
    """
    kb_path = Path(kb_dir)
    chunks: list[Chunk] = []
    for md_path in sorted(kb_path.rglob("*.md")):
        if md_path.name.lower() == "readme.md":
            continue
        rel = md_path.relative_to(kb_path)
        doc_name = str(rel).replace("\\", "/")
        text = md_path.read_text(encoding="utf-8")
        for chunk_id, paragraph in enumerate(_chunk_document(text)):
            chunks.append(
                Chunk(
                    doc_name=doc_name,
                    chunk_id=chunk_id,
                    text=paragraph,
                    score=0.0,
                )
            )
    tokenized = [_tokenize(c.text) or [""] for c in chunks]
    bm25 = BM25Okapi(tokenized)
    return Index(chunks=chunks, bm25=bm25)


def retrieve(query: str, index: Index, top_k: int = 3) -> list[Chunk]:
    """Score every chunk against ``query`` and return the top_k."""
    query_tokens = _tokenize(query) or [""]
    scores = index.bm25.get_scores(query_tokens)
    ranked = sorted(
        range(len(index.chunks)),
        key=lambda i: (-float(scores[i]), index.chunks[i].doc_name, index.chunks[i].chunk_id),
    )
    top = ranked[:top_k]
    return [
        Chunk(
            doc_name=index.chunks[i].doc_name,
            chunk_id=index.chunks[i].chunk_id,
            text=index.chunks[i].text,
            score=float(scores[i]),
        )
        for i in top
    ]


# BM25 has no calibrated weakness threshold (scores are unbounded and depend on
# corpus + query). Use a *relative* rule: a source is "weak" when its score is
# less than 30% of the top score in the same retrieval. Tunable per-skill if
# needed; pass ``weak_ratio=None`` to disable the flag entirely.
WEAK_RATIO_DEFAULT = 0.30


def build_sources(chunks: list[Chunk], *, weak_ratio: float | None = WEAK_RATIO_DEFAULT) -> list[dict]:
    """Serialize BM25 ``Chunk`` objects into the envelope-output ``sources`` shape.

    Returns a list of ``{doc_name, passage, score, weak}`` dicts. ``weak`` is
    ``True`` when the chunk's score is below ``weak_ratio * max(scores)`` in
    the same list (relative weakness), or always ``False`` when ``weak_ratio``
    is ``None``.

    This is the consistent shape every chain skill threads into
    ``envelope.outputs.sources``. The embedding-based tutor uses an analogous
    helper in ``rag.embeddings_retrieval.build_sources`` so the UI's
    EvidencePanel can render both retriever types the same way.
    """
    if not chunks:
        return []
    if weak_ratio is None:
        threshold = -1.0
    else:
        max_score = max(c.score for c in chunks)
        threshold = max(0.0, weak_ratio * max_score) if max_score > 0 else 0.0
    return [
        {
            "doc_name": c.doc_name,
            "passage": c.text,
            "score": round(float(c.score), 4),
            "weak": c.score < threshold,
        }
        for c in chunks
    ]


if __name__ == "__main__":
    index = build_index()
    query = " ".join(sys.argv[1:]) or "What is the quota ramp schedule for entry-level SDRs?"
    for chunk in retrieve(query, index, top_k=3):
        print(f"[{chunk.score:.2f}] {chunk.doc_name} chunk {chunk.chunk_id}")
        print(chunk.text[:200] + "...")
        print()
