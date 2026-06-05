"""Step 3: deterministically score and rank AE mentors ("trail guides") for an SDR hire."""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from utils.sdr_common import (  # noqa: E402
    ensure_run_dir,
    make_envelope,
    make_skill_parser,
    needs_human_review,
    run_step,
)


def _score_row(ae: dict, hire: dict) -> dict:
    territory_pts = 30.0 if ae["territory"] == hire["territory"] else 0.0
    vertical_pts = 30.0 if ae["vertical"] == hire["vertical"] else 0.0
    satisfaction_pts = (ae["satisfaction_score"] / 5.0) * 20.0
    hours_pts = (ae["mentorship_hours_per_week"] / 5.0) * 10.0
    mentees_pts = min(ae["prior_mentees"] / 10.0, 1.0) * 10.0
    total = territory_pts + vertical_pts + satisfaction_pts + hours_pts + mentees_pts
    return {
        "ae_id": ae["ae_id"],
        "name": ae["name"],
        "territory": ae["territory"],
        "vertical": ae["vertical"],
        "territory_pts": round(territory_pts, 2),
        "vertical_pts": round(vertical_pts, 2),
        "satisfaction_pts": round(satisfaction_pts, 2),
        "hours_pts": round(hours_pts, 2),
        "mentees_pts": round(mentees_pts, 2),
        "total_score": round(total, 2),
    }


def _confidence_for(top_score: float) -> float:
    if top_score >= 70:
        return 1.0
    if top_score >= 50:
        return 0.7
    return 0.4


def _render_markdown(hire: dict, ranked: list[dict]) -> str:
    lines = [
        f"# Trail-guide ranking — {hire['name']} ({hire['hire_id']})",
        "",
        f"Hire profile: {hire['territory']} / {hire['vertical']} / {hire['experience_level']}",
        "",
        "| Rank | AE ID | Name | Territory | Vertical | Total | Terr | Vert | Sat | Hrs | Mentees |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for i, ae in enumerate(ranked, start=1):
        lines.append(
            f"| {i} | {ae['ae_id']} | {ae['name']} | {ae['territory']} | {ae['vertical']} "
            f"| {ae['total_score']} | {ae['territory_pts']} | {ae['vertical_pts']} "
            f"| {ae['satisfaction_pts']} | {ae['hours_pts']} | {ae['mentees_pts']} |"
        )
    return "\n".join(lines) + "\n"


def do_work(args) -> dict:
    data_dir = Path(args.data_dir)
    sdr_path = data_dir / "raw" / "sdr_profiles.csv"
    ae_path = data_dir / "raw" / "ae_profiles.csv"

    for p in (sdr_path, ae_path):
        if not p.exists():
            return make_envelope(
                status="error",
                error={"code": "data_missing", "message": f"{p} not found"},
            )

    sdrs = pl.read_csv(sdr_path)
    row = sdrs.filter(pl.col("hire_id") == args.hire_id)
    if row.is_empty():
        return make_envelope(
            status="error",
            error={
                "code": "hire_not_found",
                "message": f"hire_id {args.hire_id!r} not present in {sdr_path}",
            },
        )
    hire = row.row(0, named=True)

    aes = pl.read_csv(ae_path)
    scored = [_score_row(ae, hire) for ae in aes.iter_rows(named=True)]
    scored.sort(key=lambda r: (-r["total_score"], r["ae_id"]))
    top = scored[: args.top_n]

    run_dir = ensure_run_dir(args.out_dir, args.workflow_run_id)
    (run_dir / "02_trail_guides.md").write_text(_render_markdown(hire, top))

    top_score = top[0]["total_score"]
    confidence = _confidence_for(top_score)
    review_required = needs_human_review(confidence)

    return make_envelope(
        status="needs_review" if review_required else "ok",
        next_action="welcome-new-hire",
        confidence=confidence,
        review_required=review_required,
        artifact_refs=["02_trail_guides.md"],
        outputs={
            "hire_id": hire["hire_id"],
            "top_ae_id": top[0]["ae_id"],
            "top_score": top_score,
            "n_candidates_scored": len(scored),
        },
    )


def main() -> int:
    parser = make_skill_parser("Step 3: rank AE mentors for an SDR hire")
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args()
    return run_step(args, do_work)


if __name__ == "__main__":
    raise SystemExit(main())
