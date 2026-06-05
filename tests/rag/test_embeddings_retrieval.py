"""Tests for rag/embeddings_retrieval.py — ChromaDB tutor retriever.

These tests use a tmp persist dir so they don't touch ``data/chroma_db/``.
ChromaDB's default embedding function downloads ~80MB the first time the
test runs; subsequent runs use the local cache.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rag.embeddings_retrieval import (
    LOW_CONFIDENCE_THRESHOLD,
    EmbedChunk,
    add_approved_qa,
    build_index,
    build_sources,
    collection_size,
    ensure_index,
    reset_collection_cache,
    retrieve,
)


@pytest.fixture
def tmp_persist(tmp_path: Path) -> Path:
    """Per-test persist dir + cache reset so each test gets a fresh collection."""
    reset_collection_cache()
    yield tmp_path / "chroma_db"
    reset_collection_cache()


@pytest.fixture
def tiny_kb(tmp_path: Path) -> Path:
    """A 3-doc synthetic KB so the index builds in milliseconds."""
    kb = tmp_path / "kb"
    kb.mkdir()
    (kb / "objection.md").write_text(
        "---\ntitle: objections\n---\n\n"
        "Acknowledge Reframe Redirect is the company-approved pattern for handling "
        "price objections on cold calls. Use it to validate, reframe to value, then "
        "redirect to a discovery question.",
        encoding="utf-8",
    )
    (kb / "ramp.md").write_text(
        "Entry-level SDRs ramp on a 25 / 60 / 100 percent quota schedule across "
        "months one through three. Ravi Anand owns the schedule.",
        encoding="utf-8",
    )
    (kb / "README.md").write_text("This README should be excluded from the index.", encoding="utf-8")
    return kb


def test_build_index_skips_readme(tmp_persist, tiny_kb):
    n = build_index(kb_dir=tiny_kb, persist_dir=tmp_persist)
    # 2 short docs, each fits in a single chunk → 2 chunks total.
    assert n == 2


def test_ensure_index_is_idempotent(tmp_persist, tiny_kb):
    first = ensure_index(kb_dir=tiny_kb, persist_dir=tmp_persist)
    second = ensure_index(kb_dir=tiny_kb, persist_dir=tmp_persist)
    assert first == second  # no re-indexing on the second call


def test_retrieve_matches_query_topic(tmp_persist, tiny_kb):
    build_index(kb_dir=tiny_kb, persist_dir=tmp_persist)
    results = retrieve("how do I handle price objections", top_k=2, persist_dir=tmp_persist)
    assert len(results) >= 1
    assert results[0].doc_name == "objection.md"
    assert "objection" in results[0].passage.lower() or "redirect" in results[0].passage.lower()
    # Cosine similarity should be in [0, 1] and the top hit should be reasonably high.
    assert 0.0 <= results[0].score <= 1.0
    assert results[0].score > 0.30


def test_retrieve_returns_low_score_for_off_topic_query(tmp_persist, tiny_kb):
    build_index(kb_dir=tiny_kb, persist_dir=tmp_persist)
    results = retrieve("xyzzy plumbus snargleflarbus quux", top_k=2, persist_dir=tmp_persist)
    # Off-topic gibberish should not score highly against the SDR-specific corpus.
    assert results[0].score < 0.40


def test_retrieve_on_empty_collection_returns_empty(tmp_persist):
    # Build no index, just query.
    results = retrieve("anything", top_k=3, persist_dir=tmp_persist)
    assert results == []


def test_add_approved_qa_increments_collection(tmp_persist, tiny_kb):
    build_index(kb_dir=tiny_kb, persist_dir=tmp_persist)
    before = collection_size(persist_dir=tmp_persist)
    qa_id = add_approved_qa(
        "How long is the entry-level ramp?",
        "Three months: 25%, 60%, 100% of quota.",
        persist_dir=tmp_persist,
    )
    after = collection_size(persist_dir=tmp_persist)
    assert after == before + 1
    assert qa_id.startswith("approved_qa::")


def test_approved_qa_is_retrievable(tmp_persist, tiny_kb):
    build_index(kb_dir=tiny_kb, persist_dir=tmp_persist)
    add_approved_qa(
        "What is the Salesforce code for the SDR onboarding policy?",
        "SDR-OB-2024-03, owned by Maya Reyes in People Ops.",
        persist_dir=tmp_persist,
    )
    results = retrieve("What policy code covers SDR onboarding?", top_k=3, persist_dir=tmp_persist)
    # The approved Q&A chunk should appear in the top results.
    doc_names = [r.doc_name for r in results]
    assert "approved_qa" in doc_names


def test_chunk_dataclass_fields():
    fields = {f for f in EmbedChunk.__dataclass_fields__}
    assert fields == {"doc_name", "chunk_id", "passage", "score"}


# ---------- build_sources (M04 Phase 2) ----------


def test_build_sources_shape():
    chunks = [
        EmbedChunk(doc_name="a.md", chunk_id="0", passage="strong evidence", score=0.85),
        EmbedChunk(doc_name="b.md", chunk_id="0", passage="weak evidence", score=0.20),
    ]
    sources = build_sources(chunks)
    assert len(sources) == 2
    for s in sources:
        assert set(s.keys()) == {"doc_name", "passage", "score", "weak"}


def test_build_sources_uses_calibrated_cosine_threshold():
    chunks = [
        EmbedChunk(doc_name="a.md", chunk_id="0", passage="strong", score=0.85),
        EmbedChunk(doc_name="b.md", chunk_id="0", passage="weak", score=0.20),
    ]
    sources = build_sources(chunks)
    # Cosine uses the absolute 0.40 threshold (unlike BM25's relative rule).
    assert sources[0]["weak"] is False
    assert sources[1]["weak"] is True
    # Sanity: the constant lives in the module and matches the rule.
    assert LOW_CONFIDENCE_THRESHOLD == 0.40


def test_build_sources_empty_returns_empty_list():
    assert build_sources([]) == []
