"""MCP tools server — callable wrappers around our skills/automations.

Three tools are exposed:

  invoke_onboarding_plan(hire_id, horizon_days=30)
      Run Step 1 (generate-onboarding-plan) and return its JSON envelope.

  invoke_trail_guide_ranking(hire_id, top_n=5)
      Run Step 3 (rank-trail-guides) and return its JSON envelope.

  preview_envelope_schema()
      Static documentation tool — return a dict describing each of the 7
      keys in the standard envelope so the model can reason about what
      each invoke_* tool returns.

Run via Claude Code (.mcp.json) or directly:

    uv run python -m mcp_servers.tools_server
"""

from __future__ import annotations

import json
import subprocess
import uuid
from pathlib import Path

from mcp.server.fastmcp import FastMCP

REPO_ROOT = Path(__file__).resolve().parent.parent

PLAN_SCRIPT = REPO_ROOT / "skills" / "generate-onboarding-plan" / "scripts" / "generate_onboarding_plan.py"
RANK_SCRIPT = REPO_ROOT / "automations" / "rank-trail-guides" / "scripts" / "rank_trail_guides.py"

server = FastMCP("sdr-onboarding-tools")


def _run_step(script_path: Path, hire_id: str, extra_args: list[str]) -> dict:
    run_id = f"mcp-{uuid.uuid4().hex[:12]}"
    step_id = f"step-{uuid.uuid4().hex[:8]}"
    cmd = [
        "uv",
        "run",
        "python",
        str(script_path),
        "--hire-id",
        hire_id,
        "--workflow-run-id",
        run_id,
        "--step-id",
        step_id,
        "--json",
        *extra_args,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    try:
        return json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {
                "code": "subprocess_failed",
                "message": (result.stderr or result.stdout or "").strip(),
            },
        }


@server.tool()
def invoke_onboarding_plan(hire_id: str, horizon_days: int = 30) -> dict:
    """Run Step 1 of the SDR onboarding workflow (generate-onboarding-plan).

    Builds a deterministic pre-boarding plan (up to 4 weekly themes with
    territory-, vertical-, and experience-level-specific modules) and writes
    it to data/working/<run_id>/01_onboarding_plan.md. Returns the standard
    JSON envelope with next_action="rank-trail-guides".
    """
    return _run_step(PLAN_SCRIPT, hire_id, ["--horizon-days", str(horizon_days)])


@server.tool()
def invoke_trail_guide_ranking(hire_id: str, top_n: int = 5) -> dict:
    """Run Step 3 of the SDR onboarding workflow (rank-trail-guides).

    Scores every AE mentor on a transparent five-component 0-100 scale and
    writes the top-N ranking to data/working/<run_id>/02_trail_guides.md.
    Returns the standard JSON envelope with next_action="welcome-new-hire".
    """
    return _run_step(RANK_SCRIPT, hire_id, ["--top-n", str(top_n)])


@server.tool()
def preview_envelope_schema() -> dict:
    """Return a documentation dict describing the 7 keys of the JSON envelope.

    Every invoke_* tool in this server returns an envelope shaped like this,
    so the model can call this tool once and then reason about every other
    tool's response uniformly. Use this to explain to a user what each field
    in a returned envelope means without having to inspect the source.
    """
    return {
        "status": "One of 'ok', 'error', or 'needs_review'. Drives downstream branching.",
        "next_action": "Name of the next step to invoke, or 'done' for the terminal step.",
        "confidence": "Float in [0, 1]. The step's self-reported confidence in its output.",
        "review_required": "True when a human should review before the workflow continues.",
        "artifact_refs": "List of relative paths to files this step wrote under the run directory.",
        "outputs": "Step-specific dict of structured outputs intended for downstream steps.",
        "error": "Null on success. On failure, {'code': str, 'message': str} describing the failure.",
    }


if __name__ == "__main__":
    server.run()
