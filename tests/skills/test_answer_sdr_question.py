"""Tests for skills/answer-sdr-question (the AI Tutor).

The skill imports ``rag.embeddings_retrieval`` which would load ChromaDB and
download the sentence-transformer model on first use. To keep these tests
offline and fast, we monkeypatch ``ensure_index`` and ``retrieve`` to return
synthetic chunks.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "answer-sdr-question" / "scripts" / "answer_sdr_question.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("answer_sdr_question", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_GOOD_MOCK = json.dumps(
    {
        "answer": (
            "Use the Acknowledge-Reframe-Redirect (ARR) pattern from [1]. "
            "Validate the concern, reframe to value (clinician time saved), "
            "then redirect to a discovery question."
        ),
        "next_step": "Try the ARR pattern on your next 3 cold calls and review the recordings with your Trail Guide.",
        "confidence": 0.85,
    }
)


_LOW_LLM_CONF_MOCK = json.dumps(
    {
        "answer": "The sources are unclear on this. The closest match suggests [1] but the details don't line up.",
        "next_step": "Ask your Trail Guide or check the latest playbook update.",
        "confidence": 0.45,
    }
)


def _high_score_chunks(mod):
    """Two strong matches — best score 0.81, well above the 0.40 flag threshold."""
    return [
        mod.EmbedChunk(
            doc_name="objection_handling_top10.md",
            chunk_id="0",
            passage="Acknowledge-Reframe-Redirect is the company-approved pattern for price objections.",
            score=0.81,
        ),
        mod.EmbedChunk(
            doc_name="cold_call_quality_rubric.md",
            chunk_id="2",
            passage="Objection handling is scored on whether the rep used ARR.",
            score=0.62,
        ),
    ]


def _low_score_chunks(mod):
    """All matches weak — best score 0.18, below the 0.40 flag threshold."""
    return [
        mod.EmbedChunk(
            doc_name="compensation_overview.md",
            chunk_id="3",
            passage="FY2024 base bands by territory.",
            score=0.18,
        ),
    ]


def _run_with(monkeypatch, mod, *, question: str, out_dir: Path) -> int:
    """Set argv on the already-loaded ``mod`` and invoke its ``main()``.

    Loading the module once and calling main on that same instance is required
    so monkeypatches against ``mod.ensure_index`` / ``mod.retrieve`` take effect
    — a fresh ``importlib`` reload would lose the patches.
    """
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--question",
            question,
            "--data-dir",
            str(REPO_ROOT / "data"),
            "--out-dir",
            str(out_dir),
            "--json",
        ],
    )
    return mod.main()


def _install_retrieval_stubs(monkeypatch, mod, chunks):
    monkeypatch.setattr(mod, "ensure_index", lambda *a, **kw: len(chunks))
    monkeypatch.setattr(mod, "retrieve", lambda q, top_k=5, persist_dir=None: chunks)


# ---------- 1. happy path ----------


def test_happy_path(tmp_path, capsys, monkeypatch):
    mod = _load_script_module()
    _install_retrieval_stubs(monkeypatch, mod, _high_score_chunks(mod))
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _GOOD_MOCK)

    rc = _run_with(monkeypatch, mod, question="How do I handle a price objection on a cold call?", out_dir=tmp_path)
    assert rc == 0

    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "ok"
    assert env["next_action"] == "done"
    assert env["review_required"] is False
    assert env["outputs"]["question"].startswith("How do I handle")
    assert "Acknowledge-Reframe-Redirect" in env["outputs"]["answer"]
    assert "[1]" in env["outputs"]["answer"]
    assert len(env["outputs"]["sources"]) == 2
    first = env["outputs"]["sources"][0]
    assert set(first.keys()) == {"doc_name", "passage", "score", "weak"}
    assert first["doc_name"] == "objection_handling_top10.md"
    assert first["passage"]
    assert isinstance(first["score"], (int, float))
    # Cosine 0.81 is well above the 0.40 threshold, so this source is not weak.
    assert first["weak"] is False
    assert env["outputs"]["confidence_score"] == 0.81
    assert env["outputs"]["flagged"] is False


# ---------- 2. nonsense question flags review (low retrieval confidence) ----------


def test_nonsense_question_flags_review(tmp_path, capsys, monkeypatch):
    mod = _load_script_module()
    _install_retrieval_stubs(monkeypatch, mod, _low_score_chunks(mod))
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _GOOD_MOCK)

    rc = _run_with(monkeypatch, mod, question="xyzzy plumbus snargleflarbus quux", out_dir=tmp_path)
    assert rc == 0

    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "needs_review"
    assert env["review_required"] is True
    assert env["outputs"]["flagged"] is True
    assert env["outputs"]["confidence_score"] < 0.40
    # The single low-score source should be marked weak (cosine < 0.40).
    assert env["outputs"]["sources"][0]["weak"] is True


# ---------- 3. low LLM self-confidence flags review even when retrieval is good ----------


def test_low_llm_confidence_flags_review(tmp_path, capsys, monkeypatch):
    mod = _load_script_module()
    _install_retrieval_stubs(monkeypatch, mod, _high_score_chunks(mod))
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _LOW_LLM_CONF_MOCK)

    rc = _run_with(monkeypatch, mod, question="How does ARR work?", out_dir=tmp_path)
    assert rc == 0

    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "needs_review"
    assert env["review_required"] is True
    # Retrieval was strong, so flagged stays false; review_required comes from LLM confidence.
    assert env["outputs"]["flagged"] is False
    assert env["confidence"] == 0.45


# ---------- 4. empty question returns error ----------


def test_missing_question_returns_error(tmp_path, capsys, monkeypatch):
    mod = _load_script_module()
    rc = _run_with(monkeypatch, mod, question="", out_dir=tmp_path)
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "question_missing"


# ---------- 5. envelope has all seven keys + tutor outputs ----------


def test_envelope_has_all_seven_keys(tmp_path, capsys, monkeypatch):
    mod = _load_script_module()
    _install_retrieval_stubs(monkeypatch, mod, _high_score_chunks(mod))
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _GOOD_MOCK)

    _run_with(monkeypatch, mod, question="anything", out_dir=tmp_path)
    env = json.loads(capsys.readouterr().out)
    assert set(env.keys()) == {
        "status",
        "next_action",
        "confidence",
        "review_required",
        "artifact_refs",
        "outputs",
        "error",
    }
    # Tutor-specific outputs
    assert {"question", "answer", "next_step", "sources", "confidence_score", "flagged"} <= set(env["outputs"].keys())


# ---------- 6. no artifact files are written (artifact_refs is empty) ----------


def test_no_artifacts_written(tmp_path, capsys, monkeypatch):
    mod = _load_script_module()
    _install_retrieval_stubs(monkeypatch, mod, _high_score_chunks(mod))
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _GOOD_MOCK)

    _run_with(monkeypatch, mod, question="anything", out_dir=tmp_path)
    env = json.loads(capsys.readouterr().out)
    assert env["artifact_refs"] == []
