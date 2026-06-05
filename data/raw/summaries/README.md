# `data/raw/summaries/`

Per-hire **personalized summaries** consumed by the `generate-onboarding-plan` LLM skill. One Markdown file per hire, keyed by `hire_id` (e.g. `HIRE-001.md`).

A summary is the **stable, PII-stripped, structured record** an HR/ATS pipeline produces at intake. In a real system the ingestion path is:

```
resume parser  ─┐
LinkedIn fetch ─┼─→ (LLM summarizer + redactor) ─→ data/raw/summaries/<HIRE-ID>.md
ATS application ┘
```

For the milestone, the summaries are hand-authored. Two are committed (HIRE-001, HIRE-006) as demo inputs; the rest can be added on the same template.

## Why a per-hire summary file (not raw resume)

The summary file is the **single, auditable, model-facing input** for personalization. By feeding the LLM this curated file instead of raw resume text:

- PII (DOB, address, marital status, citizenship) never reaches the LLM.
- The data is normalized into named sections the planner can reason about.
- HR can edit a hire's summary directly if the parser got something wrong.
- Tests can drop a synthetic summary into a `tmp_path` directory and exercise the full chain offline.

## Required sections

Every summary must include the following H2 headings. Keep each section short — the LLM has a context budget.

```markdown
# Hire summary — <Name> (<HIRE-ID>)

## Background
2-3 sentences on who they are and what they bring.

## Prior experience
Companies, roles, durations. No salary, no manager names.

## Vertical context
Domain expertise the hire already has (or doesn't). One-liners.

## Trailhead modules already completed
Module IDs from rag/knowledge_base/trailhead_module_catalog.md, one per line.
If none, write "None on record."

## Stated learning goals
What the hire said they want to get out of onboarding.

## Notes for the planner
Any flags or constraints (visa, timezone, accessibility, etc.).
```

## Graceful fallback

If `data/raw/summaries/<HIRE-ID>.md` is missing, the planner falls back to the CSV row from `sdr_profiles.csv` and emits the plan with **lower confidence** (typically 0.55-0.65) so the standard human-review gate catches it.
