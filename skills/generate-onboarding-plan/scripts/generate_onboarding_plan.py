"""LLM skill: build a personalized SDR onboarding plan grounded in proprietary docs."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import polars as pl
from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from rag.retrieval import build_index, build_sources, retrieve  # noqa: E402
from utils.connect import ask_json  # noqa: E402
from utils.sdr_common import (  # noqa: E402
    ensure_run_dir,
    make_envelope,
    make_skill_parser,
    needs_human_review,
    run_step,
)

CATALOG_FILE = REPO_ROOT / "rag" / "knowledge_base" / "trailhead_module_catalog.md"
_CATALOG_ID_RE = re.compile(r"^\|\s*(TRAIL-[A-Z0-9-]+)\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)

BASE_SYSTEM_PROMPT = (
    "You are an SDR onboarding designer at Salesforce. Produce a personalized "
    "onboarding plan for a new Sales Development Representative. "
    "You MUST return a JSON object with the required fields (summary, weeks, "
    "skip_rationale, confidence) filled in with real content — never echo the "
    "schema definition itself. "
    "You MUST only emit module_id values from the ALLOW-LIST below. Do not invent "
    "module ids. For each module assigned, give a one-sentence rationale tied to "
    "the specific hire's profile. Calibrate plan depth to experience level: entry "
    "→ 4 weeks, mid → 3 weeks, senior → 2 weeks. Skip any module the hire has "
    "already completed and record each skip in skip_rationale."
)


class TrailheadModule(BaseModel):
    module_id: str = Field(min_length=4)
    title: str = Field(min_length=2)
    rationale: str = Field(min_length=10)


class Week(BaseModel):
    week_number: int = Field(ge=1, le=6)
    theme: str = Field(min_length=3)
    modules: list[TrailheadModule] = Field(min_length=1, max_length=6)
    activities: list[str] = Field(default_factory=list)


class OnboardingPlan(BaseModel):
    summary: str = Field(min_length=20)
    weeks: list[Week] = Field(min_length=1, max_length=4)
    skip_rationale: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


OnboardingPlan.model_rebuild()


def _load_catalog() -> dict[str, str]:
    """Return {module_id: title} for every row in the catalog table."""
    if not CATALOG_FILE.exists():
        return {}
    text = CATALOG_FILE.read_text(encoding="utf-8")
    return {m.group(1): m.group(2) for m in _CATALOG_ID_RE.finditer(text)}


def _read_summary(data_dir: Path, hire_id: str) -> str | None:
    """Read the hire's per-hire summary.md if present; return None otherwise."""
    path = data_dir / "raw" / "summaries" / f"{hire_id}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _format_context(chunks) -> str:
    sections = [f"### {c.doc_name}\n{c.text}" for c in chunks]
    return (
        "Reference internal documents (use these when relevant; do not invent "
        "details that contradict them):\n\n" + "\n\n".join(sections)
    )


def _format_catalog(catalog: dict[str, str]) -> str:
    if not catalog:
        return ""
    lines = ["ALLOW-LIST (use only these module_id values):"]
    for module_id, title in sorted(catalog.items()):
        lines.append(f"- {module_id}: {title}")
    return "\n".join(lines)


def _system_prompt(catalog: dict[str, str], chunks) -> str:
    parts = [BASE_SYSTEM_PROMPT]
    catalog_block = _format_catalog(catalog)
    if catalog_block:
        parts.append(catalog_block)
    if chunks:
        parts.append(_format_context(chunks))
    return "\n\n".join(parts)


def _build_user_prompt(hire: dict, summary: str | None) -> str:
    lines = [
        f"Hire: {hire['name']} ({hire['hire_id']})",
        f"Territory: {hire['territory']}",
        f"Vertical: {hire['vertical']}",
        f"Experience level: {hire['experience_level']}",
        f"Prior role: {hire['prior_role']}",
        "",
    ]
    if summary:
        lines += ["Personalized summary (curated at intake):", "", summary, ""]
    else:
        lines += [
            "Personalized summary: NOT AVAILABLE for this hire. Build the plan from "
            "the profile fields above and lower your confidence accordingly.",
            "",
        ]
    lines.append("Produce the onboarding plan as JSON matching the schema.")
    return "\n".join(lines)


