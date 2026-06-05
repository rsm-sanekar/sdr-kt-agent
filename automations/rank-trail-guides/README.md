# `rank-trail-guides`

**Step 3 of the SDR onboarding workflow.** Deterministic, no LLM. Scores every AE in `data/raw/ae_profiles.csv` against the hire's profile in `data/raw/sdr_profiles.csv` and writes a top-N ranking to `<out_dir>/<workflow_run_id>/02_trail_guides.md`. Score is 0–100 with five components: territory match (30), vertical match (30), satisfaction (20), mentorship hours/week (10), and prior mentees capped at 10 (10). Ties break on `ae_id` for stable ordering. The output Markdown is a single ranked table showing the per-component breakdown so a reviewer can see *why* each AE landed where they did.

## Run

```bash
uv run python automations/rank-trail-guides/scripts/rank_trail_guides.py \
  --hire-id HIRE-001 \
  --workflow-run-id wf-demo \
  --step-id step2 \
  --top-n 5 \
  --json
```

Standard CLI flags plus `--top-n` (default `5`). Confidence buckets on the top-1 score: `>= 70` → `1.0`, `50–69` → `0.7`, `< 50` → `0.4`. When confidence falls below `0.60`, `review_required` flips to `True` and the envelope reports `status="needs_review"` (otherwise `"ok"`). Returns `next_action="welcome-new-hire"`, `artifact_refs=["02_trail_guides.md"]`, and `outputs={"hire_id", "top_ae_id", "top_score", "n_candidates_scored"}`. Unknown `hire_id` → `status="error"`, code `hire_not_found`.
