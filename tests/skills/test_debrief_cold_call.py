"""Tests for skills/debrief-cold-call (Cold Call Simulation rubric scorer)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "debrief-cold-call" / "scripts" / "debrief_cold_call.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("debrief_cold_call", SCRIPT)
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
                "rationale": "Clear opener and earned 30 more seconds against a skeptical CFO.",
            },
            "discovery_quality": {
                "score": d["discovery_quality"],
                "rationale": "Asked qualified questions and followed up on the budget answer.",
            },
            "objection_handling": {
                "score": d["objection_handling"],
                "rationale": "Used Acknowledge-Reframe-Redirect but missed a probe on procurement.",
            },
            "close_and_next_step": {
                "score": d["close_and_next_step"],
                "rationale": "Proposed a specific calendared next step with both attendees.",
            },
            "weighted_total": wt,
            "what_worked": [
                "Strong opener that earned more time",
                "Asked discovery before pitching features",
            ],
            "what_to_improve": [
                "Push harder on the budget objection",
            ],
            "language_alternatives": [
                'Replace "circle back" with "I\'ll send a 20-minute calendar invite for Thursday"',
                'Replace "touching base" with "following up on the patient-portal question"',
            ],
            "confidence": confidence,
        }
    )


def _write_messages(path: Path, *, turns: list[tuple[str, str]] | None = None) -> Path:
    turns = turns or [
        ("trainee", "Hi, this is Sam from Salesforce, do you have a minute?"),
        ("prospect", "Make it count — what specifically do you do?"),
        ("trainee", "We help finance teams cut close-of-books time by 30 percent."),
        ("prospect", "Send me a one-pager. I'll look when I have time."),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([{"role": r, "text": t} for r, t in turns]))
    return path


def _run(
    monkeypatch,
    *,
    out_dir: Path,
    run_id: str,
    persona_id: str | None = "cfo-saas",
    messages_file: Path | None = None,
) -> int:
    argv = [
        str(SCRIPT),
        "--workflow-run-id",
        run_id,
        "--step-id",
        "debrief-cold-call",
        "--data-dir",
        str(REPO_ROOT / "data"),
        "--out-dir",
        str(out_dir),
        "--json",
    ]
    if persona_id is not None:
        argv += ["--persona-id", persona_id]
    if messages_file is not None:
        argv += ["--messages-file", str(messages_file)]
    monkeypatch.setattr(sys, "argv", argv)
    return _load_script_module().main()


# ---------- 1. happy path ----------


def test_happy_path(tmp_path, capsys, monkeypatch):
    msgs = _write_messages(tmp_path / "msgs.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(confidence=0.85))
    rc = _run(monkeypatch, out_dir=tmp_path, run_id="dbg-h", messages_file=msgs)
    assert rc == 0
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "ok"
    assert env["next_action"] == "done"
    assert env["outputs"]["weighted_total"] == _weighted(_DEFAULT_DIM_SCORES)
    assert env["outputs"]["persona_id"] == "cfo-saas"
    assert env["outputs"]["persona_name"] == "Marcus Chen"
    assert env["outputs"]["n_turns"] == 4
    assert env["outputs"]["review_reasons"] == []
    assert (tmp_path / "dbg-h" / "01_simulation_debrief.md").exists()


# ---------- 2. low confidence flags review ----------


def test_low_confidence_flags_review(tmp_path, capsys, monkeypatch):
    msgs = _write_messages(tmp_path / "msgs.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(confidence=0.4))
    _run(monkeypatch, out_dir=tmp_path, run_id="dbg-low", messages_file=msgs)
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "needs_review"
    assert env["review_required"] is True
    assert any("confidence" in r for r in env["outputs"]["review_reasons"])


# ---------- 3. low weighted total flags review ----------


def test_low_weighted_total_flags_review(tmp_path, capsys, monkeypatch):
    msgs = _write_messages(tmp_path / "msgs.json")
    low_dims = {k: 3 for k in _WEIGHTS}
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(dims=low_dims, confidence=0.9))
    _run(monkeypatch, out_dir=tmp_path, run_id="dbg-bad", messages_file=msgs)
    env = json.loads(capsys.readouterr().out)
    assert env["review_required"] is True
    assert env["outputs"]["weighted_total"] == 3.0
    assert any("below 4" in r for r in env["outputs"]["review_reasons"])


# ---------- 4. missing messages file ----------


def test_missing_messages_returns_error(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    rc = _run(
        monkeypatch,
        out_dir=tmp_path,
        run_id="dbg-nf",
        messages_file=tmp_path / "does_not_exist.json",
    )
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "messages_file_missing"


# ---------- 5. empty conversation ----------


def test_empty_messages_returns_error(tmp_path, capsys, monkeypatch):
    empty = tmp_path / "empty.json"
    empty.write_text("[]")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    rc = _run(monkeypatch, out_dir=tmp_path, run_id="dbg-empty", messages_file=empty)
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "empty_conversation"


# ---------- 6. envelope has all 7 keys ----------


def test_envelope_has_all_seven_keys(tmp_path, capsys, monkeypatch):
    msgs = _write_messages(tmp_path / "msgs.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    _run(monkeypatch, out_dir=tmp_path, run_id="dbg-keys", messages_file=msgs)
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


# ---------- 7. markdown has expected sections ----------


def test_markdown_contains_expected_sections(tmp_path, capsys, monkeypatch):
    msgs = _write_messages(tmp_path / "msgs.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    _run(monkeypatch, out_dir=tmp_path, run_id="dbg-md", messages_file=msgs)
    capsys.readouterr()
    md = (tmp_path / "dbg-md" / "01_simulation_debrief.md").read_text()
    assert "# Cold Call Simulation debrief" in md
    assert "## Dimension scores" in md
    assert "Opening & framing (0.20)" in md
    assert "Discovery quality (0.35)" in md
    assert "Objection handling (0.25)" in md
    assert "Close & next step (0.20)" in md
    assert "## What worked" in md
    assert "## What to improve" in md
    assert "## Language alternatives" in md
