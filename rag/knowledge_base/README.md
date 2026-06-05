# Knowledge base — SDR onboarding (proprietary)

Twelve simulated internal documents the AI coworker can retrieve from at workflow execution time. The content is fabricated but plausible: policy codes, internal codenames, named owners, and specific numbers that an LLM could not invent from public training data — which is what makes retrieval testable.

This corpus is **separate** from `data/raw/` (the M02 hire/AE profile dataset). Do not conflate them.

## Documents

| # | File | One-line description |
|---|---|---|
| 1 | [onboarding_policy.md](onboarding_policy.md) | Policy SDR-OB-2024-03: required Trailhead modules and shadowing windows by experience level. POC Maya Reyes (People Ops). |
| 2 | [mentor_program_handbook.md](mentor_program_handbook.md) | TG Program v4.2: Trail Guide cadence, escalation rules, and satisfaction-survey schedule. Owner Devon Park. |
| 3 | [territory_definitions.md](territory_definitions.md) | How AMER-West, AMER-East, EMEA, and APAC are split. Edge cases: India→APAC, UAE→EMEA, Brazil→AMER-East. Effective January 2024. |
| 4 | [vertical_playbook_healthcare.md](vertical_playbook_healthcare.md) | Healthcare playbook (codename "Project Stethoscope"): HIPAA talking points, objections, Veeva positioning. |
| 5 | [vertical_playbook_fintech.md](vertical_playbook_fintech.md) | Fintech playbook (codename "Project Ledger"): SOC 2 talking points, core-banking integration patterns, regulatory acknowledgements. |
| 6 | [cold_call_quality_rubric.md](cold_call_quality_rubric.md) | Coaching Rubric v3.1: the 1-10 cold-call scale, four scored dimensions, and common deductions. |
| 7 | [quota_ramp_schedule.md](quota_ramp_schedule.md) | Ramp Schedule FY24-Q2: 25%/60%/100% standard ramp curve, plus mid/senior variants and relief triggers. |
| 8 | [tooling_access_checklist.md](tooling_access_checklist.md) | Ticket ACCESS-2024-NEWSDR: Day-1 tools, Gong on Day 3, Sales Navigator Week 2, ZoomInfo on manager approval. |
| 9 | [compensation_overview.md](compensation_overview.md) | FY2024 base bands by territory and level (e.g., AMER-West entry $65K + $25K variable), commission structure, accelerators. Confidential. |
| 10 | [escalation_paths.md](escalation_paths.md) | Where to take Day-1 IT problems, mentor conflicts, quota concerns, and crises (Crisis Line x4427). |
| 11 | [objection_handling_top10.md](objection_handling_top10.md) | Top ten cold-call objections with company-approved Acknowledge–Reframe–Redirect (ARR) responses. |
| 12 | [legal_messaging_constraints.md](legal_messaging_constraints.md) | Workflow LMG-2024: no specific revenue claims, no named-competitor comparisons, no forward-looking statements without approval. |

## How this corpus is used

The corpus is indexed by `rag/retrieval.py` and exposed to skills that need grounded context — most notably `skills/score-cold-call/` (which retrieves the rubric, ARR objection patterns, and LMG-2024 constraints when scoring a call). Indexing and retrieval are built in the next step.
