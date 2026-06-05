"""Tests for skills/generate-handoff-doc (post-certification onboarding debrief)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "generate-handoff-doc" / "scripts" / "generate_handoff_doc.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("generate_handoff_doc", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_INTERVIEW_QA = [
    (1, "Most valuable onboarding content?", "The SaaS pricing module and advanced prospecting; entry CRM basics were too basic."),
    (2, "How did the AI Tutor help?", "Fast on objection handling, thin on multi-threading enterprise deals."),
    (3, "Did the cold-call sim match real prospects?", "Mostly — the skeptical CFO persona was realistic."),
    (4, "A piece of coaching that landed?", "Slow down on discovery before pitching — changed my call open."),
    (5, "Biggest barrier to ramp?", "Incomplete territory data meant my plan started generic and I lost a week."),
    (6, "Territory/vertical surprises?", "SaaS procurement cycles were longer than the playbook implied."),
    (7, "One thing to change?", "Auto-pull territory and account data so the plan is specific on day one."),
]


def _interview(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    qa_pairs = [
        {"question_id": qid, "question": q, "answer": a} for qid, q, a in _INTERVIEW_QA
    ]
    path.write_text(
        json.dumps(
            {
                "rep_info": {
                    "name": "Devon Park",
                    "territory": "AMER-West",
                    "vertical": "SaaS",
                },
                "qa_pairs": qa_pairs,
            }
        )
    )
    return path


def _mock(*, confidence: float = 0.85, n_elements: int = 3) -> str:
    elements = []
    for i in range(n_elements):
        elements.append(
            {
                "element": f"Onboarding element {i + 1}",
                "what_worked": "Front-loaded the right content and matched the SDR's prior experience well.",
                "what_to_improve": "Add an earlier, territory-specific module so the plan is concrete on day one.",
            }
        )
    return json.dumps(
        {
            "summary": (
                "Devon ramped well in AMER-West SaaS; the plan front-loaded the right "
                "pricing and prospecting content, while incomplete territory data was the "
                "main early barrier. The AI Tutor and coaching closed most gaps."
            ),
            "elements": elements,
            "ramp_barriers": [
                "Incomplete territory data caused a generic plan in week one.",
                "Entry-level CRM content was mismatched to prior experience.",
            ],
            "program_strengths": [
                "Personalized onboarding plan.",
                "Rubric-based coaching that changed call behavior.",
            ],
            "suggested_improvements": [
                "Auto-pull territory and account data before day one.",
                "Add a skills pre-assessment to place SDRs at the right module level.",
            ],
            "confidence": confidence,
        }
    )


def _run(
    monkeypatch,
    *,
    out_dir: Path,
    run_id: str,
    interview_file: Path | None = None,
    idempotency: str = "skip",
) -> int:
    argv = [
        str(SCRIPT),
        "--workflow-run-id",
        run_id,
        "--step-id",
        "generate-handoff-doc",
        "--data-dir",
        str(REPO_ROOT / "data"),
        "--out-dir",
        str(out_dir),
        "--idempotency-mode",
        idempotency,
        "--json",
    ]
    if interview_file is not None:
        argv += ["--interview-file", str(interview_file)]
    monkeypatch.setattr(sys, "argv", argv)
    return _load_script_module().main()


# ---------- 1. happy path ----------


def test_happy_path(tmp_path, capsys, monkeypatch):
    interview = _interview(tmp_path / "iv.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(confidence=0.85))
    rc = _run(monkeypatch, out_dir=tmp_path, run_id="off-h", interview_file=interview)
    assert rc == 0
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "ok"
    assert env["next_action"] == "done"
    assert env["review_required"] is False
    assert env["outputs"]["n_elements"] == 3
    assert env["outputs"]["rep_name"] == "Devon Park"
    sources = env["outputs"]["sources"]
    assert isinstance(sources, list) and len(sources) > 0
    assert set(sources[0].keys()) == {"doc_name", "passage", "score", "weak"}
    assert (tmp_path / "off-h" / "01_handoff_doc.md").exists()


# ---------- 2. debrief outputs are present ----------


def test_outputs_have_debrief_fields(tmp_path, capsys, monkeypatch):
    interview = _interview(tmp_path / "iv.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    _run(monkeypatch, out_dir=tmp_path, run_id="off-fields", interview_file=interview)
    out = json.loads(capsys.readouterr().out)["outputs"]
    assert out["ramp_barriers"] and out["program_strengths"] and out["suggested_improvements"]
    assert out["elements"][0]["element"]
    assert "accounts" not in out  # no account/handoff language anymore


# ---------- 3. low confidence flags review ----------


def test_low_confidence_flags_review(tmp_path, capsys, monkeypatch):
    interview = _interview(tmp_path / "iv.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock(confidence=0.4))
    _run(monkeypatch, out_dir=tmp_path, run_id="off-low", interview_file=interview)
    env = json.loads(capsys.readouterr().out)
    assert env["review_required"] is True
    assert any("confidence" in r for r in env["outputs"]["review_reasons"])


# ---------- 4. missing interview file ----------


def test_missing_interview_returns_error(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    rc = _run(
        monkeypatch,
        out_dir=tmp_path,
        run_id="off-nf",
        interview_file=tmp_path / "does_not_exist.json",
    )
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "interview_file_missing"


# ---------- 5. invalid interview JSON ----------


def test_invalid_interview_returns_error(tmp_path, capsys, monkeypatch):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    rc = _run(monkeypatch, out_dir=tmp_path, run_id="off-bad", interview_file=bad)
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["status"] == "error"
    assert env["error"]["code"] == "interview_file_invalid"


# ---------- 6. envelope has all 7 keys ----------


def test_envelope_has_all_seven_keys(tmp_path, capsys, monkeypatch):
    interview = _interview(tmp_path / "iv.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    _run(monkeypatch, out_dir=tmp_path, run_id="off-keys", interview_file=interview)
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
    interview = _interview(tmp_path / "iv.json")
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _mock())
    _run(monkeypatch, out_dir=tmp_path, run_id="off-md", interview_file=interview)
    capsys.readouterr()
    md = (tmp_path / "off-md" / "01_handoff_doc.md").read_text()
    assert "# Onboarding debrief" in md
    assert "## Summary" in md
    assert "## Experience by element" in md
    assert "## Barriers to ramp" in md
    assert "## What worked well" in md
    assert "## Suggested improvements" in md
