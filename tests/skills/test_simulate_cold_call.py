"""Tests for skills/simulate-cold-call (Cold Call Simulation turn-driver)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "simulate-cold-call" / "scripts" / "simulate_cold_call.py"
PERSONAS_PATH = REPO_ROOT / "data" / "raw" / "sim_personas.json"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("simulate_cold_call", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_messages(path: Path, *, turns: list[tuple[str, str]] | None = None) -> Path:
    turns = turns or [
        ("trainee", "Hi, this is Sam from Salesforce. Do you have two minutes?"),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([{"role": r, "text": t} for r, t in turns]))
    return path


def _mock(
    *,
    response: str = "Two minutes? Make it count — what specifically do you do, and why are you on my line right now?",
    objection: str | None = "Send me a one-pager; I'll look at it when I have time.",
    confidence: float = 0.9,
) -> str:
    return json.dumps(
        {
            "prospect_response": response,
            "suggested_objection_used": objection,
            "confidence": confidence,
        }
    )


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
        "simulate-cold-call",
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
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(confidence=0.92))
    rc = _run(monkeypatch, out_dir=tmp_path, run_id="sim-h", messages_file=msgs)
    assert rc == 0
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "ok"
    assert env["next_action"] == "done"
    assert env["confidence"] == 0.92
    assert env["review_required"] is False
    assert env["outputs"]["persona_id"] == "cfo-saas"
    assert env["outputs"]["persona_name"] == "Gregory Hale"
    assert "two minutes" in env["outputs"]["prospect_response"].lower()
    assert env["outputs"]["n_messages_in"] == 1
    # Simulation skill does not write artifacts.
    assert env["artifact_refs"] == []


# ---------- 2. unknown persona ----------


def test_unknown_persona_returns_error(tmp_path, capsys, monkeypatch):
    msgs = _write_messages(tmp_path / "msgs.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    rc = _run(monkeypatch, out_dir=tmp_path, run_id="sim-bad", persona_id="not-a-real-persona", messages_file=msgs)
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "persona_not_found"


# ---------- 3. missing messages file ----------


def test_missing_messages_file_returns_error(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    rc = _run(
        monkeypatch,
        out_dir=tmp_path,
        run_id="sim-nf",
        messages_file=tmp_path / "does_not_exist.json",
    )
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "messages_file_missing"


# ---------- 4. malformed messages file ----------


def test_invalid_messages_returns_error(tmp_path, capsys, monkeypatch):
    bad = tmp_path / "bad.json"
    bad.write_text('{"not": "a list"}')
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    rc = _run(monkeypatch, out_dir=tmp_path, run_id="sim-mal", messages_file=bad)
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "messages_file_invalid"


# ---------- 5. envelope has all 7 keys ----------


def test_envelope_has_all_seven_keys(tmp_path, capsys, monkeypatch):
    msgs = _write_messages(tmp_path / "msgs.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    _run(monkeypatch, out_dir=tmp_path, run_id="sim-keys", messages_file=msgs)
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


# ---------- 6. persona file has the 5 expected ids ----------


def test_personas_file_has_expected_ids():
    personas = json.loads(PERSONAS_PATH.read_text(encoding="utf-8"))
    ids = {p["id"] for p in personas}
    expected = {
        "cfo-saas",
        "clinical-buyer-hc",
        "it-director-fintech",
        "vp-ops-retail",
        "gatekeeper-receptionist",
    }
    assert expected.issubset(ids)
