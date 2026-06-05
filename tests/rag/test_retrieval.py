"""Tests for rag/retrieval.py — the BM25 keyword retriever."""

from __future__ import annotations

from dataclasses import fields

import pytest

from rag.retrieval import Chunk, build_index, build_sources, retrieve


@pytest.fixture(scope="module")
def index():
    return build_index()


def test_build_index_finds_all_core_documents(index):
    """The curated KB docs at the top level are all indexed, regardless of
    how many scraped docs (in ``scraped/`` subdir) are present. The minimum
    bar is the 14 original M03 docs plus the M04 certification additions
    (certification_rubric.md, certification_questions.md)."""
    docs = {c.doc_name for c in index.chunks}
    core_docs = {d for d in docs if "/" not in d}
    assert "README.md" not in docs
    assert len(core_docs) >= 14, f"expected at least 14 core KB docs, got {len(core_docs)}: {core_docs}"
    # The two M03 additions must be indexed (allow-list + gold-standard exemplar).
    assert "trailhead_module_catalog.md" in docs
    assert "gold_plan_healthcare_entry.md" in docs
    # M04 certification additions must also be present.
    assert "certification_rubric.md" in docs
    assert "certification_questions.md" in docs


def test_each_document_has_multiple_chunks(index):
    counts: dict[str, int] = {}
    for c in index.chunks:
        counts[c.doc_name] = counts.get(c.doc_name, 0) + 1
    for doc, n in counts.items():
        assert n >= 2, f"{doc} only produced {n} chunk(s); expected ≥2"


def test_retrieve_quota_ramp_top_result(index):
    results = retrieve("quota ramp schedule", index, top_k=3)
    assert len(results) == 3
    assert results[0].doc_name == "quota_ramp_schedule.md"


def test_retrieve_hipaa_returns_healthcare(index):
    results = retrieve("HIPAA compliance", index, top_k=3)
    doc_names = [r.doc_name for r in results]
    assert "vertical_playbook_healthcare.md" in doc_names


def test_retrieve_nonsense_query_still_returns_top_k(index):
    results = retrieve("nonexistent random query xyzzy", index, top_k=3)
    assert len(results) == 3


def test_chunk_has_four_fields():
    field_names = {f.name for f in fields(Chunk)}
    assert field_names == {"doc_name", "chunk_id", "text", "score"}


def test_retrieve_respects_top_k(index):
    assert len(retrieve("ramp", index, top_k=1)) == 1
    assert len(retrieve("ramp", index, top_k=5)) == 5


def test_retrieve_is_deterministic(index):
    a = retrieve("HIPAA compliance", index, top_k=3)
    b = retrieve("HIPAA compliance", index, top_k=3)
    assert [(r.doc_name, r.chunk_id, r.score) for r in a] == [
        (r.doc_name, r.chunk_id, r.score) for r in b
    ]


# ---------- build_sources (M04 Phase 2 — envelope-output serializer) ----------


def test_build_sources_shape(index):
    chunks = retrieve("HIPAA compliance", index, top_k=3)
    sources = build_sources(chunks)
    assert len(sources) == 3
    for s in sources:
        assert set(s.keys()) == {"doc_name", "passage", "score", "weak"}
        assert isinstance(s["passage"], str) and s["passage"]
        assert isinstance(s["score"], (int, float))
        assert isinstance(s["weak"], bool)


def test_build_sources_empty_returns_empty_list():
    assert build_sources([]) == []


def test_build_sources_weak_flag_is_relative_to_top():
    """BM25 scores are unbounded; 'weak' is defined as <30% of the top score."""
    chunks = [
        Chunk(doc_name="a.md", chunk_id=0, text="strong match", score=10.0),
        Chunk(doc_name="b.md", chunk_id=0, text="medium match", score=4.0),
        Chunk(doc_name="c.md", chunk_id=0, text="weak match", score=1.0),
    ]
    sources = build_sources(chunks)
    # Top: 10.0 → weak threshold 3.0. 10.0 and 4.0 pass; 1.0 is weak.
    assert sources[0]["weak"] is False
    assert sources[1]["weak"] is False
    assert sources[2]["weak"] is True


def test_build_sources_weak_disabled_when_ratio_none():
    chunks = [Chunk(doc_name="a.md", chunk_id=0, text="x", score=0.001)]
    assert build_sources(chunks, weak_ratio=None)[0]["weak"] is False
