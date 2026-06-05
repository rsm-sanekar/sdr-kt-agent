---
name: generate-handoff-doc
description: Use this skill to synthesize a post-certification onboarding debrief from a newly-certified SDR's self-assessment of their 12-week ramp. Produces a structured, manager-facing debrief (summary, per-element feedback, ramp barriers, program strengths, suggested improvements) so the enablement team can improve the program. Standalone — invoked by the `/offboarding/synthesize` endpoint (Onboarding Debrief tab).
---

# Generate onboarding debrief

## Runtime modes

Invokable from a terminal, from the debrief endpoint (`POST /offboarding/synthesize`), or by an agent. Envelope reports `next_action="done"` — this skill never hands off.

## What the script needs

Standard CLI flags from `utils.sdr_common.make_skill_parser`, plus:

- `--interview-file` — path to a JSON file with the SDR info + Q&A pairs.

The interview file shape (mirrors `QUESTIONS.md`):

```json
{
  "rep_info": {
    "name": "Devon Park",
    "territory": "AMER-West",
    "vertical": "healthcare"
  },
  "qa_pairs": [
    {"question_id": 1, "question": "...", "answer": "..."},
    ...
  ]
}
```

`--hire-id` is **not required** — the SDR info comes entirely from the interview file.

## What the LLM receives

A system prompt instructing it to act as a Salesforce enablement specialist synthesizing a program debrief (NOT an account handoff), with rules for per-element feedback, ramp barriers, and actionable improvements. Retrieval pulls from the territory definition + vertical playbook so any program references are grounded.

## Schema (Pydantic)

- `summary`: 3-5 sentence memo for the manager
- `elements`: list of 1-6 `ElementFeedback` records
  - `element` (e.g. Onboarding plan / AI Tutor / Cold-call sim / Coaching / Territory playbook), `what_worked`, `what_to_improve`
- `ramp_barriers`: 1-5 bullets
- `program_strengths`: 1-5 bullets
- `suggested_improvements`: 1-5 bullets
- `confidence`: float 0-1

## Review triggers

`review_required = true` if `confidence < 0.65`. Triggers are surfaced in `outputs.review_reasons`.

## What it writes

- `<run_dir>/01_handoff_doc.md` — sectioned Markdown debrief (filename kept for route stability).
- JSON envelope on stdout:
  - `status`: `"ok"` or `"needs_review"`
  - `next_action`: `"done"`
  - `confidence`, `review_required`, `artifact_refs=["01_handoff_doc.md"]`
  - `outputs`: `{rep_name, territory, vertical, n_elements, elements, ramp_barriers, program_strengths, suggested_improvements, review_reasons, retrieved_docs, sources}`

Errors: `interview_file_missing`, `interview_file_invalid`.

## Example

```bash
uv run python skills/generate-handoff-doc/scripts/generate_handoff_doc.py \
  --workflow-run-id debrief-demo --step-id generate-handoff-doc \
  --out-dir data/working/offboarding \
  --interview-file /tmp/devon-debrief.json --json
```

For offline runs, set `MOCK_LLM_RESPONSE` to a JSON string matching `DebriefDoc`.
