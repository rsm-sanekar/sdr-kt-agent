"""End-to-end orchestrator for the SDR onboarding workflow.

Chains three steps in order:

    generate-onboarding-plan  (LLM skill)
    rank-trail-guides         (automation)
    welcome-new-hire          (automation)

Each step is invoked as a subprocess with the standard CLI flags and a
shared ``workflow_run_id``. The orchestrator parses the JSON envelope on
stdout, follows ``next_action`` to choose the next step, and stops when a
step reports ``next_action="done"`` or returns an error envelope.

Note: ``score-cold-call`` is no longer chained — it lives behind the
``/coaching`` endpoints in workflow_server.py and is driven by the
Coaching Notes UI (manager uploads a transcript on demand).

Usage:

    uv run python scripts/orchestrator.py --hire-id HIRE-001

For offline / LLM-mocked runs set ``MOCK_LLM_RESPONSE`` in the environment
before invoking — the orchestrator inherits it to every subprocess.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

STEP_SCRIPTS: dict[str, Path] = {
    "generate-onboarding-plan": REPO_ROOT
    / "skills"
    / "generate-onboarding-plan"
    / "scripts"
    / "generate_onboarding_plan.py",
    "rank-trail-guides": REPO_ROOT / "automations" / "rank-trail-guides" / "scripts" / "rank_trail_guides.py",
    "welcome-new-hire": REPO_ROOT / "automations" / "welcome-new-hire" / "scripts" / "welcome_new_hire.py",
}

TERMINAL_ACTIONS = {"done", "closed", None}


def run_step(name: str, script: Path, hire_id: str, run_id: str) -> dict:
    """Run one step as a subprocess and return its JSON envelope."""
    cmd = [
        sys.executable,
        str(script),
        "--json",
        "--hire-id",
        hire_id,
        "--workflow-run-id",
        run_id,
        "--step-id",
        name,
        "--data-dir",
        str(REPO_ROOT / "data"),
        "--out-dir",
        str(REPO_ROOT / "data" / "working"),
    ]
    env = os.environ.copy()  # forwards MOCK_LLM_RESPONSE and anything else
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    if not stdout:
        return {
            "status": "error",
            "error": {
                "code": "no_output",
                "message": (completed.stderr or "").strip() or "step produced no output",
            },
            "exit_code": completed.returncode,
        }
    try:
        return json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "error": {"code": "invalid_envelope", "message": str(exc)},
            "exit_code": completed.returncode,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="SDR onboarding workflow orchestrator")
    parser.add_argument("--hire-id", default="HIRE-001", help="SDR hire identifier (default: HIRE-001).")
    args = parser.parse_args()

    if not STEP_SCRIPTS:
        print("no steps registered yet — edit STEP_SCRIPTS in this file.")
        return 0

    run_id = f"wf-{uuid.uuid4().hex[:12]}"
    print(f"workflow_run_id={run_id} hire_id={args.hire_id}")

    next_step = next(iter(STEP_SCRIPTS))  # start with the first registered step
    while next_step is not None:
        if next_step in TERMINAL_ACTIONS:
            print(f"workflow finished (terminal action: {next_step!r}).")
            break
        if next_step not in STEP_SCRIPTS:
            print(f"unknown next_action {next_step!r} — stopping.")
            return 1

        script = STEP_SCRIPTS[next_step]
        print(f"\n--- step: {next_step} ---")
        envelope = run_step(next_step, script, args.hire_id, run_id)
        print(json.dumps(envelope, indent=2))

        if envelope.get("status") == "error":
            print(f"step {next_step} returned error — stopping.")
            return 1

        action = envelope.get("next_action")
        if action in TERMINAL_ACTIONS:
            print(f"workflow finished after {next_step} (next_action={action!r}).")
            break
        next_step = action

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
