---
name: generate-onboarding-plan
description: Use this skill to produce a personalized 1-4 week Trailhead-grounded SDR onboarding plan for a new hire. The skill reads the hire's profile and per-hire summary, retrieves the matching gold-standard template and the Trailhead module allow-list from RAG, and asks an LLM to adapt the template to the hire's actual background. First step of the SDR onboarding workflow.
---

# Generate onboarding plan

## Runtime modes

Invokable from a terminal, from the orchestrator, or by an agent. This is the **first step** of the SDR pre-boarding chain — it runs before `rank-trail-guides` and `welcome-new-hire`.

## What the script needs

Standard CLI flags from `utils.sdr_common.make_skill_parser`, plus:

- `--horizon-days` (default `30`) — soft hint for plan length; the LLM still calibrates by experience level (entry=4 weeks, mid=3, senior=2).

Upstream artifacts required:

- `data/raw/sdr_profiles.csv` (seed hire data)
- `rag/knowledge_base/trailhead_module_catalog.md` (the allow-list — without this the skill cannot validate module ids)

Upstream artifacts **optional but strongly recommended**:

- `data/raw/summaries/<HIRE-ID>.md` — per-hire personalized summary (background, prior experience, already-completed modules, learning goals). When this file is **absent** the plan still runs but `review_required` is forced to `true` and `confidence` drops, because the LLM has only the CSV row to work from.

## How to use this skill

1. Confirm `data/raw/summaries/<HIRE-ID>.md` exists for the hire (or accept that the plan will be flagged for review).
2. Invoke this skill with `--hire-id`, a fresh `--workflow-run-id`, and `--step-id` (typically `step1` or `generate-onboarding-plan`).
3. Read the envelope. If `review_required=true`, check `outputs.invalid_modules` (LLM hallucinated module ids that aren't in the catalog) and `outputs.summary_present` (whether the personalized summary was loaded).
4. The rendered plan lives at `<run_dir>/01_onboarding_plan.md`.

## What the LLM receives

A system prompt that:

1. States the role ("SDR onboarding designer at Salesforce").
2. Inlines the **Trailhead module allow-list** from `rag/knowledge_base/trailhead_module_catalog.md` and instructs the model to use only module ids from that list.
3. Calibrates plan depth by experience level (entry=4 weeks / mid=3 / senior=2).
4. Appends the top-4 RAG-retrieved chunks (typically the matching gold-standard template, the onboarding policy `SDR-OB-2024-03`, the relevant vertical playbook, and the mentor program handbook).

The user prompt carries the hire's CSV row + the full text of `summary.md` (or a `NOT AVAILABLE` notice when missing).

Output is validated against the Pydantic `OnboardingPlan` schema:

- `summary`: 1-3 sentence personalized intro (≥20 chars)
- `weeks`: 1-4 weeks. Each week has `week_number`, `theme`, `modules` (1-6), and optional `activities`. Each module has `module_id`, `title`, `rationale`.
- `skip_rationale`: list of strings explaining which modules were skipped and why (typically because the hire already completed them).
- `confidence`: float 0-1.

## Catalog allow-list validation

After the LLM returns, every `module_id` in `plan.weeks` is checked against the catalog. **Any `module_id` not in the catalog forces `review_required=true`** and is surfaced in `outputs.invalid_modules`. This is the primary hallucination safeguard.

## What it writes

- `<run_dir>/01_onboarding_plan.md` — sectioned Markdown plan with summary, weeks (each with module list + rationales + activities), and skipped-module rationale.
- JSON envelope on stdout:
  - `status`: `"ok"` or `"needs_review"`
  - `next_action`: `"rank-trail-guides"`
  - `confidence`, `review_required`, `artifact_refs=["01_onboarding_plan.md"]`
  - `outputs`: `{"hire_id", "n_weeks", "n_modules", "summary_present", "invalid_modules", "retrieved_docs"}`

Errors: `profiles_missing`, `hire_not_found`.

## Example

```bash
uv run python skills/generate-onboarding-plan/scripts/generate_onboarding_plan.py \
  --hire-id HIRE-001 --workflow-run-id wf-demo --step-id step1 --json
```

For offline / test runs, set `MOCK_LLM_RESPONSE` to a JSON string matching the `OnboardingPlan` schema; the skill uses it verbatim instead of calling the LLM.
