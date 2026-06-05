"""Tests for automations/rank-trail-guides."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automations" / "rank-trail-guides" / "scripts" / "rank_trail_guides.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("rank_trail_guides", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_data_dir(tmp_path: Path, ae_csv: str | None = None) -> Path:
    """Build a fake data/ tree under tmp_path; optionally override ae_profiles.csv."""
    data = tmp_path / "data"
    raw = data / "raw"
    raw.mkdir(parents=True)
    shutil.copy(REPO_ROOT / "data" / "raw" / "sdr_profiles.csv", raw / "sdr_profiles.csv")
    if ae_csv is None:
        shutil.copy(REPO_ROOT / "data" / "raw" / "ae_profiles.csv", raw / "ae_profiles.csv")
    else:
        (raw / "ae_profiles.csv").write_text(ae_csv)
    return data


def _run(
    monkeypatch,
    *,
    out_dir: Path,
    hire_id: str,
    run_id: str,
    step_id: str,
    data_dir: Path | None = None,
    top_n: int | None = None,
    idempotency: str = "skip",
) -> int:
    argv = [
        str(SCRIPT),
        "--hire-id",
        hire_id,
        "--data-dir",
        str(data_dir or (REPO_ROOT / "data")),
        "--out-dir",
        str(out_dir),
        "--workflow-run-id",
        run_id,
        "--step-id",
        step_id,
        "--idempotency-mode",
        idempotency,
        "--json",
    ]
    if top_n is not None:
        argv.extend(["--top-n", str(top_n)])
    monkeypatch.setattr(sys, "argv", argv)
    return _load_script_module().main()


def _count_table_rows(md: str) -> int:
    # Markdown rows that start with "| 1 |", "| 2 |", etc.
    return len(re.findall(r"^\| \d+ \|", md, flags=re.MULTILINE))


def _extract_scores(md: str) -> list[float]:
    """Pull the total_score column (column 6) from each ranked row."""
    scores = []
    for line in md.splitlines():
        m = re.match(r"^\| (\d+) \|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        scores.append(float(cells[5]))
    return scores


# ---------- happy path ----------


def test_happy_path(tmp_path, capsys, monkeypatch):
    rc = _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-h", step_id="step2")
    assert rc == 0
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "ok"
    assert env["next_action"] == "welcome-new-hire"
    assert env["outputs"]["hire_id"] == "HIRE-001"

    plan = tmp_path / "wf-h" / "02_trail_guides.md"
    assert plan.exists() and plan.stat().st_size > 0


# ---------- top-N respected ----------


def test_top_n_three_rows(tmp_path, capsys, monkeypatch):
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-n3", step_id="step2", top_n=3)
    capsys.readouterr()
    md = (tmp_path / "wf-n3" / "02_trail_guides.md").read_text()
    assert _count_table_rows(md) == 3


# ---------- score ordering ----------


def test_scores_descending(tmp_path, capsys, monkeypatch):
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-ord", step_id="step2", top_n=5)
    env = json.loads(capsys.readouterr().out)
    md = (tmp_path / "wf-ord" / "02_trail_guides.md").read_text()
    scores = _extract_scores(md)
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == env["outputs"]["top_score"]


# ---------- perfect match ----------


def test_perfect_match_near_100(tmp_path, capsys, monkeypatch):
    # HIRE-001 = EMEA / healthcare
    ae_csv = (
        "ae_id,name,territory,vertical,tenure_years,satisfaction_score,"
        "mentorship_hours_per_week,prior_mentees\n"
        "AE-PERF,Perfect Match,EMEA,healthcare,10,4.8,5,12\n"
    )
    data = _make_data_dir(tmp_path, ae_csv=ae_csv)
    _run(monkeypatch, out_dir=tmp_path / "out", hire_id="HIRE-001", run_id="wf-perf", step_id="step2", data_dir=data)
    env = json.loads(capsys.readouterr().out)
    assert env["outputs"]["top_ae_id"] == "AE-PERF"
    # 30 + 30 + (4.8/5)*20 + (5/5)*10 + min(12/10,1)*10 = 30+30+19.2+10+10 = 99.2
    assert env["outputs"]["top_score"] == pytest.approx(99.2, abs=0.01)
    assert env["status"] == "ok"


# ---------- no-match scenario ----------


def test_no_match_flags_review(tmp_path, capsys, monkeypatch):
    # HIRE-001 is EMEA / healthcare; build a catalog with neither.
    ae_csv = (
        "ae_id,name,territory,vertical,tenure_years,satisfaction_score,"
        "mentorship_hours_per_week,prior_mentees\n"
        "AE-X1,Nope One,AMER-West,fintech,5,4.0,2,3\n"
        "AE-X2,Nope Two,APAC,SaaS,6,4.2,3,4\n"
        "AE-X3,Nope Three,AMER-East,retail,4,3.8,1,2\n"
    )
    data = _make_data_dir(tmp_path, ae_csv=ae_csv)
    _run(monkeypatch, out_dir=tmp_path / "out", hire_id="HIRE-001", run_id="wf-no", step_id="step2", data_dir=data)
    env = json.loads(capsys.readouterr().out)
    # Best case here: 0 + 0 + (4.2/5)*20 + (3/5)*10 + (4/10)*10 = 16.8+6+4 = 26.8
    assert env["outputs"]["top_score"] < 60
    assert env["status"] == "needs_review"
    assert env["review_required"] is True


# ---------- unknown hire ----------


def test_unknown_hire_returns_error(tmp_path, capsys, monkeypatch):
    rc = _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-999", run_id="wf-bad", step_id="step2")
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "hire_not_found"


# ---------- idempotency ----------


def test_idempotency_skip_returns_cached(tmp_path, capsys, monkeypatch):
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-idem", step_id="step2")
    first = json.loads(capsys.readouterr().out)

    script = _load_script_module()

    def _boom(_args):
        raise RuntimeError("do_work should not have been called on cached run")

    monkeypatch.setattr(script, "do_work", _boom)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--hire-id",
            "HIRE-001",
            "--data-dir",
            str(REPO_ROOT / "data"),
            "--out-dir",
            str(tmp_path),
            "--workflow-run-id",
            "wf-idem",
            "--step-id",
            "step2",
            "--idempotency-mode",
            "skip",
            "--json",
        ],
    )
    rc = script.main()
    second = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert second == first
