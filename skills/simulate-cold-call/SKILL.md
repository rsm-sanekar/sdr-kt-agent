---
name: simulate-cold-call
description: Role-play one turn of a cold-call prospect persona for the trainee Cold Call Simulation feature. Loads the persona from data/raw/sim_personas.json, replays the conversation history, and returns the next prospect message. Stateless — the UI maintains the running message log.
---

# Simulate cold call

## Runtime modes

Invokable from a terminal, from the `/simulation/turn` endpoint, or by an agent. The skill is **stateless** — every turn replays the entire conversation history that the UI POSTs. No session persistence on disk.

## What the script needs

Standard CLI flags from `utils.sdr_common.make_skill_parser`, plus:

- `--persona-id` — required; one of the ids in `data/raw/sim_personas.json`
- `--messages-file` — required; path to a JSON array of `{role: "trainee"|"prospect", text: "..."}` objects

`--hire-id` is **not used**. The trainee identity is implicit at the UI level.

## What the LLM receives

A persona-shaped system prompt:
- Names the persona, role, company, vertical
- Quotes the persona's personality block verbatim
- Lists the persona's `top_objections` as a "use these when fitting" library
- Hard rules: stay in character, no coaching the trainee, 2-4 sentence responses, push back on vague pitches, never break the fourth wall

The user prompt is the full conversation transcript with role labels (`TRAINEE:` / `<PERSONA_NAME>:`) plus an explicit "respond as the prospect" cue.

## Schema (Pydantic)

`ProspectTurn`:
- `prospect_response`: 2-4 sentence message as the prospect
- `suggested_objection_used`: the verbatim objection string from the persona's `top_objections` list (or `null` if no objection raised)
- `confidence`: float 0-1 — Claude's stay-in-character confidence

## What it writes

- **No artifact file** (stateless turn-driver).
- JSON envelope on stdout:
  - `status`: `"ok"` on success
  - `next_action`: `"done"`
  - `confidence`, `review_required: false`, `artifact_refs: []`
  - `outputs`: `{persona_id, persona_name, prospect_response, suggested_objection_used, n_messages_in}`

Errors: `persona_id_missing`, `persona_not_found`, `messages_file_missing`, `messages_file_invalid`.

## Example

```bash
echo '[{"role":"trainee","text":"Hi, this is Sam from Salesforce."}]' > /tmp/msgs.json

uv run python skills/simulate-cold-call/scripts/simulate_cold_call.py \
  --persona-id cfo-saas \
  --messages-file /tmp/msgs.json \
  --workflow-run-id sim-demo --step-id simulate-cold-call --json
```

For offline runs, set `MOCK_LLM_RESPONSE` to a JSON string matching `ProspectTurn`.
