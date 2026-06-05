"""Tests for skills/score-certification (5-dimension SDR certification gap analysis).

Two layers:
- Unit tests on the `compute_overall` band logic (server-side source of truth)
- Happy-path + error tests that exercise `do_work` end-to-end via the seeded
  synthetic cohort under `data/sdr_records/`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "score-certification" / "scripts" / "score_certification.py"
SDR_RECORDS_DIR = REPO_ROOT / "data" / "sdr_records"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("score_certification", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def _preserve_cohort_gap_analyses():
    """The cert skill caches its result to data/sdr_records/<id>/gap_analysis.json.
    These tests intentionally run it against the real data dir with placeholder
    mocks, which would clobber the demo cohort's real (seeded) gap analyses.
    Snapshot every gap_analysis.json before the test and restore it after, so
    running the suite never degrades the seeded demo data."""
    snapshots = {p: p.read_bytes() for p in SDR_RECORDS_DIR.glob("*/gap_analysis.json")}
    try:
        yield
    finally:
        for path, content in snapshots.items():
            path.write_bytes(content)


# ---------------------------------------------------------------------------
# 1. Band logic — server-side source of truth
# ---------------------------------------------------------------------------


def test_compute_overall_all_pass():
    mod = _load_script_module()
    assert mod.compute_overall([7, 7, 7, 7, 7]) == "PASS"
    assert mod.compute_overall([10, 10, 10, 10, 10]) == "PASS"
    assert mod.compute_overall([8, 9, 7, 9, 8]) == "PASS"


def test_compute_overall_borderline_on_single_five_or_six():
    mod = _load_script_module()
    assert mod.compute_overall([7, 5, 7, 7, 7]) == "BORDERLINE"
    assert mod.compute_overall([7, 7, 6, 7, 7]) == "BORDERLINE"
    assert mod.compute_overall([6, 7, 7, 7, 7]) == "BORDERLINE"


def test_compute_overall_fail_on_any_four_or_below():
    mod = _load_script_module()
    assert mod.compute_overall([7, 7, 4, 7, 7]) == "FAIL"
    assert mod.compute_overall([3, 7, 7, 7, 7]) == "FAIL"
    assert mod.compute_overall([1, 1, 1, 1, 1]) == "FAIL"
    # Even a single sub-5 wins over otherwise-passing scores
    assert mod.compute_overall([10, 10, 4, 10, 10]) == "FAIL"


def test_verdict_for_band_logic():
    mod = _load_script_module()
    assert mod.verdict_for(10) == "pass"
    assert mod.verdict_for(7) == "pass"
    assert mod.verdict_for(6) == "borderline"
    assert mod.verdict_for(5) == "borderline"
    assert mod.verdict_for(4) == "fail"
    assert mod.verdict_for(1) == "fail"


# ---------------------------------------------------------------------------
# 2. Happy-path scoring with MOCK_LLM_RESPONSE — exercises seeded SDR records
# ---------------------------------------------------------------------------


def _mock_analysis(scores: list[int], *, overall: str = "PASS", confidence: float = 0.85) -> str:
    """Build a valid CertificationGapAnalysis JSON payload for mocking."""
    dim_names = [
        "product_knowledge_accuracy",
        "objection_handling",
        "meddic_application",
        "salesforce_value_messaging",
        "discovery_and_questioning",
    ]
    payload = {}
    for dim, score in zip(dim_names, scores):
        verdict = "pass" if score >= 7 else "borderline" if score >= 5 else "fail"
        payload[dim] = {
            "score": score,
            "evidence_quote": f"Sample evidence quote for {dim} from the candidate's answer.",
            "rationale": f"Rationale grounded in the rubric for {dim}.",
            "gap_to_close": f"Specific gap on {dim} that needs addressing.",
            "coaching_action": f"Targeted coaching action for {dim}.",
            "verdict": verdict,
        }
    payload["overall_recommendation"] = overall
    payload["overall_rationale"] = (
        "Synthetic gap analysis used in test fixtures — narrative of at least twenty characters."
    )
    payload["confidence"] = confidence
    return json.dumps(payload)


def _run(monkeypatch, *, sdr_id: str, out_dir: Path, run_id: str) -> int:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--sdr-id",
            sdr_id,
            "--data-dir",
            str(REPO_ROOT / "data"),
            "--out-dir",
            str(out_dir),
            "--workflow-run-id",
            run_id,
            "--step-id",
            "score-certification",
            "--idempotency-mode",
            "replace",
            "--json",
        ],
    )
    return _load_script_module().main()


def test_happy_path_pass(tmp_path, capsys, monkeypatch):
    """All dims >= 7 → PASS, status=ok, no review reasons, cache written."""
    monkeypatch.setenv(
        "MOCK_LLM_RESPONSE",
        _mock_analysis([8, 8, 9, 9, 8], overall="PASS", confidence=0.9),
    )
    rc = _run(monkeypatch, sdr_id="SDR-002", out_dir=tmp_path, run_id="cert-test-pass")
    assert rc == 0
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "ok"
    assert env["next_action"] == "done"
    assert env["review_required"] is False
    assert env["outputs"]["overall_recommendation"] == "PASS"
    assert env["outputs"]["sdr_id"] == "SDR-002"
    assert env["outputs"]["weakest_dimension"] in (
        "product_knowledge_accuracy",
        "objection_handling",
        "discovery_and_questioning",
    )
    # Markdown artifact rendered
    assert (tmp_path / "cert-test-pass" / "01_certification_gap_analysis.md").exists()
    # Cache file written next to the SDR record
    cache = REPO_ROOT / "data" / "sdr_records" / "SDR-002" / "gap_analysis.json"
    assert cache.exists()


def test_borderline_triggers_review(tmp_path, capsys, monkeypatch):
    """Any dim in 5-6 → BORDERLINE → review_required=True."""
    monkeypatch.setenv(
        "MOCK_LLM_RESPONSE",
        _mock_analysis([7, 5, 7, 7, 7], overall="BORDERLINE", confidence=0.8),
    )
    _run(monkeypatch, sdr_id="SDR-001", out_dir=tmp_path, run_id="cert-test-bord")
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "needs_review"
    assert env["review_required"] is True
    assert env["outputs"]["overall_recommendation"] == "BORDERLINE"
    assert any("BORDERLINE" in r for r in env["outputs"]["review_reasons"])


def test_fail_triggers_review(tmp_path, capsys, monkeypatch):
    """Any dim <= 4 → FAIL → review_required=True."""
    monkeypatch.setenv(
        "MOCK_LLM_RESPONSE",
        _mock_analysis([2, 3, 2, 3, 3], overall="FAIL", confidence=0.92),
    )
    _run(monkeypatch, sdr_id="SDR-003", out_dir=tmp_path, run_id="cert-test-fail")
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "needs_review"
    assert env["review_required"] is True
    assert env["outputs"]["overall_recommendation"] == "FAIL"
    assert env["outputs"]["weakest_dimension"] in (
        "product_knowledge_accuracy",
        "meddic_application",
    )


def test_llm_overall_mismatch_flagged(tmp_path, capsys, monkeypatch):
    """LLM reports PASS but scores include a 4 → server forces FAIL + drift reason."""
    monkeypatch.setenv(
        "MOCK_LLM_RESPONSE",
        _mock_analysis([7, 7, 4, 7, 7], overall="PASS", confidence=0.9),
    )
    _run(monkeypatch, sdr_id="SDR-004", out_dir=tmp_path, run_id="cert-test-drift")
    env = json.loads(capsys.readouterr().out)
    assert env["outputs"]["overall_recommendation"] == "FAIL"
    assert env["outputs"]["llm_overall_recommendation"] == "PASS"
    assert any("differs from" in r for r in env["outputs"]["review_reasons"])


def test_low_confidence_flags_review(tmp_path, capsys, monkeypatch):
    """Confidence below 0.65 always triggers review."""
    monkeypatch.setenv(
        "MOCK_LLM_RESPONSE",
        _mock_analysis([8, 8, 8, 8, 8], overall="PASS", confidence=0.40),
    )
    _run(monkeypatch, sdr_id="SDR-005", out_dir=tmp_path, run_id="cert-test-lowconf")
    env = json.loads(capsys.readouterr().out)
    assert env["review_required"] is True
    assert any("confidence" in r for r in env["outputs"]["review_reasons"])


# ---------------------------------------------------------------------------
# 3. Error paths
# ---------------------------------------------------------------------------


def test_unknown_sdr_returns_error(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock_analysis([8, 8, 8, 8, 8]))
    rc = _run(monkeypatch, sdr_id="SDR-XXXX", out_dir=tmp_path, run_id="cert-test-missing")
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "sdr_not_found"


def test_envelope_has_all_seven_keys(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock_analysis([8, 8, 8, 8, 8]))
    _run(monkeypatch, sdr_id="SDR-006", out_dir=tmp_path, run_id="cert-test-keys")
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
