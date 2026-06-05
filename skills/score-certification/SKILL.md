---
name: score-certification
description: Run a 5-dimension certification gap analysis for an SDR from their persisted journey artifacts (simulation transcripts + certification exam Q&A). Scores against rag/knowledge_base/certification_rubric.md (Decision Gate 1 rubric) using RAG. Cached per-SDR at data/sdr_records/<sdr_id>/gap_analysis.json so the manager's certification roster loads instantly. The AI recommendation is advisory — the trainer makes the final pass/fail call.
---

# Score certification

## Runtime modes

Invokable from a terminal, from the `/certification/sdr/{sdr_id}/analyze` endpoint, or by an agent. Envelope reports `next_action="done"` — standalone skill, not part of any chain.

## What the script needs

Standard CLI flags from `utils.sdr_common.make_skill_parser`, plus:

- `--sdr-id` — required. Resolves to `data/sdr_records/<sdr_id>.json`.

Upstream artifacts (read by the skill):

- `data/sdr_records/<sdr_id>.json` — the SDR's persistent index record. Must contain at least one `simulation` event (with `transcript_file`) and one `exam` event (with `qa_file`).
- The MD artifact files referenced from `simulation` and `exam` events. Paths are relative to `data/sdr_records/`.

Coaching notes and tutor_activity events are **deliberately ignored** at scoring time. They surface in the UI as supporting context, never as scoring inputs.

## How to use this skill

1. Ensure `data/sdr_records/<sdr_id>.json` exists with at least one `simulation` and one `exam` event. The seed script `seed_synthetic_cohort.py` creates a 7-SDR demo cohort.
2. Run the skill. It RAG-retrieves the rubric, scores 5 dimensions, recomputes the overall recommendation server-side, writes the rendered Markdown to `<run_dir>/01_certification_gap_analysis.md`, and **caches the full envelope** at `data/sdr_records/<sdr_id>/gap_analysis.json` so the roster endpoint can read it without re-running the LLM.
3. If `review_required=true`, `outputs.review_reasons` explains which gates tripped. The trainer reviews and makes the final decision via `POST /certification/decide`.

## What the LLM receives

A system prompt instructing it to act as a senior SDR coach grading the candidate against **certification_rubric.md**. The rubric's full text is appended via RAG retrieval, and the five dimensions + scoring bands (7+/5-6/≤4) are inlined verbatim.

Output is validated against a Pydantic `CertificationGapAnalysis` schema:

- Five dimensions, each `{score: int 1-10, evidence_quote: str, rationale: str, gap_to_close: str, coaching_action: str, verdict: pass|borderline|fail}`:
  - `product_knowledge_accuracy`
  - `objection_handling` (Defuse, Discover, Deliver)
  - `meddic_application`
  - `salesforce_value_messaging`
  - `discovery_and_questioning`
- `overall_recommendation`: PASS | BORDERLINE | FAIL (LLM emits; **server recomputes** and uses the computed value as the source of truth — drift is flagged as a review reason)
- `overall_rationale`: short narrative
- `confidence`: float 0-1

## Server-side recompute (band logic)

```
any dim score <= 4   → overall = FAIL
any dim score in 5-6 → overall = BORDERLINE
all dim scores >= 7  → overall = PASS
```

The skill **also recomputes per-dimension `verdict`** from the score (≥7 pass, 5-6 borderline, ≤4 fail) and overwrites the LLM's value defensively.

## Review triggers

`review_required = true` if any of:

- Computed `overall_recommendation` != "PASS" (every non-PASS goes to trainer review)
- `confidence < 0.65`
- LLM `overall_recommendation` differs from the server-computed one (drift)

All triggers that fired are surfaced in `outputs.review_reasons`.

## What it writes

- `<run_dir>/01_certification_gap_analysis.md` — sectioned Markdown (overall verdict banner, per-dimension table with score / evidence / gap / coaching action, retrieved-doc list, optional review-reasons block).
- `data/sdr_records/<sdr_id>/gap_analysis.json` — cached envelope. The roster endpoint reads this directly; `analyze` endpoint overwrites it.
- JSON envelope on stdout:
  - `status`: `"ok"` or `"needs_review"`
  - `next_action`: `"done"`
  - `confidence`, `review_required`, `artifact_refs=["01_certification_gap_analysis.md"]`
  - `outputs`: `{sdr_id, sdr_name, overall_recommendation, overall_rationale, weakest_dimension, dimension_findings, review_reasons, retrieved_docs, sources}`

Errors: `sdr_not_found`, `sdr_record_invalid`, `missing_required_artifacts`.

## Example

```bash
uv run python skills/score-certification/scripts/score_certification.py \
  --sdr-id SDR-001 --workflow-run-id cert-SDR-001 --step-id score-certification \
  --json
```

For offline runs, set `MOCK_LLM_RESPONSE` to a JSON string matching `CertificationGapAnalysis`. The cached `gap_analysis.json` is overwritten on every run; cohort seed script uses this mode.
