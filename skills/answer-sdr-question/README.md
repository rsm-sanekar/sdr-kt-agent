# `answer-sdr-question` (AI Tutor)

Standalone LLM skill that answers a free-form SDR question by retrieving the most semantically-relevant chunks from the proprietary knowledge base (ChromaDB cosine similarity over the same 14 docs the chain uses) and producing a citation-grounded answer with one concrete next step.

**Not part of the 4-step onboarding chain.** Its envelope reports `next_action="done"` — the orchestrator does not invoke it.

## Run

```bash
uv run python skills/answer-sdr-question/scripts/answer_sdr_question.py \
  --question "How do I handle a price objection on a cold call?" --json
```

For offline testing, set `MOCK_LLM_RESPONSE`:

```bash
MOCK_LLM_RESPONSE='{"answer":"Use the Acknowledge-Reframe-Redirect (ARR) pattern from [1]. Acknowledge the concern, reframe to value, redirect to a discovery question.","next_step":"Try the ARR pattern on your next 3 cold calls and review the recordings with your Trail Guide.","confidence":0.85}' \
  uv run python skills/answer-sdr-question/scripts/answer_sdr_question.py \
    --question "How do I handle a price objection?" --json
```

## Review triggers

`review_required=true` is set when either:

- the best retrieval cosine similarity is below `0.40` → `outputs.flagged=true` (the AI is admitting weak evidence before a human looks)
- the model's self-reported `confidence < 0.60`

## Approval loop

Used via `POST /tutor/approve` and `POST /tutor/reject` on the FastAPI server:

- **Approve** writes the (possibly edited) Q&A back to ChromaDB as `source="approved_qa"` so future questions retrieve it.
- **Reject** logs the question + rejected answer to `data/gap_tracker.json`. **Never** writes to the KB.

## See also

- [SKILL.md](SKILL.md) — full skill contract.
- [`rag/embeddings_retrieval.py`](../../rag/embeddings_retrieval.py) — ChromaDB retriever this skill uses (separate from the BM25 retriever the chain uses).
