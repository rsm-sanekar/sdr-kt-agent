"""Tests for mcp_servers/data_server.py."""

from __future__ import annotations

import asyncio
import json

from mcp_servers.data_server import (
    all_ae_profiles,
    all_sdr_profiles,
    one_sdr_profile,
    server,
)

# ---------- server identity + resource registry ----------


def test_server_name():
    assert server.name == "sdr-onboarding-data"


def test_server_registers_three_resources():
    # FastMCP splits concrete URIs from templated ones — combine both.
    resources = asyncio.run(server.list_resources())
    templates = asyncio.run(server.list_resource_templates())
    assert len(resources) + len(templates) == 3

    uris = {str(r.uri) for r in resources} | {t.uriTemplate for t in templates}
    assert uris == {
        "sdr-profiles://all",
        "sdr-profiles://{hire_id}",
        "ae-profiles://all",
    }


def test_each_resource_has_nonempty_description():
    resources = asyncio.run(server.list_resources())
    templates = asyncio.run(server.list_resource_templates())
    for r in resources:
        assert r.description and r.description.strip()
    for t in templates:
        assert t.description and t.description.strip()


# ---------- resource handlers ----------


def test_all_sdr_profiles_returns_parseable_json_with_hire_001():
    payload = json.loads(all_sdr_profiles())
    assert isinstance(payload, list)
    ids = {row["hire_id"] for row in payload}
    assert "HIRE-001" in ids


def test_one_sdr_profile_known_hire():
    payload = json.loads(one_sdr_profile("HIRE-001"))
    assert payload["name"] == "Priya Sharma"
    assert payload["territory"] == "EMEA"
    assert payload["vertical"] == "healthcare"


def test_one_sdr_profile_unknown_hire_returns_error():
    payload = json.loads(one_sdr_profile("HIRE-999"))
    assert payload["error"] == "hire_not_found"


def test_all_ae_profiles_returns_15_entries():
    payload = json.loads(all_ae_profiles())
    assert isinstance(payload, list)
    assert len(payload) == 15
