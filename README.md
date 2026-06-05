# SDR KT Onboarding Agent — Milestone 04 (Group 2)

An AI coworker that supports a new Salesforce SDR through the full
ramp: **pre-boarding** (a personalized plan, a ranked mentor match, a
drafted welcome email), **on-the-job learning** (an AI Tutor grounded in
proprietary docs, a cold-call simulator with a scored debrief),
**manager coaching** (a structured note drafted from a real call
transcript), a **certification gap analysis** that scores an SDR on a
five-dimension rubric and shows the evidence behind every score, and an
**onboarding debrief** that, after an SDR passes certification, captures
their feedback on the program (what worked, barriers, improvements) for
the manager and enablement team. Every AI output is gated by a
human approve / edit / reject / escalate decision; every decision is
logged.

**Team:** Anjali Roy, Shreya Anekar — MGT 449 GenAI for Business —
submitted June 4, 2026.

---

## What's in this repo

| Component | Path | What it does |
|---|---|---|
| 7 LLM skills | [skills/](skills/) | `generate-onboarding-plan`, `answer-sdr-question` (Tutor), `score-cold-call`, `simulate-cold-call`, `debrief-cold-call`, `generate-handoff-doc`, `score-certification` |
| 2 deterministic automations | [automations/](automations/) | `rank-trail-guides` (5-component mentor score), `welcome-new-hire` (template slot-fill) |
| 2 MCP servers | [mcp_servers/](mcp_servers/) | `sdr-onboarding-data` (3 resources) + `sdr-onboarding-tools` (3 callable tools), registered in [.mcp.json](.mcp.json) |
| RAG corpus | [rag/knowledge_base/](rag/knowledge_base/) | 16 internal Salesforce SDR docs (incl. gold-standard onboarding template, Trailhead module allow-list, certification rubric + question bank) + 7 scraped Wikipedia refs |
| Two retrievers | [rag/retrieval.py](rag/retrieval.py), [rag/embeddings_retrieval.py](rag/embeddings_retrieval.py) | BM25 keyword (chain skills); ChromaDB semantic (AI Tutor's free-form questions) |
| FastAPI orchestrator | [workflow_server.py](workflow_server.py) | Drives the pre-boarding chain + exposes endpoints for every standalone feature; persists decisions to `data/decision_log.json` |
| CLI orchestrator | [scripts/orchestrator.py](scripts/orchestrator.py) | Runs the 3-step pre-boarding chain end-to-end from the command line |
| Per-hire summaries | [data/raw/summaries/](data/raw/summaries/) | One Markdown file per hire, consumed by the onboarding planner |
| Synthetic SDR cohort | [data/sdr_records/](data/sdr_records/) | 7 SDRs with simulation transcripts, exam answers, coaching notes, cached gap analyses (powers Certification) |
| React UI | [ui/](ui/) | Role-aware (manager / trainee) — 9 screens, evidence panels with inline citations |
| Tests | [tests/](tests/) | 153 pytest tests offline via `MOCK_LLM_RESPONSE`; DeepEval Tutor suite (10 cases × 4 metrics) at [tests/eval_suite/](tests/eval_suite/) |

---

## The workflow — at a glance

Two halves:

1. **Pre-boarding chain** (3 steps, once per new hire):
   `generate-onboarding-plan` (LLM + BM25 RAG) → `rank-trail-guides`
   (deterministic) → `welcome-new-hire` (deterministic). Steps hand off
   via a shared JSON envelope and pause at a review gate when
   confidence is low.

2. **Standalone on-demand features** (used across the 12-week ramp, at
   certification, and at offboarding): AI Tutor, Coaching Notes,
   Cold-Call Simulation, **Certification Gap Analysis**, Onboarding Debrief.
   Each is invoked from its own UI tab and returns an envelope with
   `next_action="done"`.

Detailed handoff mechanics and the chain are in
[ai_process_design.pdf](ai_process_design.pdf).

---

## UI screens by role

| Role | Tab | What it does |
|---|---|---|
| Manager | Pre-boarding | Pick a hire, run the 3-step chain, review and approve/edit/reject at the gate |
| Manager | Coaching Notes | Paste a call transcript → per-dimension scored note → approve before it reaches the SDR |
| Manager | **Certification** | Roster of all SDRs with PASS / BORDERLINE / FAIL badges; click for 5-dim scores, quoted evidence, journey context, trainer decision panel |
| Manager | Debrief Reviews | Queue of SDR-submitted onboarding debriefs → full debrief (per-element feedback, barriers, improvements) → approve/edit/reject |
| Manager | Dashboard | Process metrics + recent decisions |
| Trainee | AI Tutor | Ask a question → cited answer → approve / reject (feedback re-enters ChromaDB) |
| Trainee | Cold Call Simulation | Pick a prospect persona → turn-by-turn cold call → scored debrief |
| Trainee | Onboarding Debrief | (Newly-certified SDR) pick your name, walk a 7-question debrief on your ramp, submit to your manager |

---

## RAG integration

A 16-document proprietary knowledge base in
[rag/knowledge_base/](rag/knowledge_base/) simulates the kind of
internal information a real Salesforce SDR onboarding program would
have — policy codes, internal codenames, named owners, ramp
percentages, dollar bands, legal-approval workflow IDs, certification
rubric bands. Each doc is fabricated but plausible, intentionally
containing details an LLM cannot invent from public training data.

**Two retrievers** over the same corpus:

- **BM25 keyword** ([rag/retrieval.py](rag/retrieval.py)) — used by the
  chain skills + certification scorer. Machine-generated queries,
  deterministic, no API key needed.
- **ChromaDB semantic** ([rag/embeddings_retrieval.py](rag/embeddings_retrieval.py))
  — used by the AI Tutor because it handles free-form human questions.
  Includes a write-back path so approved Q&A re-enters the index.

Both append top chunks to the system prompt and surface source doc
names in `envelope.outputs.retrieved_docs` for auditability.

---

## How to run

Install + tests:

```bash
uv sync
uv run pytest -q
```

Full app (API + UI) — the way to demo the M04 prototype:

```bash
# terminal 1 — FastAPI on http://localhost:8000
uv run python workflow_server.py

# terminal 2 — Vite on http://localhost:5173
cd ui && npm install && npm run dev
```

Open `http://localhost:5173`, pick a role from the navbar, walk the
tabs.

CLI orchestrator (pre-boarding chain end-to-end, offline):

```bash
MOCK_LLM_RESPONSE='{"summary":"...","weeks":[...],"subject":"Welcome aboard!","body":"...","confidence":0.92}' \
  uv run python scripts/orchestrator.py --hire-id HIRE-001
```

Re-seed the synthetic certification cohort (idempotent):

```bash
uv run python skills/score-certification/scripts/seed_synthetic_cohort.py
```

Re-run the DeepEval Tutor suite:

```bash
uv run --env-file .env python -m tests.eval_suite.test_tutor_quality
```

---

## Milestone 04 deliverables

| Deliverable | File |
|---|---|
| Final process redesign (diagram + 1–2 page explanation) | [ai_process_design.pdf](ai_process_design.pdf) ([source](ai_process_design.qmd)) |
| Human review + control plan | [human_review_plan.md](human_review_plan.md) |
| Evidence + source use | [evidence_and_sources.md](evidence_and_sources.md) |
| Time, cost + quality reasoning | [estimates.md](estimates.md) |
| Face-validity check | [face_validity.md](face_validity.md) |
| Predicted failure cases | [failure_cases.md](failure_cases.md) |
| DeepEval test report (6-run before/after) | [test_report.md](test_report.md) |
| Final presentation deck (PDF) | [presentation_slides/SDR_Onboarding_AI_Coworker.pdf](presentation_slides/SDR_Onboarding_AI_Coworker.pdf) |
| Presentation source (Quarto / reveal.js) | [presentation_slides/SDR_Onboarding_AI_Coworker.qmd](presentation_slides/SDR_Onboarding_AI_Coworker.qmd) (+ `custom.scss`; renders to HTML or PDF) |

---

## Repository layout

```
.
├── README.md                       # this file
├── ai_process_design.{qmd,pdf}     # workflow diagram + 1-2 page explanation
├── human_review_plan.md            # 8-row review plan with 5 explicit gates
├── evidence_and_sources.md         # 5 questions answered
├── estimates.md                    # 8-row per-step table + summary + cost
├── face_validity.md                # 4 questions + 4 anchors
├── failure_cases.md                # 8 failure cases, 4 exercised by tests
├── test_report.md                  # DeepEval 6-run before/after analysis
├── presentation_slides/            # SDR_Onboarding_AI_Coworker.pdf + .qmd + custom.scss
├── .mcp.json                       # MCP server registration
├── workflow_server.py              # FastAPI orchestrator
├── utils/                          # sdr_common.py, connect.py
├── automations/                    # rank-trail-guides, welcome-new-hire
├── skills/                         # 7 LLM skills
├── mcp_servers/                    # FastMCP data + tools servers
├── rag/
│   ├── knowledge_base/             # 16 docs + scraped/
│   ├── retrieval.py                # BM25
│   └── embeddings_retrieval.py     # ChromaDB
├── scripts/                        # CLI orchestrator + glue
├── ui/                             # React + Vite + Tailwind (role toggle)
├── tests/                          # 153 tests + DeepEval eval_suite
└── data/
    ├── raw/                        # sdr_profiles, ae_profiles, summaries, sim_personas
    ├── sdr_records/                # 7-SDR synthetic cert cohort
    ├── working/                    # per-run envelopes + artifacts
    ├── decision_log.json           # every approve/edit/reject/escalate
    └── gap_tracker.json            # rolling counts feeding the dashboard
```

---

## Milestone 04 status

- [x] Final process redesign (PDF + 1–2 page explanation)
- [x] Human review + control plan (8 rows, 5 explicit approval gates)
- [x] UI with 9 screens (start, AI work, evidence, review, dashboard, 4 more)
- [x] Evidence + source use documented
- [x] Time, cost + quality reasoning (assumptions labeled, ranges used)
- [x] Face-validity check (4 questions, 4 anchors)
- [x] Predicted failure cases (8 rows, 4 tied to DeepEval cases)
- [x] DeepEval suite — 10 cases × 4 metrics × 6 runs (3 before/3 after)
- [x] Before/after comparison — prompt tighten lifted mean from 21.3 to 23.3 with variance tightening 3 → 1
- [x] Final presentation deck (12 slides)
- [x] 153 pytest passing, ruff clean, UI builds clean
