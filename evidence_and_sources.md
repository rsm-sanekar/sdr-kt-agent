# Evidence and Source Use

The AI coworker never just returns an answer. Every LLM step retrieves
from a proprietary knowledge base, attaches the passages it used, and
surfaces them to the user so the output can be inspected rather than
trusted blindly. This document answers the five required questions.

## 1. What data does the AI use?

Structured inputs live under `data/`:

- **[data/raw/sdr_profiles.csv](data/raw/sdr_profiles.csv)** — new-hire
  records (id, name, experience level, assigned vertical, territory,
  tenure). Read by the onboarding planner, the welcome-email
  automation, the coaching scorer (to calibrate tone), and the
  Onboarding Debrief trainee form (to auto-fill territory / vertical /
  experience when the SDR picks their own name).
- **[data/raw/ae_profiles.csv](data/raw/ae_profiles.csv)** — candidate
  mentors, scored by the Trail Guide ranking automation.
- [`data/raw/summaries/HIRE-*.md`](data/raw/summaries/) — one
  per-hire summary, consumed by the onboarding planner to personalize
  the plan.
- **[data/raw/sim_personas.json](data/raw/sim_personas.json)** —
  prospect personas the cold-call simulator role-plays.
- **[data/sdr_records/SDR-001..007/](data/sdr_records/)** — a synthetic
  cohort of seven SDRs with simulation transcripts, certification exam
  answers, coaching notes, and cached gap analyses. Read by the
  certification feature; produced (idempotently) by
  `skills/score-certification/scripts/seed_synthetic_cohort.py`.
- **Call transcripts and debrief answers supplied at runtime**
  by the user (pasted into the Coaching Notes screen, typed into the
  Onboarding Debrief screen).

Operational data also accumulates:

- **[data/decision_log.json](data/decision_log.json)** — every
  approve / edit / reject / escalate decision, tagged with `feature` so
  the dashboard can group counts. Certification decisions get
  `feature="certification"`.
- **[data/gap_tracker.json](data/gap_tracker.json)** — rolling counts
  for the dashboard's metric tiles.

## 2. What documents does the AI use?

A 16-document simulated-proprietary knowledge base in
[rag/knowledge_base/](rag/knowledge_base/), written to contain details
an LLM cannot invent from public training data — policy codes, named
owners, ramp percentages, dollar bands, legal-approval workflow IDs,
certification rubric bands:

`onboarding_policy.md`, `quota_ramp_schedule.md`,
`objection_handling_top10.md`, `cold_call_quality_rubric.md`,
`escalation_paths.md`, `legal_messaging_constraints.md`,
`compensation_overview.md`, `territory_definitions.md`,
`mentor_program_handbook.md`, `tooling_access_checklist.md`,
`trailhead_module_catalog.md`, `gold_plan_healthcare_entry.md`,
`vertical_playbook_healthcare.md`, `vertical_playbook_fintech.md`,
**`certification_rubric.md`** (5 dimensions × pass/borderline/fail
bands with common gaps and coaching actions), **`certification_questions.md`**
(5 canonical exam questions, one per rubric dimension).

A `rag/knowledge_base/scraped/` folder also holds 7 public reference
docs (Wikipedia articles on cold calling, CRM, lead generation, the
sales process, etc.) collected by the scraper as background context.

## 3. What tools or Python functions does the AI use?

- **Skills (7):** `generate-onboarding-plan`, `answer-sdr-question`
  (tutor), `score-cold-call`, `simulate-cold-call`, `debrief-cold-call`,
  `generate-handoff-doc`, **`score-certification`** (gap analysis
  against the 5-dimension rubric). Each is a CLI script that emits a
  JSON envelope.
- **Automations (2, no GenAI):** `rank_trail_guides.py` (deterministic
  5-component mentor score) and `welcome_new_hire.py` (template
  slot-fill for the welcome email).
