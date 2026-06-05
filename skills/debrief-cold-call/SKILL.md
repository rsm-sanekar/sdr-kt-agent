---
name: debrief-cold-call
description: Debrief a Cold Call Simulation conversation against Coaching Rubric v3.1 (four weighted dimensions plus what worked / improve / language alternatives). Consumes the simulation chat transcript and the persona id; produces the same CoachingNote shape as score-cold-call. Standalone — never chained.
---

# Debrief cold call

## Runtime modes

Invokable from a terminal, from the `/simulation/debrief` endpoint, or by an agent. Envelope reports `next_action="done"`.

## What the script needs

Standard CLI flags from `utils.sdr_common.make_skill_parser`, plus:

- `--messages-file` — required; path to a JSON array of `{role: "trainee"|"prospect", text: "..."}` objects
- `--persona-id` — optional; used to scope the system prompt's context ("the trainee practiced against persona X")

## What the LLM receives

A coach-shaped system prompt that:
- Quotes the persona name + role + vertical + personality for context
- Names **Coaching Rubric v3.1** with the four weighted dimensions and weights
- Lists the standard rubric deductions
- Reminds the model this is **practice** — lead with what worked, then specific actionable critique

The user prompt is the simulation transcript with `TRAINEE:` / `<PERSONA_NAME>:` role labels.

## Schema (Pydantic)

Same `CoachingNote` shape as `score-cold-call` — kept self-contained in this skill rather than imported across skills (each skill is independently invokable as a subprocess).

## Review triggers

`review_required = true` if any of:
- `confidence < 0.70`
- server-recomputed `weighted_total < 4.0`
- any single dimension scores below 3
- LLM-emitted `weighted_total` drifts > 1 point from the server-recomputed value

## What it writes

- `<run_dir>/01_simulation_debrief.md` — sectioned Markdown debrief.
- JSON envelope on stdout:
  - `status`: `"ok"` or `"needs_review"`
  - `next_action`: `"done"`
  - `confidence`, `review_required`, `artifact_refs=["01_simulation_debrief.md"]`
  - `outputs`: `{persona_id, persona_name, n_turns, weighted_total, llm_weighted_total, weighted_total_drift, dimension_scores, what_worked, what_to_improve, language_alternatives, review_reasons}`

Errors: `messages_file_missing`, `messages_file_invalid`, `empty_conversation`.

## Example

```bash
uv run python skills/debrief-cold-call/scripts/debrief_cold_call.py \
  --persona-id cfo-saas \
  --messages-file /tmp/sim-msgs.json \
  --workflow-run-id sim-demo --step-id debrief-cold-call \
  --out-dir data/working/simulation --json
```

For offline runs, set `MOCK_LLM_RESPONSE` to a JSON string matching `CoachingNote`.