def _render_markdown(hire: dict, plan: OnboardingPlan, summary_present: bool) -> str:
    lines = [
        f"# Onboarding plan — {hire['name']} ({hire['hire_id']})",
        "",
        f"_Profile: {hire['territory']} / {hire['vertical']} / {hire['experience_level']}_",
        f"_Source: personalized summary {'loaded' if summary_present else 'NOT loaded (CSV-only fallback)'}_",
        f"_Planner confidence: {plan.confidence}_",
        "",
        "## Summary",
        "",
        plan.summary,
        "",
    ]
    for week in plan.weeks:
        lines.append(f"## Week {week.week_number}: {week.theme}")
        lines.append("")
        lines.append("**Modules**")
        lines.append("")
        for module in week.modules:
            lines.append(f"- `{module.module_id}` — {module.title}")
            lines.append(f"  - _Why for this hire:_ {module.rationale}")
        if week.activities:
            lines.append("")
            lines.append("**Activities**")
            lines.append("")
            for activity in week.activities:
                lines.append(f"- {activity}")
        lines.append("")
    if plan.skip_rationale:
        lines += ["## Skipped modules", ""]
        lines += [f"- {item}" for item in plan.skip_rationale]
        lines.append("")
    return "\n".join(lines)


def _validate_module_ids(plan: OnboardingPlan, catalog: dict[str, str]) -> list[str]:
    if not catalog:
        return []
    invalid: list[str] = []
    for week in plan.weeks:
        for module in week.modules:
            if module.module_id not in catalog:
                invalid.append(module.module_id)
    return invalid


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

    summary = _read_summary(Path(args.data_dir), args.hire_id)

    rag_query = (
        f"onboarding {hire['vertical']} {hire['experience_level']} "
        f"trailhead modules territory {hire['territory']}"
    )
    chunks = retrieve(rag_query, build_index(), top_k=4)

    catalog = _load_catalog()
    system_prompt = _system_prompt(catalog, chunks)
    user_prompt = _build_user_prompt(hire, summary)

    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock is not None:
        plan = OnboardingPlan.model_validate_json(mock)
    else:
        plan = ask_json(user_prompt, schema=OnboardingPlan, system=system_prompt, model="claude-sonnet-4-6")

    invalid_modules = _validate_module_ids(plan, catalog)
    summary_present = summary is not None

    run_dir = ensure_run_dir(args.out_dir, args.workflow_run_id)
    (run_dir / "01_onboarding_plan.md").write_text(_render_markdown(hire, plan, summary_present))

    review_required = (
        bool(invalid_modules)
        or not summary_present
        or needs_human_review(plan.confidence, threshold=0.70)
    )
    outputs = {
        "hire_id": hire["hire_id"],
        "n_weeks": len(plan.weeks),
        "n_modules": sum(len(w.modules) for w in plan.weeks),
        "summary_present": summary_present,
        "invalid_modules": invalid_modules,
        "retrieved_docs": [c.doc_name for c in chunks],
        "sources": build_sources(chunks),
    }
    return make_envelope(
        status="needs_review" if review_required else "ok",
        next_action="rank-trail-guides",
        confidence=plan.confidence,
        review_required=review_required,
        artifact_refs=["01_onboarding_plan.md"],
        outputs=outputs,
    )


def main() -> int:
    parser = make_skill_parser("LLM skill: build a personalized SDR onboarding plan")
    parser.add_argument("--horizon-days", type=int, default=30)
    args = parser.parse_args()
    return run_step(args, do_work)


if __name__ == "__main__":
    raise SystemExit(main())
