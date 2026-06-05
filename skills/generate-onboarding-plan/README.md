# `generate-onboarding-plan`

**First step of the SDR onboarding workflow.** LLM skill that produces a personalized Trailhead-grounded onboarding plan for a new SDR hire. Reads the hire's row from `data/raw/sdr_profiles.csv` and their personalized summary from `data/raw/summaries/<HIRE-ID>.md`, RAG-retrieves the matching gold-standard template plus the Trailhead module allow-list, then asks an LLM to adapt the template to the hire's actual background. Every `module_id` the LLM emits is validated against the catalog allow-list (`rag/knowledge_base/trailhead_module_catalog.md`) — any unknown id forces `review_required=true`.

## Run

```bash
uv run python skills/generate-onboarding-plan/scripts/generate_onboarding_plan.py \
  --hire-id HIRE-001 \
  --workflow-run-id wf-demo \
  --step-id step1 \
  --json
```

For offline testing, set `MOCK_LLM_RESPONSE` to skip the network call:

```bash
MOCK_LLM_RESPONSE='{"summary":"Priya brings strong clinical-buyer fluency from Pfizer; compress HIPAA basics and lean into payer/provider personas in week 1.","weeks":[{"week_number":1,"theme":"Salesforce + healthcare baseline","modules":[{"module_id":"TRAIL-CRM-101","title":"Salesforce CRM Basics","rationale":"New to Salesforce CRM after years on Veeva."},{"module_id":"TRAIL-VERT-HC-101","title":"HIPAA-Aware Selling","rationale":"Required even with pharma background, per policy SDR-OB-2024-03."}],"activities":["Shadow 4 discovery calls"]}],"skip_rationale":[],"confidence":0.88}' \
  uv run python skills/generate-onboarding-plan/scripts/generate_onboarding_plan.py \
    --hire-id HIRE-001 --workflow-run-id wf-demo --step-id step1 --json
```

Returns `next_action="rank-trail-guides"` and `artifact_refs=["01_onboarding_plan.md"]`.

Error codes: `profiles_missing` (CSV missing), `hire_not_found` (unknown `--hire-id`).

## Review triggers

`review_required=true` is set when any of:

- the LLM emitted a `module_id` that is not in the catalog allow-list (full list surfaced in `outputs.invalid_modules`)
- `data/raw/summaries/<HIRE-ID>.md` was missing (the plan still gets written from CSV fields only, but is flagged)
- model self-reported `confidence < 0.70`

## How to add a new hire summary

Drop a Markdown file at `data/raw/summaries/<HIRE-ID>.md` with the section headers documented in [`data/raw/summaries/README.md`](../../data/raw/summaries/README.md). The planner picks it up automatically the next run.
