# `welcome-new-hire`

**Final step of the SDR pre-boarding chain.** Deterministic, no LLM. Renders a personalized welcome email by slot-filling the hire's profile (`data/raw/sdr_profiles.csv`) and the top-ranked mentor parsed out of `<run_dir>/02_trail_guides.md` into a four-paragraph template. The third paragraph is chosen from one of three per-experience-level variants (`entry` / `mid` / `senior`); unknown levels fall back to `mid`. Writes the rendered email to `<run_dir>/03_welcome_email.md`. The chain auto-completes past this step — the manager can still view and edit the artifact from the run view.

## Run

```bash
uv run python automations/welcome-new-hire/scripts/welcome_new_hire.py \
  --hire-id HIRE-001 --workflow-run-id wf-demo --step-id step3 --json
```

Standard CLI flags. Returns `status="ok"`, `next_action="done"`, `confidence=1.0`, `review_required=False`, `artifact_refs=["03_welcome_email.md"]`, and `outputs={"hire_id", "mentor_ae_id", "mentor_name", "subject", "experience_level"}`. Error codes: `hire_not_found` (unknown `--hire-id`), `mentor_ranking_not_found` (`rank-trail-guides` hasn't run for this `workflow_run_id`), `mentor_ranking_unparseable` (`02_trail_guides.md` exists but the rank-1 row can't be parsed), `profiles_missing` (`data/raw/sdr_profiles.csv` not present).
