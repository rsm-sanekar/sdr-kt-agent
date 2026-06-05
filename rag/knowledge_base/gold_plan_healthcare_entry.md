---
title: Gold-standard onboarding plan — healthcare / entry-level
category: Sales enablement
template_version: GOLD-OB-HC-ENTRY-FY24-Q2
last_reviewed: 2024-09-15
owner: Sales Enablement — Priya Subramanian (Coaching Lead)
audience: SDR onboarding planner
---

# Gold-standard plan: healthcare vertical, entry experience

This is the **exemplar shape** the SDR onboarding planner should adapt for an entry-level hire selling into the healthcare vertical. The planner reads the hire's personalized `summary.md`, picks the closest gold-standard, and adapts it (replacing or skipping modules the hire has already mastered, compressing or expanding weeks based on prior-role context).

The exemplar below assumes a hire with zero prior Salesforce exposure, no prior pharma or provider-side experience, and no completed Trailhead modules. **Adapt aggressively** when the hire's summary contradicts these assumptions.

## Hiring-manager intent

- Get the hire from "first day badge" to "first booked discovery call" inside 30 days without skipping HIPAA grounding.
- Lean shadowing-heavy in weeks 1-2 (per Policy SDR-OB-2024-03 — entry hires need 25 observed calls before live dials).
- Build vertical fluency early so cold-call mechanics in week 3 are anchored to real provider/payer language.

## Exemplar weekly structure

### Week 1 — Salesforce + EMEA territory baseline
Theme: "Salesforce navigation + day-1 tooling"
- TRAIL-CRM-101 (Salesforce CRM Basics) — required baseline, no shortcut available
- TRAIL-OUT-101 (Outreach Foundations) — sets up the sequence-builder UX before cold-call week
- TRAIL-TERR-EMEA-101 (EMEA Outreach + GDPR Awareness) — only when hire is on EMEA territory; swap for the matching territory module otherwise
- Activities: shadow 8 discovery calls (Day-2 through Day-5), complete Day-1 tooling checklist from Ticket ACCESS-2024-NEWSDR

### Week 2 — Healthcare vertical deep dive
Theme: "Provider and payer fluency before live dial"
- TRAIL-VERT-HC-101 (HIPAA-Aware Selling) — non-negotiable; legal team flags reps who skip this in QA review
- TRAIL-VERT-HC-201 (Healthcare Buyer Personas — Payer vs Provider) — promote earlier (normally a mid-level module) when hire shows prior healthcare/pharma context
- TRAIL-DISC-101 (Discovery Calls I) — overlaps thematically; pair with vertical module so discovery questions land in healthcare language
- Activities: shadow 8 more discovery calls (focus on payer-side conversations), submit shadow log to Trail Guide for review

### Week 3 — Cold-call mechanics
Theme: "Make your first warm outbound under supervision"
- TRAIL-COLD-101 (Cold Call Mechanics) — required
- TRAIL-OBJ-101 (Objection Handling Patterns) — pairs with the ARR pattern from `objection_handling_top10.md`
- TRAIL-PROS-101 (Prospecting 101) — required; sequence-builder usage
- Activities: 5 supervised cold calls with Trail Guide on the line, Friday review of recordings against Coaching Rubric v3.1

### Week 4 — Independent dial + CRM hygiene
Theme: "Earn the seat for solo outbound"
- TRAIL-CRM-HYG-101 (Post-Call CRM Hygiene) — entry-level capstone for week 4
- Activities: 20 solo cold dials across the week, 3 booked discovery calls target (per ramp month 1), Friday calibration call with manager + Trail Guide

## Adapt-not-copy guidance for the planner

The planner **must not** emit this template verbatim. Apply at least these adaptations:

1. **Read the hire's `summary.md`** for already-completed Trailhead modules. Skip them and note each in `skip_rationale`.
2. **If the hire has prior healthcare/pharma sales experience** (e.g., ex-pharma rep, ex-Medtronic, ex-Veeva), demote TRAIL-VERT-HC-101 to a refresher and promote TRAIL-VERT-HC-201 into week 1; free up week 2 for shadow rotations on enterprise-provider calls instead.
3. **Match the territory module** to the actual `territory` field — swap TRAIL-TERR-EMEA-101 for the AMER/APAC equivalent when applicable.
4. **Mention the hire by first name** in the plan summary; reference one concrete fact from their prior role.

## Confidence calibration

- Output `confidence ≥ 0.85` only when (a) summary.md was loaded, (b) at least one personalization decision is justified in the summary string, and (c) every module emitted is in the allow-list.
- Output `confidence ≤ 0.65` when summary.md was missing (fallback to CSV row only) — this routes the plan through human review per the standard 0.70 threshold.
