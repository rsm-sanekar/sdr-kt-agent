# `score-cold-call`

Final step of the SDR onboarding workflow. LLM skill that scores a recorded (or synthetic) cold-call transcript and produces structured coaching feedback validated against a Pydantic `CoachingNote` schema (`what_worked`, `what_to_improve`, `language_alternatives`, `overall_score`, `confidence`). The hire's experience level from `data/raw/sdr_profiles.csv` is fed into the system prompt so entry hires get gentler, encouragement-forward feedback while senior hires get sharper, more tactical critique. Output is written to `<run_dir>/04_coaching_note.md`; the envelope reports `next_action="done"`. Review is flagged when the model's `confidence < 0.70` *or* `overall_score < 4`.

## Run

```bash
uv run python skills/score-cold-call/scripts/score_cold_call.py \
  --hire-id HIRE-001 --workflow-run-id wf-demo --step-id step4 \
  --transcript-file tests/skills/fixtures/sample_transcript.json --json
```

For offline testing, set `MOCK_LLM_RESPONSE` to skip the network call:

```bash
MOCK_LLM_RESPONSE='{"what_worked":["Clear opener and value proposition","Asked discovery question early"],"what_to_improve":["Could handle the budget objection more confidently"],"language_alternatives":["Replace \"just checking in\" with \"following up on our last conversation\"","Replace \"I think\" with \"based on what you shared\""],"overall_score":7,"confidence":0.85}' \
  uv run python skills/score-cold-call/scripts/score_cold_call.py \
    --hire-id HIRE-001 --workflow-run-id wf-demo --step-id step4 --json
```

Error codes: `hire_not_found` (unknown `--hire-id`), `transcript_not_found` (missing `--transcript-file`).
