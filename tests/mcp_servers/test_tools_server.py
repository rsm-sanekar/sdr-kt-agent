"""Tests for mcp_servers/tools_server.py."""

from __future__ import annotations

import asyncio
import json

from mcp_servers.tools_server import (
    invoke_onboarding_plan,
    invoke_trail_guide_ranking,
    preview_envelope_schema,
    server,
)

ENVELOPE_KEYS = {
    "status",
    "next_action",
    "confidence",
    "review_required",
    "artifact_refs",
    "outputs",
    "error",
}


_PLAN_MOCK = json.dumps(
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
                        "rationale": "Required even with pharma background.",
                    },
                ],
                "activities": ["Shadow 4 discovery calls"],
            }
        ],
        "skip_rationale": [],
        "confidence": 0.88,
    }
)


# ---------- server identity + tool registry ----------


def test_server_name():
    assert server.name == "sdr-onboarding-tools"


def test_list_tools_returns_three():
    tools = asyncio.run(server.list_tools())
    assert len(tools) == 3
    names = {t.name for t in tools}
    assert names == {
        "invoke_onboarding_plan",
        "invoke_trail_guide_ranking",
        "preview_envelope_schema",
    }


def test_each_tool_has_meaningful_description():
    tools = asyncio.run(server.list_tools())
    for t in tools:
        assert t.description, f"tool {t.name} has no description"
        assert len(t.description) > 40, (
            f"tool {t.name} description is too short ({len(t.description)} chars): {t.description!r}"
        )


# ---------- invoke tools (real subprocess) ----------


def test_invoke_onboarding_plan_happy_path(monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _PLAN_MOCK)
    env = invoke_onboarding_plan(hire_id="HIRE-001")
    assert env["status"] in {"ok", "needs_review"}
    assert env["next_action"] == "rank-trail-guides"


def test_invoke_trail_guide_ranking_top_three():
    env = invoke_trail_guide_ranking(hire_id="HIRE-001", top_n=3)
    assert env["status"] == "ok"
    assert env["artifact_refs"], "expected at least one artifact reference"


def test_invoke_onboarding_plan_unknown_hire_returns_error(monkeypatch):
    monkeypatch.setenv("MOCK_LLM_RESPONSE", _PLAN_MOCK)
    env = invoke_onboarding_plan(hire_id="HIRE-999")
    assert env["status"] == "error"
    assert env["error"]["code"] == "hire_not_found"


# ---------- schema preview ----------


def test_preview_envelope_schema_has_all_seven_keys():
    schema = preview_envelope_schema()
    assert set(schema.keys()) == ENVELOPE_KEYS
    for key, doc in schema.items():
        assert isinstance(doc, str) and doc.strip(), f"empty doc for {key}"