- **Retrieval (2):** [rag/retrieval.py](rag/retrieval.py) is BM25
  keyword retrieval used by the chain skills + certification scorer
  (machine-generated queries, deterministic, offline);
  [rag/embeddings_retrieval.py](rag/embeddings_retrieval.py) is
  embedding-based semantic retrieval over ChromaDB used by the AI Tutor
  for free-form human questions, with a write-back path so approved
  Q&A re-enters the index.
- **MCP servers (2):** [mcp_servers/data_server.py](mcp_servers/data_server.py)
  exposes 3 read-only resources (`sdr-profiles://all`,
  `sdr-profiles://{hire_id}`, `ae-profiles://all`);
  [mcp_servers/tools_server.py](mcp_servers/tools_server.py) exposes
  3 callable tools (`invoke_onboarding_plan`,
  `invoke_trail_guide_ranking`, `preview_envelope_schema`).
- **Orchestrator:** [workflow_server.py](workflow_server.py) chains
  pre-boarding steps by following each envelope's `next_action`,
  exposes endpoints for every standalone feature, persists decisions.

## 4. How does the user see the evidence?

The UI has a dedicated Evidence presentation, not a dump at the bottom
of the page. Every LLM skill returns its sources in a consistent shape
(`[{ doc_name, passage, score, weak }]`) and the front end renders
them two ways linked together:

- **`EvidencePanel`** shows one numbered pill per source. Clicking a
  pill expands the full retrieved passage and its match score, so the
  user can read what the AI actually saw.
- **`InlineCitations`** turns the `[n]` markers inside an answer into
  clickable pills; clicking one opens the matching source in the
  panel. This lets the user trace any sentence in a tutor answer back
  to the exact passage that supports it.

For coaching notes, the evidence is the score itself:
`ScoreBreakdown` and `ScoreBadge` show the per-dimension rubric scores
beside the drafted note, with the source transcript available for
comparison.

For certification, every per-dimension score card shows three things
side-by-side: the 1–10 score with its band color, a verbatim quote
from the SDR's own artifact (simulation transcript or exam answer)
that the LLM cited as evidence, and the rubric-derived gap-to-close +
coaching action. The `EvidencePanel` below the cards renders the
retrieved rubric passages with their match scores, and the raw
artifact MDs (transcripts, exam, coaching notes) are expandable inline
so the trainer can read the underlying text without leaving the page.

The plan, tutor, and certification envelopes all carry retrieved
document names in `outputs.retrieved_docs`, so the reviewer can tell
at a glance whether the evidence supports the output before approving.

## 5. What happens if the evidence is missing, weak, or conflicting?

The system flags weak evidence rather than hide it:

- **Weak match.** Each source carries a `weak` flag, and a retrieval
  whose best similarity score falls below the low-confidence threshold
  sets `flagged: true` on the envelope. The `EvidencePanel` marks weak
  sources visibly instead of presenting them as solid.
- **Low confidence blocks auto-completion.** When a step is flagged or
  its own reported confidence is below 0.60, the envelope sets
  `review_required: true`. In the pre-boarding chain this pauses the
  run at the review gate so a manager must approve, edit, reject, or
  escalate before anything proceeds; nothing low-confidence reaches an
  SDR unreviewed.
- **No authoritative source.** The tutor is instructed to answer using
  only the numbered sources and to cite them inline; when retrieval is
  weak it flags the answer for review rather than presenting an
  unsupported claim. The tightened prompt requires the tutor to cite
  at least one `[n]` even when refusing, so the reviewer can see what
  was checked. The Faithfulness check in the DeepEval suite verifies
  the tutor either stays within its sources or declines.
- **Conflicting sources.** The system does not silently pick a winner.
  It surfaces every retrieved passage in the `EvidencePanel` and
  routes the decision to the human at the review gate, who resolves
  the conflict and records the decision in the log.
- **Verdict drift on certification.** When the LLM's self-reported
  band disagrees with the server-side recompute from the dimension
  scores, the recompute wins; the mismatch is appended to
  `review_reasons` so the trainer is told *why* the case is flagged.
