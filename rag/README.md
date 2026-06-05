# Proprietary Knowledge Base + Retrieval

## What's in the KB

12 internal documents simulating Salesforce SDR onboarding context the LLM cannot know from training data:

| # | File | One-line description |
|---|---|---|
| 1 | [knowledge_base/onboarding_policy.md](knowledge_base/onboarding_policy.md) | Policy SDR-OB-2024-03: required Trailhead modules and shadowing windows by experience level. POC Maya Reyes (People Ops). |
| 2 | [knowledge_base/mentor_program_handbook.md](knowledge_base/mentor_program_handbook.md) | TG Program v4.2: Trail Guide cadence, escalation rules, and satisfaction-survey schedule. Owner Devon Park. |
| 3 | [knowledge_base/territory_definitions.md](knowledge_base/territory_definitions.md) | How AMER-West, AMER-East, EMEA, and APAC are split. Edge cases: India→APAC, UAE→EMEA, Brazil→AMER-East. |
| 4 | [knowledge_base/vertical_playbook_healthcare.md](knowledge_base/vertical_playbook_healthcare.md) | Healthcare playbook (codename "Project Stethoscope"): HIPAA talking points, objections, Veeva positioning. |
| 5 | [knowledge_base/vertical_playbook_fintech.md](knowledge_base/vertical_playbook_fintech.md) | Fintech playbook (codename "Project Ledger"): SOC 2 talking points, core-banking integration patterns. |
| 6 | [knowledge_base/cold_call_quality_rubric.md](knowledge_base/cold_call_quality_rubric.md) | Coaching Rubric v3.1: the 1-10 cold-call scale, four scored dimensions, common deductions. |
| 7 | [knowledge_base/quota_ramp_schedule.md](knowledge_base/quota_ramp_schedule.md) | Ramp Schedule FY24-Q2: 25%/60%/100% standard ramp curve, mid/senior variants, relief triggers. |
| 8 | [knowledge_base/tooling_access_checklist.md](knowledge_base/tooling_access_checklist.md) | Ticket ACCESS-2024-NEWSDR: Day-1 tools, Gong on Day 3, Sales Navigator Week 2, ZoomInfo on approval. |
| 9 | [knowledge_base/compensation_overview.md](knowledge_base/compensation_overview.md) | FY2024 base bands by territory and level, commission structure, accelerators. Confidential. |
| 10 | [knowledge_base/escalation_paths.md](knowledge_base/escalation_paths.md) | Where to take Day-1 IT problems, mentor conflicts, quota concerns, and crises (Crisis Line x4427). |
| 11 | [knowledge_base/objection_handling_top10.md](knowledge_base/objection_handling_top10.md) | Top ten cold-call objections with company-approved Acknowledge–Reframe–Redirect (ARR) responses. |
| 12 | [knowledge_base/legal_messaging_constraints.md](knowledge_base/legal_messaging_constraints.md) | Workflow LMG-2024: no specific revenue claims, no named-competitor comparisons, no forward-looking statements. |

## Why a separate corpus

This corpus is intentionally distinct from [data/raw/](../data/raw/). The M02 CSVs (`sdr_profiles.csv`, `ae_profiles.csv`) are the **operational data** the workflow processes — the SDR and AE catalog the steps read and join against. The RAG corpus is **proprietary knowledge** an employee would need to *understand* the work — internal policies, vertical playbooks, coaching rubrics, legal constraints. RAG's pedagogical point is to teach the model facts it cannot otherwise know: policy codes, named owners, internal codenames, ramp percentages, specific dollar bands. Mixing the two would defeat the exercise.

## Retrieval

[`retrieval.py`](retrieval.py) exposes a small API:

```python
from rag.retrieval import build_index, retrieve

index = build_index()                            # parses every .md in knowledge_base/
results = retrieve("HIPAA compliance", index, top_k=3)
for c in results:
    print(c.doc_name, c.chunk_id, c.score, c.text[:80])
```

Documents are split on blank lines into paragraph-level chunks (YAML frontmatter stripped first). Tokens are lowercased, punctuation-stripped, and filtered against a small built-in stopword list. Scoring uses **BM25** via [`rank-bm25`](https://pypi.org/project/rank-bm25/).

We chose keyword/BM25 over embeddings because the corpus is small (12 docs, ~70 chunks), the queries are short and lexical (territory names, doc codes, vertical names), and BM25 is **fast, deterministic, offline-testable, and needs no API key**. An embedding-based retriever can be swapped in later behind the same `build_index` / `retrieve` interface without changing any caller.

## Which skills use RAG

| Skill | Query template | What it retrieves |
|---|---|---|
| [generate-onboarding-plan](../skills/generate-onboarding-plan) | `"onboarding {vertical} territory {territory} experience {level}"` | Onboarding policy, mentor program, vertical playbook |
| [score-cold-call](../skills/score-cold-call) | `"cold call coaching {vertical} {outcome}"` | Coaching rubric, vertical playbook, objection handling |
| [answer-sdr-question](../skills/answer-sdr-question) | the trainee's question, verbatim | Whatever's relevant to the question (hybrid BM25 + cosine, separate retriever) |

Each LLM skill builds the query from its own inputs, retrieves the top 3 chunks, appends them to the LLM system prompt under a "Reference internal documents" heading, and surfaces the source doc names in the envelope's `outputs.retrieved_docs` for downstream auditability. The third pre-boarding step — `welcome-new-hire` — is a deterministic template-fill automation and intentionally does **not** use RAG.

## Running retrieval manually

```bash
uv run python rag/retrieval.py "your query here"
```

Prints the top 3 chunks (score, doc name, chunk id, snippet) for the query. Useful for sanity-checking what the skills will see before an LLM call.

## Tests

```bash
uv run pytest tests/rag/
```

Eight tests cover index construction (all 12 docs found, README excluded, multiple chunks per doc), retrieval correctness (`quota_ramp_schedule.md` tops the quota-ramp query; healthcare playbook surfaces for HIPAA queries), nonsense-query fallback (returns top_k without crashing), `top_k` honoring, and determinism (same query → identical results across runs).
