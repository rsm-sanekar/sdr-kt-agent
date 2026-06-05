---
name: answer-sdr-question
description: Use this skill to answer a free-form SDR question (cold-call tactics, policy lookups, ramp questions, etc.) by retrieving the most semantically-relevant chunks from the proprietary knowledge base and producing a short, citation-grounded answer with one concrete next step. Standalone Q&A — not part of the 4-step onboarding chain.
---

# Answer SDR question (AI Tutor)

## Runtime modes

Invokable from a terminal, from the FastAPI `/tutor/ask` endpoint, or by an agent. **Standalone** — this skill does not participate in the orchestrator's chain; its envelope's `next_action` is always `"done"`.

## What the script needs

Standard CLI flags from `utils.sdr_common.make_skill_parser`, plus:

- `--question` — the SDR's free-form question (required at the application layer; if empty the skill returns a `question_missing` error envelope).

Upstream artifacts required:

- `rag/knowledge_base/*.md` (the same 14 docs the chain uses)
- A populated ChromaDB collection at `data/chroma_db/` named `sdr_tutor_kb`. The skill calls `ensure_index()` on every invocation, which builds the collection on first run and is a no-op afterwards.

## How retrieval works

Free-form human questions need semantic match, not BM25 keyword overlap. So this skill uses [`rag/embeddings_retrieval.py`](../../rag/embeddings_retrieval.py) — ChromaDB persistent client + the default sentence-transformer embedding (`all-MiniLM-L6-v2`, no API key needed). Documents are chunked into ~300-word windows with 40-word overlap; the query is embedded and cosine-similarity is used as the relevance score.

The LLM chain steps (`generate-onboarding-plan`, `score-cold-call`) continue to use BM25 via [`rag/retrieval.py`](../../rag/retrieval.py). Both retrievers coexist over the same source KB — they do not interfere. `welcome-new-hire` is now a deterministic template-fill automation and uses no retriever.

## What the LLM receives

A system prompt instructing it to:

1. Answer using ONLY the numbered sources.
2. Cite inline with `[n]`.
3. Stay under 200 words.
4. End with one concrete next step the SDR can take today.
5. Say so explicitly (and recommend who to ask) when the sources don't contain the answer.

The user prompt carries the question and the top-5 retrieved chunks formatted as `[1] (source: doc.md, relevance: 0.82)\n<passage>`.

Output is validated against the Pydantic `TutorAnswer` schema:

- `answer` — the response with `[n]` citations (≥20 chars)
- `next_step` — one concrete action (≥5 chars)
- `confidence` — float 0-1

## Review and flagging triggers

`review_required=true` is forced when **any** of:

- the best retrieval cosine similarity is below `LOW_CONFIDENCE_THRESHOLD` (0.40) — `outputs.flagged=true`
- the model self-reported `confidence < 0.60`

A `flagged=true` answer is the AI being honest about its evidence quality *before* a human even looks. Approve / Reject in the UI feeds the loop described below.

## Envelope

- `status` — `"ok"` or `"needs_review"`
- `next_action` — always `"done"` (terminal — no chain handoff)
- `confidence` — model's self-reported confidence
- `review_required` — see flagging rules above
- `artifact_refs` — empty (no Markdown file is written; the answer lives in `outputs`)
- `outputs`:
  - `question` — the input question
  - `answer` — the cited response
  - `next_step` — one concrete action
  - `sources` — list of `{doc_name, passage, score}` (the top-5 retrieved chunks with the actual matched text and cosine similarity)
  - `confidence_score` — the best cosine similarity (separate from the LLM's `confidence`)
  - `flagged` — `true` when `confidence_score < 0.40`

Errors: `question_missing` (empty `--question`).

## Approval loop (separate from this skill)

The FastAPI server exposes:

- `POST /tutor/approve` — writes the (possibly edited) Q&A back to ChromaDB as a new chunk with `source="approved_qa"`. Closes the human-in-the-loop loop: an approved answer becomes future retrieved evidence.
- `POST /tutor/reject` — writes nothing to the KB; logs the question and rejected answer to `data/gap_tracker.json` as a gap for a human to fill.

Rejected answers **never** enter the KB.

## Example

```bash
uv run python skills/answer-sdr-question/scripts/answer_sdr_question.py \
  --question "How do I handle a price objection on a cold call?" --json
```

For offline / test runs, set `MOCK_LLM_RESPONSE` to a JSON string matching the `TutorAnswer` schema; the skill uses it verbatim instead of calling the LLM.
