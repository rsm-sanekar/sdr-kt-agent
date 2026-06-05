"""Tests for skills/generate-onboarding-plan."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "generate-onboarding-plan" / "scripts" / "generate_onboarding_plan.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("generate_onboarding_plan", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _valid_mock(confidence: float = 0.88) -> str:
    return json.dumps(
        {
            "summary": (
                "Priya brings clinical-buyer fluency from Pfizer; compress HIPAA basics "
                "and lean into payer/provider personas in week 1."
            ),
            "weeks": [
                {
                    "week_number": 1,
                    "theme": "Salesforce + healthcare baseline",
                    "modules": [
                        {
                            "module_id": "TRAIL-CRM-101",
                            "title": "Salesforce CRM Basics",
                            "rationale": "New to Salesforce CRM after years on Veeva.",
                        },
                        {
                            "module_id": "TRAIL-VERT-HC-101",
                            "title": "HIPAA-Aware Selling",
                            "rationale": "Required even with pharma background per policy SDR-OB-2024-03.",
                        },
                    ],
                    "activities": ["Shadow 4 discovery calls"],
                }
            ],
            "skip_rationale": [],
            "confidence": confidence,
        }
    )


def _hallucinated_mock() -> str:
    return json.dumps(
        {
            "summary": "A plan that invents a fake module to test catalog validation.",
            "weeks": [
                {
                    "week_number": 1,
                    "theme": "Mostly real modules + one fake",
                    "modules": [
                        {
                            "module_id": "TRAIL-CRM-101",
                            "title": "Salesforce CRM Basics",
                            "rationale": "Required baseline.",
                        },
                        {
                            "module_id": "TRAIL-BOGUS-999",
                            "title": "Hallucinated Module",
                            "rationale": "This id is not in the catalog.",
                        },
                    ],
                    "activities": [],
                }
            ],
            "skip_rationale": [],
            "confidence": 0.9,
        }
    )


def _run(
    monkeypatch,
    *,
    out_dir: Path,
    hire_id: str,
    run_id: str,
    step_id: str = "step1",
    data_dir: Path | None = None,
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
        ],
    )
    return _load_script_module().main()


# ---------- 1. happy path with summary present ----------


def test_happy_path_with_summary(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _valid_mock(confidence=0.88))
    rc = _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-h")
    assert rc == 0
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "ok"
    assert env["next_action"] == "rank-trail-guides"
    assert env["confidence"] == 0.88
    assert env["review_required"] is False
    assert env["outputs"]["hire_id"] == "HIRE-001"
    assert env["outputs"]["summary_present"] is True
    assert env["outputs"]["invalid_modules"] == []
    assert isinstance(env["outputs"]["retrieved_docs"], list)
    assert len(env["outputs"]["retrieved_docs"]) > 0

    # M04 Phase 2: every chain skill exposes outputs.sources with passages + scores.
    sources = env["outputs"]["sources"]
    assert isinstance(sources, list)
    assert len(sources) > 0
    assert set(sources[0].keys()) == {"doc_name", "passage", "score", "weak"}
    assert isinstance(sources[0]["passage"], str) and sources[0]["passage"]
    assert isinstance(sources[0]["score"], (int, float))
    assert isinstance(sources[0]["weak"], bool)

    plan = (tmp_path / "wf-h" / "01_onboarding_plan.md").read_text()
    assert "Priya Patel" in plan
    assert "TRAIL-CRM-101" in plan


# ---------- 2. missing summary forces review ----------


def test_missing_summary_flags_review(tmp_path, capsys, monkeypatch):
    # Stage a fake data dir with the CSVs but NO summaries folder.
    data = tmp_path / "data"
    raw = data / "raw"
    raw.mkdir(parents=True)
    (raw / "sdr_profiles.csv").write_bytes((REPO_ROOT / "data" / "raw" / "sdr_profiles.csv").read_bytes())
    (raw / "ae_profiles.csv").write_bytes((REPO_ROOT / "data" / "raw" / "ae_profiles.csv").read_bytes())

    monkeypatch.setenv("MOCK_LLM_RESPONSE", _valid_mock(confidence=0.9))
    rc = _run(
        monkeypatch,
        out_dir=tmp_path / "out",
        hire_id="HIRE-001",
        run_id="wf-ns",
        data_dir=data,
    )
    assert rc == 0
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "needs_review"
    assert env["review_required"] is True
    assert env["outputs"]["summary_present"] is False


# ---------- 3. hallucinated module triggers review ----------


def test_invalid_module_flags_review(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _hallucinated_mock())
    rc = _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-bad-mod")
    assert rc == 0
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "needs_review"
    assert env["review_required"] is True
    assert "TRAIL-BOGUS-999" in env["outputs"]["invalid_modules"]


# ---------- 4. low confidence forces review ----------


def test_low_confidence_flags_review(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _valid_mock(confidence=0.4))
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-low")
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "needs_review"
    assert env["review_required"] is True
    assert env["confidence"] == 0.4


# ---------- 5. unknown hire returns error ----------


def test_unknown_hire_returns_error(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _valid_mock())
    rc = _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-999", run_id="wf-bad")
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "hire_not_found"


# ---------- 6. envelope has all seven keys ----------


def test_envelope_has_all_seven_keys(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _valid_mock())
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


# ---------- 7. catalog loader picks up real catalog ----------


def test_catalog_loader_has_expected_ids():
    mod = _load_script_module()
    catalog = mod._load_catalog()
    assert "TRAIL-CRM-101" in catalog
    assert "TRAIL-VERT-HC-101" in catalog
    assert catalog["TRAIL-CRM-101"] == "Salesforce CRM Basics"


# ---------- 8. markdown contains module rationale ----------


def test_markdown_contains_module_rationale(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _valid_mock())
    _run(monkeypatch, out_dir=tmp_path, hire_id="HIRE-001", run_id="wf-md")
    capsys.readouterr()
    md = (tmp_path / "wf-md" / "01_onboarding_plan.md").read_text()
    assert "Why for this hire" in md
    assert "TRAIL-CRM-101" in md
    assert "Shadow 4 discovery calls" in md
