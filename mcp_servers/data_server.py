"""MCP data server — read-only resources backed by data/raw/ CSVs.

Three resources are exposed:

  sdr-profiles://all           — every SDR hire profile
  sdr-profiles://{hire_id}     — one SDR hire by id (or {"error": "hire_not_found"})
  ae-profiles://all            — every AE mentor profile

Run via Claude Code (.mcp.json) or directly:

    uv run python -m mcp_servers.data_server
"""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
from mcp.server.fastmcp import FastMCP

REPO_ROOT = Path(__file__).resolve().parent.parent
SDR_CSV = REPO_ROOT / "data" / "raw" / "sdr_profiles.csv"
AE_CSV = REPO_ROOT / "data" / "raw" / "ae_profiles.csv"

server = FastMCP("sdr-onboarding-data")


@server.resource("sdr-profiles://all")
def all_sdr_profiles() -> str:
    """All SDR hire profiles available for onboarding."""
    df = pl.read_csv(SDR_CSV)
    return json.dumps(df.to_dicts(), indent=2)


@server.resource("sdr-profiles://{hire_id}")
def one_sdr_profile(hire_id: str) -> str:
    """One SDR hire profile by hire_id (or an error JSON if not found)."""
    df = pl.read_csv(SDR_CSV)
    row = df.filter(pl.col("hire_id") == hire_id)
    if row.is_empty():
        return json.dumps({"error": "hire_not_found", "hire_id": hire_id})
    return json.dumps(row.row(0, named=True), indent=2)


@server.resource("ae-profiles://all")
def all_ae_profiles() -> str:
    """All AE mentor profiles available as trail guides."""
    df = pl.read_csv(AE_CSV)
    return json.dumps(df.to_dicts(), indent=2)


if __name__ == "__main__":
    server.run()
