"""Tests for skills/score-cold-call (Coaching Rubric v3.1, four-dimension shape)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "score-cold-call" / "scripts" / "score_cold_call.py"
DEFAULT_TRANSCRIPT = REPO_ROOT / "tests" / "skills" / "fixtures" / "sample_transcript.json"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("score_cold_call", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_WEIGHTS = {
    "opening_and_framing": 0.20,
    "discovery_quality": 0.35,
    "objection_handling": 0.25,
    "close_and_next_step": 0.20,
}

_DEFAULT_DIM_SCORES = {
    "opening_and_framing": 7,
    "discovery_quality": 8,
    "objection_handling": 6,
    "close_and_next_step": 7,
}


def _weighted(dims: dict[str, int]) -> float:
    return round(sum(dims[k] * w for k, w in _WEIGHTS.items()), 2)


def _mock(
    *,
    dims: dict[str, int] | None = None,
    weighted_total: float | None = None,
    confidence: float = 0.85,
) -> str:
    d = dims if dims is not None else _DEFAULT_DIM_SCORES
    wt = weighted_total if weighted_total is not None else _weighted(d)
    return json.dumps(
        {
            "opening_and_framing": {
                "score": d["opening_and_framing"],
                "rationale": "Clear opener and earned 30 more seconds.",
            },
            "discovery_quality": {
                "score": d["discovery_quality"],
                "rationale": "Asked qualified questions and followed up on answers.",
            },
            "objection_handling": {
                "score": d["objection_handling"],
                "rationale": "Used Acknowledge-Reframe-Redirect but missed a deeper probe.",
            },
            "close_and_next_step": {
                "score": d["close_and_next_step"],
                "rationale": "Specific calendared next step with both attendees.",
            },
            "weighted_total": wt,
            "what_worked": [
                "Clear opener and value proposition",
                "Asked discovery question early",
            ],
            "what_to_improve": [
                "Could handle the budget objection more confidently",
            ],
            "language_alternatives": [
                'Replace "just checking in" with "following up on our last conversation"',
                'Replace "I think" with "based on what you shared"',
            ],
            "confidence": confidence,
        }
    )


def _write_transcript(path: Path, *, hire_id: str = "HIRE-001", outcome: str = "meeting_booked") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "hire_id": hire_id,
                "messages": [
                    {"role": "sdr", "text": "Hi, this is a test opener."},
                    {"role": "prospect", "text": "Not interested right now."},
                    {"role": "sdr", "text": "Totally fair — quick clarifying question..."},
                    {"role": "prospect", "text": "Send me a time next week."},
                ],
                "outcome": outcome,
            }
        )
    )
    return path


def _run(
    monkeypatch,
    *,
    out_dir: Path,
    hire_id: str,
    run_id: str,
    step_id: str = "step4",
    transcript_file: Path | str | None = None,
    idempotency: str = "skip",
) -> int:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--hire-id",
            hire_id,
            "--data-dir",
            str(REPO_ROOT / "data"),
            "--out-dir",
            str(out_dir),
            "--workflow-run-id",
            run_id,
            "--step-id",
            step_id,
            "--idempotency-mode",
            idempotency,
            "--transcript-file",
            str(transcript_file or DEFAULT_TRANSCRIPT),
            "--json",
        ],
    )
    return _load_script_module().main()


# ---------- 1. happy path ----------


def test_happy_path(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(confidence=0.85))
    rc = _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-h")
    assert rc == 0
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "ok"
    assert env["next_action"] == "done"
    expected_total = _weighted(_DEFAULT_DIM_SCORES)
    assert env["outputs"]["weighted_total"] == expected_total
    assert env["outputs"]["outcome"] == "meeting_booked"
    assert env["outputs"]["dimension_scores"]["opening_and_framing"]["score"] == 7
    assert env["outputs"]["dimension_scores"]["discovery_quality"]["weight"] == 0.35
    assert env["outputs"]["review_reasons"] == []
    assert env["review_required"] is False
    assert isinstance(env["outputs"]["retrieved_docs"], list)
    assert len(env["outputs"]["retrieved_docs"]) > 0

    sources = env["outputs"]["sources"]
    assert isinstance(sources, list) and len(sources) > 0
    assert set(sources[0].keys()) == {"doc_name", "passage", "score", "weak"}

    assert (tmp_path / "wf-h" / "04_coaching_note.md").exists()


# ---------- 2. low confidence ----------


def test_low_confidence_flags_review(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(confidence=0.4))
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-low")
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "needs_review"
    assert env["review_required"] is True
    assert env["confidence"] == 0.4
    assert any("confidence" in r for r in env["outputs"]["review_reasons"])


# ---------- 3. low weighted total still flags review with high confidence ----------


def test_low_weighted_total_still_flags_review(tmp_path, capsys, monkeypatch):
    low_dims = {k: 3 for k in _WEIGHTS}  # weighted total = 3.0
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(dims=low_dims, confidence=0.9))
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-bad-call")
    env = json.loads(capsys.readouterr().out)
    assert env["review_required"] is True
    assert env["status"] == "needs_review"
    assert env["confidence"] == 0.9
    assert env["outputs"]["weighted_total"] == 3.0
    assert any("below 4" in r for r in env["outputs"]["review_reasons"])


# ---------- 4. one dimension below 3 flags review ----------


def test_low_single_dimension_flags_review(tmp_path, capsys, monkeypatch):
    dims = {
        "opening_and_framing": 8,
        "discovery_quality": 8,
        "objection_handling": 2,
        "close_and_next_step": 8,
    }
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(dims=dims, confidence=0.9))
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-dim")
    env = json.loads(capsys.readouterr().out)
    assert env["review_required"] is True
    assert any("dimension" in r.lower() for r in env["outputs"]["review_reasons"])


# ---------- 5. weighted_total drift flags review ----------


def test_drift_flags_review(tmp_path, capsys, monkeypatch):
    # Sub-scores compute to a weighted total around 7.05, but the LLM claims 10.
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(weighted_total=10.0, confidence=0.9))
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-drift")
    env = json.loads(capsys.readouterr().out)
    assert env["review_required"] is True
    assert any("drift" in r.lower() for r in env["outputs"]["review_reasons"])


# ---------- 6. missing transcript ----------


def test_missing_transcript_returns_error(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    rc = _run(
        monkeypatch,
        out_dir=tmp_path,
        hire_id="HIRE-001",
        run_id="wf-nt",
        transcript_file=tmp_path / "does_not_exist.json",
    )
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "transcript_not_found"


# ---------- 7. unknown hire ----------


def test_unknown_hire_returns_error(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    rc = _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-999", run_id="wf-bad")
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "hire_not_found"


# ---------- 8. markdown sections ----------


def test_markdown_contains_all_sections(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    transcript = _write_transcript(tmp_path / "tx.json")
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-md", transcript_file=transcript)
    capsys.readouterr()
    md = (tmp_path / "wf-md" / "04_coaching_note.md").read_text()
    assert "Overall score (weighted)" in md
    assert "## Dimension scores" in md
    assert "Opening & framing (0.20)" in md
    assert "Discovery quality (0.35)" in md
    assert "Objection handling (0.25)" in md
    assert "Close & next step (0.20)" in md
    assert "## What worked" in md
    assert "## What to improve" in md
    assert "## Language alternatives" in md


# ---------- 9. envelope has all 7 keys ----------


def test_envelope_has_all_seven_keys(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-keys")
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
