---
name: score-cold-call
description: Score a recorded sales call transcript against Coaching Rubric v3.1 (four weighted dimensions plus what worked / what to improve / language alternatives). Standalone — manager uploads a recording on demand via the Coaching Notes UI; no longer part of the 3-step onboarding chain.
---

# Score cold call

## Runtime modes

Invokable from a terminal, from the Coaching Notes endpoint (`POST /coaching/score`), or by an agent. Envelope reports `next_action="done"` — this skill never hands off.

## What the script needs

Standard CLI flags from `utils.sdr_common.make_skill_parser`, plus:

- `--transcript-file` — path to a JSON transcript (default `tests/skills/fixtures/sample_transcript.json`)

Upstream artifacts:

- `data/raw/sdr_profiles.csv` — used to calibrate coaching tone to the hire's experience level.
- A transcript JSON shaped as:

  ```json
  {
    "hire_id": "HIRE-001",
    "messages": [{"role": "sdr"|"prospect", "text": "..."}],
    "outcome": "meeting_booked" | "no_meeting",
    "call_context": "optional free-form context the manager attached"
  }
  ```

## How to use this skill

1. Point `--transcript-file` at a real or synthetic transcript.
2. Read the envelope. If `review_required=true`, `outputs.review_reasons` explains which thresholds tripped (low confidence, weighted total below 4, a single dimension below 3, or LLM arithmetic drift > 1 point from the server-recomputed total).
3. The rendered Markdown lives at `<run_dir>/04_coaching_note.md`.

## What the LLM receives

A system prompt instructing it to act as a senior SDR coach calibrated to the hire's experience level (entry → encouraging; mid → direct; senior → pointed). It is told to score against **Coaching Rubric v3.1**:

- `opening_and_framing` (weight 0.20)
- `discovery_quality` (weight 0.35)
- `objection_handling` (weight 0.25)
- `close_and_next_step` (weight 0.20)

Plus the rubric's common deductions (talking past prospect, pitch dumping, unapproved claims, skipping recap). Output is validated against a Pydantic `CoachingNote` schema:

- Each of the four dimensions: `{score: int 1-10, rationale: one sentence}`
- `weighted_total`: float 1-10 (LLM computes; **the skill re-computes server-side** and flags drift > 1 as a review reason)
- `what_worked`: 1-3 bullets
- `what_to_improve`: 1-3 bullets
- `language_alternatives`: exactly 2 concrete "replace X with Y" rewrites
- `confidence`: float 0-1

## Review triggers

`review_required = true` if any of:

- `confidence < 0.70`
- server-recomputed `weighted_total < 4.0` (below-bar performance per rubric)
- any single dimension scores below 3
- LLM-emitted `weighted_total` drifts more than 1 point from the server-recomputed value

All triggers that fired are surfaced in `outputs.review_reasons` (and in the markdown's "Why manager review is required" section).

## What it writes

- `<run_dir>/04_coaching_note.md` — sectioned Markdown (Overall weighted score, Dimension scores, What worked, What to improve, Language alternatives, optional review-reasons block).
- JSON envelope on stdout:
  - `status`: `"ok"` or `"needs_review"`
  - `next_action`: `"done"`
  - `confidence`, `review_required`, `artifact_refs=["04_coaching_note.md"]`
  - `outputs`: `{hire_id, weighted_total, llm_weighted_total, weighted_total_drift, dimension_scores, what_worked, what_to_improve, language_alternatives, review_reasons, outcome, retrieved_docs, sources}`

Errors: `hire_not_found`, `transcript_not_found`, `profiles_missing`.

## Example

```bash
uv run python skills/score-cold-call/scripts/score_cold_call.py \
  --hire-id HIRE-001 --workflow-run-id co-demo --step-id score-cold-call \
  --transcript-file tests/skills/fixtures/sample_transcript.json --json
```

For offline runs, set `MOCK_LLM_RESPONSE` to a JSON string matching `CoachingNote`.
