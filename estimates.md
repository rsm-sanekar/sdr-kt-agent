# Time, Cost, and Quality Reasoning

All figures below are **reasoned assumptions**, not measured company
data. The "current" column is anchored to the Milestone 01 baseline
metrics and the per-step times in the M01 process documentation; the
"AI-supported" column is our estimate of the same work once the
prototype assists it. Ranges are used wherever uncertainty is high.

---

## Per-step time estimate

Units differ by step and are stated per row. The first three rows are
the once-per-hire pre-boarding chain; the last five are recurring
features used across the 12-week ramp.

| Process step | Current time per case | AI-supported time per case | Why might time change? | Confidence in estimate |
|---|---:|---:|---|---|
| Build pre-boarding onboarding plan *(per hire)* | 90–150 min | 10–20 min | M01 US1 put manual customization near two hours per hire; the AI drafts from a template plus RAG and the human spot-checks. | Medium |
| Match a Trail Guide mentor *(per hire)* | 20–40 min | 5–10 min | M01 Step 3 was ~30 min of manager judgment; a deterministic ranked table replaces the search and the manager confirms. | Medium-High |
| Draft welcome email *(per hire)* | 15–30 min | 3–8 min | Written from scratch today; the AI slot-fills a template and the manager edits. | Medium |
| Answer a product or policy question *(per question)* | 10–30 min | 1–3 min | SDR currently waits for a trainer or searches docs; the tutor retrieves and cites in seconds, with a quick human check. | Medium |
| Run a cold-call practice and debrief *(per session)* | 30–45 min | 15–25 min | A trainer plays the prospect and gives verbal feedback now; the AI plays the prospect and scores, so trainer time shifts to coaching. | Low-Medium |
| Produce a coaching note from a call *(per call)* | 20–40 min | 5–12 min | M01 baseline is 3–5 hrs/week of manual call review at 24–72 hr latency; the AI drafts from the transcript and the manager reviews and adds context. | Medium |
| **Certification gap analysis** *(per SDR at the cert gate)* | **45–75 min** | **10–15 min** | A trainer currently re-listens to a simulation call and re-reads exam answers, then scores against the 5-dimension rubric by hand. The AI scores against the same rubric, quotes the evidence behind each score, and the trainer reviews and decides. | Medium |
| Post-cert onboarding debrief *(per certified SDR)* | 60–90 min (rarely done) | 10–15 min review | Structured program feedback is rarely captured today, so onboarding rarely improves cohort-over-cohort. The SDR answers 7 process questions, the AI synthesizes a debrief (what worked, barriers, fixes), the manager reviews before sharing with enablement. | Low |

---

## Summary table

"Case" here is one new-hire pre-boarding cycle (the first three rows
above). Recurring per-instance savings are captured in the per-step
table.

| Metric | Current process estimate | AI-supported process estimate | Expected change |
|---|---:|---:|---|
| Total time per case (pre-boarding setup) | 125–220 min | 18–38 min | Faster |
| Human review time per case | folded into the work, unmeasured | 15–30 min, now explicit | May rise as a share of a smaller total because review is deliberate |
| Number of handoffs | 3–4 (enablement → manager → mentor) | 1–2 | Fewer handoffs |
| Rework risk | Medium | Low-Medium | Cited sources and an explicit review gate reduce it |
| Hire wait time for a personalized plan | Days; often generic content | Same day or next day | Faster and personalized |

---

## Cost assumptions

```text
Estimated labor cost per case = estimated minutes per case / 60 * estimated hourly cost
```

We assume a fully loaded cost of **$70/hour** for the enablement
manager, SDR manager, and trainer roles that do this work, including
salary, benefits, and overhead. This is a reasonable mid-range
assumption for a US sales-management or enablement role and is labeled
as an assumption, not a Salesforce figure.

**Pre-boarding setup, per hire:**

- **Current:** 125–220 min / 60 × $70/hr = **$146–$257 per hire**
- **AI-supported:** 18–38 min / 60 × $70/hr = **$21–$44 per hire**
- **Estimated labor savings:** roughly **$120–$215 per hire**

The larger recurring saving is in coaching. At 20–40 min per call
today versus 5–12 min reviewed, a manager handling several calls per
rep per week moves toward the M01 target of under 1 hr/week of review
(from a 3–5 hr/week baseline), which compounds across a cohort far
faster than the one-time setup saving.

Certification adds a one-time saving of **$40–$71** per SDR at the
gate (45–75 min → 10–15 min × $70/hr). For a cohort of 10 SDRs per
quarter that's ~$1,600–$2,800 per year — small compared to coaching
but the verdict is more reliable thanks to the server-side band
recompute.

---

## Quality measures

We expect the prototype to improve quality on four measures, not just
time:

1. **Better use of internal documents.** Both LLM skills retrieve from
   the 16-document knowledge base and cite their sources, and the
   tutor refuses when no authoritative passage exists. This directly
   counters the M01 pain point that SDRs "may learn outdated product
   positioning" from stale, manually updated content.

2. **More consistent coaching and feedback.** Coaching notes and
   simulation debriefs apply the same rubric every time, which
   addresses M01's finding that manager coaching quality is "the
   largest uncontrolled variable" and feedback is "verbal and
   unstructured." Certification adds a second consistency lever —
   every SDR is scored on the same 5 dimensions with quoted evidence.

3. **Faster feedback and fewer unreviewed calls.** Drafting a note
   from a transcript in minutes moves feedback latency from the M01
   baseline of 24–72 hours toward the under-4-hour target, and makes
   it feasible to review calls that currently "go unreviewed entirely."

4. **Auditability and fewer missed review steps.** Every AI output is
   gated by an approve / edit / reject / escalate decision that is
   written to a shared decision log, so review is explicit and
   traceable rather than implicit. The certification step adds a
   **server-side band-recompute** that catches LLM verdict drift
   before the recommendation reaches the trainer; any mismatch between
   the LLM's self-reported overall verdict and the deterministic
   recompute is appended to `review_reasons` so the trainer is told
   *why* the case is flagged.

---

## Face validity check

A full face-validity check (direction, magnitude, evidence alignment,
and practical constraints, with anchors) lives in
[face_validity.md](face_validity.md). In short: the redesign reduces
time where AI helps while keeping human review where judgment matters,
the 60–85% effect sizes sit below Milestone 01's own user-story
claims, and the DeepEval 6-run measurement (3 baseline + 3 post-fix)
shows produced answers tracing to their sources with a measurable
+2 mean lift and tightened variance (range 3 → range 1), so the
estimates above are reasonable enough to investigate further.
