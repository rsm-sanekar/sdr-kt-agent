"""Tests for automations/welcome-new-hire (deterministic template, no LLM)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automations" / "welcome-new-hire" / "scripts" / "welcome_new_hire.py"
PROFILES_CSV = REPO_ROOT / "data" / "raw" / "sdr_profiles.csv"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("welcome_new_hire", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_trail_guides(run_dir: Path, ae_id: str = "AE-011", name: str = "Fiona MacLeod") -> None:
    """Drop a minimal 02_trail_guides.md so the skill can parse the top mentor."""
    run_dir.mkdir(parents=True, exist_ok=True)
    md = (
        "# Trail-guide ranking — test\n\n"
        "| Rank | AE ID | Name | Territory | Vertical | Total | Terr | Vert | Sat | Hrs | Mentees |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| 1 | {ae_id} | {name} | EMEA | healthcare | 92.8 | 30 | 30 | 18.8 | 6 | 8 |\n"
    )
    (run_dir / "02_trail_guides.md").write_text(md)


def _find_hire(level: str) -> tuple[str, str]:
    """Find the first hire at the given experience level. Returns (hire_id, name)."""
    profiles = pl.read_csv(PROFILES_CSV).filter(pl.col("experience_level") == level)
    assert not profiles.is_empty(), f"seed CSV must have at least one {level!r} hire"
    row = profiles.row(0, named=True)
    return row["hire_id"], row["name"]


def _run(
    monkeypatch,
    *,
    out_dir: Path,
    hire_id: str,
    run_id: str,
    step_id: str = "step3",
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
            "--json",
        ],
    )
    return _load_script_module().main()


# ---------- 1. happy path (entry-level hire) ----------


def test_happy_path_entry(tmp_path, capsys, monkeypatch):
    hire_id, hire_name = _find_hire("entry")
    first_name = hire_name.split()[0]
    _write_trail_guides(tmp_path / "wf-h")

    rc = _run(monkeypatch, out_dir=tmp_path, hire_id=hire_id, run_id="wf-h")
    assert rc == 0
    env = json.loads(capsys.readouterr().out)

    # Deterministic contract: full confidence, no review gate, terminal action.
    assert env["status"] == "ok"
    assert env["next_action"] == "done"
    assert env["confidence"] == 1.0
    assert env["review_required"] is False

    assert env["outputs"]["mentor_ae_id"] == "AE-011"
    assert env["outputs"]["mentor_name"] == "Fiona MacLeod"
    assert first_name in env["outputs"]["subject"]
    assert env["outputs"]["experience_level"] == "entry"

    email = (tmp_path / "wf-h" / "03_welcome_email.md").read_text()
    assert first_name in email
    assert "Fiona MacLeod" in email
    assert "AE-011" in email
    # entry-specific paragraph fingerprint
    assert "shadow at least 4 discovery calls" in email


# ---------- 2. mid-level hire gets the mid variant ----------


def test_mid_level_paragraph(tmp_path, capsys, monkeypatch):
    hire_id, _hire_name = _find_hire("mid")
    _write_trail_guides(tmp_path / "wf-mid")

    rc = _run(monkeypatch, out_dir=tmp_path, hire_id=hire_id, run_id="wf-mid")
    assert rc == 0
    capsys.readouterr()

    email = (tmp_path / "wf-mid" / "03_welcome_email.md").read_text()
    assert "peer SDRs" in email  # mid-specific
    assert "shadow at least 4 discovery calls" not in email  # not the entry block
    assert "perspective on the territory" not in email  # not the senior block


# ---------- 3. senior-level hire gets the senior variant ----------


def test_senior_level_paragraph(tmp_path, capsys, monkeypatch):
    hire_id, _hire_name = _find_hire("senior")
    _write_trail_guides(tmp_path / "wf-sr")

    rc = _run(monkeypatch, out_dir=tmp_path, hire_id=hire_id, run_id="wf-sr")
    assert rc == 0
    capsys.readouterr()

    email = (tmp_path / "wf-sr" / "03_welcome_email.md").read_text()
    assert "perspective on the territory" in email
    assert "shadow at least 4 discovery calls" not in email


# ---------- 4. missing mentor ranking ----------


def test_missing_mentor_ranking_returns_error(tmp_path, capsys, monkeypatch):
    hire_id, _ = _find_hire("entry")
    rc = _run(monkeypatch, out_dir=tmp_path, hire_id=hire_id, run_id="wf-missing")
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "mentor_ranking_not_found"
    assert "rank-trail-guides" in env["error"]["message"]


# ---------- 5. unknown hire ----------


def test_unknown_hire_returns_error(tmp_path, capsys, monkeypatch):
    rc = _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-999", run_id="wf-bad")
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "hire_not_found"


# ---------- 6. envelope has all 7 keys ----------


def test_envelope_has_all_seven_keys(tmp_path, capsys, monkeypatch):
    hire_id, _ = _find_hire("entry")
    _write_trail_guides(tmp_path / "wf-keys")
    _run(monkeypatch, out_dir=tmp_path, hire_id=hire_id, run_id="wf-keys")
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
