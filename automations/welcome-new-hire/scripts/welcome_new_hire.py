"""Step 3: deterministically render a personalized SDR welcome email from a template.

Slot-fills the hire's profile (`data/raw/sdr_profiles.csv`) and the top-ranked
mentor parsed out of `<run_dir>/02_trail_guides.md` into a four-paragraph
template. The third paragraph is chosen from one of three per-experience-level
variants (``entry`` / ``mid`` / ``senior``). No LLM call, no RAG —
``confidence=1.0`` and ``review_required=False`` so the chain auto-completes;
the manager can still see and edit the artifact from the run view.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from utils.sdr_common import (  # noqa: E402
    ensure_run_dir,
    make_envelope,
    make_skill_parser,
    run_step,
)


def _parse_top_mentor(md_text: str) -> tuple[str, str] | None:
    """Return (ae_id, name) from the first ranked row of the trail-guides table."""
    for line in md_text.splitlines():
        m = re.match(r"^\|\s*1\s*\|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # cells: [rank, ae_id, name, territory, vertical, total, ...]
        return cells[1], cells[2]
    return None


def _first_name(name: str) -> str:
    return name.split()[0] if name else "there"


# Per-experience-level paragraph blocks. Each adds one tailored paragraph
# between the mentor introduction and the closing — keeps the email from
# sounding boilerplate without needing a generative model.
_LEVEL_PARAGRAPH = {
    "entry": (
        "Your first week is structured: complete the policy-required Trailhead "
        "modules (CRM Basics + the vertical-specific module for your level), "
        "shadow at least 4 discovery calls, and join the weekly SDR standup. "
        "Don't worry about your first dial yet — week one is about calibration."
    ),
    "mid": (
        "We'll skip the ramp basics — your prior experience covers it. Your "
        "first week is about shadowing for territory context and connecting "
        "with the peer SDRs in your vertical; their relationships are your "
        "fastest path to local context."
    ),
    "senior": (
        "We'd love your perspective on the territory once you've had a chance "
        "to sit with the data — the team values challenge from senior voices, "
        "and ramp is intentionally short so you can start contributing fast."
    ),
}


def _build_subject(hire: dict) -> str:
    return f"Welcome to the Salesforce SDR team, {_first_name(hire['name'])}"


def _build_body(hire: dict, mentor_name: str, mentor_ae_id: str) -> str:
    first = _first_name(hire["name"])
    level_paragraph = _LEVEL_PARAGRAPH.get(
        hire["experience_level"], _LEVEL_PARAGRAPH["mid"]
    )
    return (
        f"Hi {first},\n\n"
        f"Welcome to Salesforce. You're joining the {hire['vertical']} team in "
        f"{hire['territory']}, and we're excited to have you on board.\n\n"
        f"Your Trail Guide for the first 90 days is {mentor_name} "
        f"({mentor_ae_id}). They've been matched to you on territory and "
        f"vertical fit, and they'll be your first stop for ramp questions, "
        f"shadowing, and live-deal walkthroughs.\n\n"
        f"{level_paragraph}\n\n"
        f"If anything blocks you in the first week, ping {mentor_name} "
        f"directly, or escalate to People Ops per the escalation playbook.\n\n"
        f"Welcome aboard,\n"
        f"The Salesforce SDR onboarding team"
    )


def _render_email(hire: dict, mentor_ae_id: str, mentor_name: str) -> tuple[str, str]:
    """Return (subject, full_markdown_artifact)."""
    subject = _build_subject(hire)
    body = _build_body(hire, mentor_name, mentor_ae_id)
    artifact = (
        f"# Welcome email for {hire['name']}\n\n"
        f"**Subject:** {subject}\n\n"
        f"{body}\n"
    )
    return subject, artifact


def do_work(args) -> dict:
    profiles_path = Path(args.data_dir) / "raw" / "sdr_profiles.csv"
    if not profiles_path.exists():
        return make_envelope(
            status="error",
            error={"code": "profiles_missing", "message": f"{profiles_path} not found"},
        )

    sdrs = pl.read_csv(profiles_path)
    row = sdrs.filter(pl.col("hire_id") == args.hire_id)
    if row.is_empty():
        return make_envelope(
            status="error",
            error={
                "code": "hire_not_found",
                "message": f"hire_id {args.hire_id!r} not present in {profiles_path}",
            },
        )
    hire = row.row(0, named=True)

    run_dir = ensure_run_dir(args.out_dir, args.workflow_run_id)
    mentor_file = run_dir / "02_trail_guides.md"
    if not mentor_file.exists():
        return make_envelope(
            status="error",
            error={
                "code": "mentor_ranking_not_found",
                "message": (
                    f"{mentor_file} not found. Run rank-trail-guides for "
                    f"workflow_run_id {args.workflow_run_id!r} first."
                ),
            },
        )

    parsed = _parse_top_mentor(mentor_file.read_text())
    if parsed is None:
        return make_envelope(
            status="error",
            error={
                "code": "mentor_ranking_unparseable",
                "message": f"Could not parse top mentor row from {mentor_file}",
            },
        )
    mentor_ae_id, mentor_name = parsed

    subject, artifact = _render_email(hire, mentor_ae_id, mentor_name)
    (run_dir / "03_welcome_email.md").write_text(artifact)

    return make_envelope(
        status="ok",
        next_action="done",
        confidence=1.0,
        review_required=False,
        artifact_refs=["03_welcome_email.md"],
        outputs={
            "hire_id": hire["hire_id"],
            "mentor_ae_id": mentor_ae_id,
            "mentor_name": mentor_name,
            "subject": subject,
            "experience_level": hire["experience_level"],
        },
    )


def main() -> int:
    parser = make_skill_parser("Step 3: render a personalized SDR welcome email (deterministic)")
    args = parser.parse_args()
    return run_step(args, do_work)


if __name__ == "__main__":
    raise SystemExit(main())
