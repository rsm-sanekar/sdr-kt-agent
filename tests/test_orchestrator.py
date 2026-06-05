"""End-to-end happy-path test for scripts/orchestrator.py."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "orchestrator.py"

# One JSON payload that satisfies all three LLM schemas in the chain
# (OnboardingPlan, WelcomeEmail, CoachingNote). Pydantic ignores extra
# fields, so each skill only validates the keys it cares about.
TRI_MOCK = (
    "{"
    '"summary":"Priya brings clinical-buyer fluency from Pfizer; compress HIPAA basics '
    'and lean into payer/provider personas in week 1.",'
    '"weeks":[{"week_number":1,"theme":"Salesforce + healthcare baseline",'
    '"modules":[{"module_id":"TRAIL-CRM-101","title":"Salesforce CRM Basics",'
    '"rationale":"New to Salesforce CRM after years on Veeva."},'
    '{"module_id":"TRAIL-VERT-HC-101","title":"HIPAA-Aware Selling",'
    '"rationale":"Required even with pharma background per policy SDR-OB-2024-03."}],'
    '"activities":["Shadow 4 discovery calls"]}],'
    '"skip_rationale":[],'
    '"subject":"Welcome aboard!",'
    '"body":"Hi there, the whole team is excited to have you join us. '
    "We have lined up an experienced mentor to guide you through your "
    'first 90 days. Looking forward to working with you.",'
    '"what_worked":["Clear opener","Strong discovery question"],'
    '"what_to_improve":["Handle budget objection more confidently"],'
    '"language_alternatives":['
    '"Replace just checking in with following up",'
    '"Replace I think with based on what you shared"'
    "],"
    '"overall_score":7,'
    '"confidence":0.92'
    "}"
)


def _load_script_module():
    spec = importlib.util.spec_from_file_location("orchestrator", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_orchestrator_runs_all_three_steps(capsys, monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", TRI_MOCK)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--hire-id", "HIRE-001"])

    rc = _load_script_module().main()
    out = capsys.readouterr().out

    assert rc == 0
    for step in (
        "generate-onboarding-plan",
        "rank-trail-guides",
        "welcome-new-hire",
    ):
        assert f"--- step: {step} ---" in out, f"step {step!r} did not run"

    # The final envelope printed should report next_action="done".
    next_actions = re.findall(r'"next_action":\s*"([^"]+)"', out)
    assert next_actions, "no envelope with next_action key found in orchestrator output"
    assert next_actions[-1] == "done"
