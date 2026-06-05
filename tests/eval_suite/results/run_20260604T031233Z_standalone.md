# DeepEval results — 20260604T031233Z (standalone)

**10 cases · 40 metric runs · 23 passed · 17 failed** (pass threshold = 0.70)

| # | Case | Category | Citation+NextStep | Faithfulness | AnswerRelevancy | SDRFaceValidity | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | `price_objection` | normal | ✅ 1.00 | ✅ 1.00 | ✅ 0.70 | ❌ 0.50 | **FAIL** |
| 2 | `cold_call_rubric` | normal | ✅ 1.00 | ✅ 1.00 | ✅ 0.70 | ✅ 1.00 | **PASS** |
| 3 | `quota_ramp` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 4 | `territories` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 5 | `escalation_silent_enterprise` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 6 | `tooling_first_week` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 7 | `competitor_pricing_legal` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 8 | `vague_get_better` | vague | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | ❌ 0.50 | **FAIL** |
| 9 | `no_source_fake_roi` | no_source | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 10 | `confident_incomplete_perfect_call` | confident_incomplete | ✅ 1.00 | ✅ 1.00 | ❌ 0.10 | ❌ 0.00 | **FAIL** |

## `price_objection` (normal)

**Question:** How do I handle a price objection on a cold call?

**Ideal answer (rubric):** Acknowledge the budget concern, reframe to value or ROI, and ask a discovery question to surface the real driver. Never lead with a discount on the first call.

**Expected KB doc:** `objection_handling_top10.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.82 · **best cosine:** 0.468 · **flagged:** False

**Answer:**

> Use the Acknowledge–Reframe–Redirect (ARR) pattern, which is required by Coaching Rubric v3.1 [5]. For a price/budget objection ('We don't have budget'), here's how to apply it [1]: (1) Acknowledge — don't argue, just validate their concern. (2) Reframe — 'Budget cycles vary; we typically start the conversation 4–6 months before procurement.' (3) Redirect — propose a future-dated discovery call so you're in the conversation when budget opens up [1]. Skipping the Acknowledge step costs you 1–2 points on dimension 3 of your call review score [5], so never jump straight to reframing. Keep it short, stay curious, and end with a specific ask for time.

**Next step:** Within the next hour, open Slack and message your Trail Guide in #sdr-help with: 'Can you pull up a Gong clip where a rep handles a budget objection well using ARR? I want to hear a real example before my next call block.'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the retrieved sources: the ARR pattern, its requirement in Coaching Rubric v3.1, the specific budget objection response, the 4–6 months reframe, the future-dated discovery call redirect, and the 1–2 point deduction on dimension 3 for skipping the Acknowledge step are all explicitly stated in sources [1] and [5].
- ✅ **AnswerRelevancy** (0.70) — The answer covers acknowledging the concern and redirecting with a discovery ask, but the reframe focuses on budget timing rather than value/ROI, and it doesn't explicitly address never leading with a discount on the first call.
- ❌ **SDRFaceValidity** (0.50) — The ARR framework and example line are concrete and useful, but referencing internal rubric scores and coaching documents feels bureaucratic rather than peer advice, and the actionable step is vague ('end with a specific ask') rather than a single thing to do today.

## `cold_call_rubric` (normal)

**Question:** What does our cold-call quality rubric grade on?

**Ideal answer (rubric):** The rubric scores opening, discovery, value framing, objection handling, and a concrete next step. Strong calls hit the bar on opening and end with one clear CTA.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.95 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> The cold-call quality rubric (Coaching Rubric v3.1) grades every recorded call on four dimensions, each scored 1–10 and combined into a weighted overall score [1]: 1) Opening & framing (weight 0.20) — did you state who you are, why you're calling, and earn 30 more seconds within the first 15? [1] 2) Discovery quality (weight 0.35) — how many qualified discovery questions did you ask, and did you follow up on prospect answers? [1] 3) Objection handling (weight 0.25) — did you use the Acknowledge–Reframe–Redirect (ARR) pattern? [1][3] 4) Close & next step (weight 0.20) — did you propose and get a specific, calendared next step? [1] Watch out for common deductions: talking past the prospect (–1 to –2), pitch dumping (–2), and unapproved claims (–3) [1].

**Next step:** Within the next hour, pull up one of your recent Gong call recordings and self-score it across the four rubric dimensions using the weights in source [1], then post your scores and one question about where you lost points in the #sdr-help Slack channel, tagging your Trail Guide for feedback.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by source [1] (the four dimensions, their weights, the 1-10 scale, and the common deductions) and source [3] (the ARR pattern requirement), with no fabricated details.
- ✅ **AnswerRelevancy** (0.70) — The answer covers opening, discovery, objection handling, and next step, but omits 'value framing' as a distinct dimension mentioned in the rubric, and doesn't explicitly note that strong calls must hit the bar on opening specifically.
- ✅ **SDRFaceValidity** (1.00) — Concrete dimensions with weights, plain peer-level language, specific deduction examples, and an implicit action (review your recorded calls against these four criteria today).

## `quota_ramp` (normal)

**Question:** What is the quota ramp schedule for a new SDR?

**Ideal answer (rubric):** Ramp is graduated over the first six months: a lower target in months 1–2, a mid target in months 3–4, and full quota from roughly month 6 onward.

**Expected KB doc:** `quota_ramp_schedule.md`

**Retrieved docs (top-5):** onboarding_policy.md, quota_ramp_schedule.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.95 · **best cosine:** 0.714 · **flagged:** False

**Answer:**

> Your quota ramp depends on your experience level [1]:
> 
> **Entry-level (0–1 yrs sales experience):**
> - Month 1: 25% of full quota (focus on activity metrics) [1]
> - Month 2: 60% of full quota (partial commission) [1]
> - Month 3+: 100% of full quota (full commission) [1]
> Months 1–2 include a guaranteed minimum equal to 70% of target variable [1].
> 
> **Mid-level (2–4 yrs experience):**
> - Month 1: 50%, Month 2: 90%, Month 3+: 100% [1]
> Guaranteed minimum applies Month 1 only [1].
> 
> **Senior (5+ yrs experience):**
> - 100% quota from Day 30 onward; no guaranteed minimum unless negotiated at offer [1].
> 
> During Month 1, all SDRs must also hit activity targets: 60 outbound dials/day, 25 personalized emails/day, 5 LinkedIn touches/day, and 3 booked discovery calls/week [2]. This schedule is binding for start dates April 1, 2024–March 31, 2025 [1].

**Next step:** Slack Ravi Anand (Director of Sales Operations) in #sdr-help with your start date and experience level, and ask him to confirm which ramp tier applies to you under the FY24-Q2 schedule.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the retrieved sources, including the ramp percentages, guaranteed minimums, activity targets, and the binding date range.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses quota ramp but describes a 3-month ramp (full quota at month 3+) rather than the rubric's 6-month graduated schedule, so it partially matches but diverges on the key timeline detail.
- ❌ **SDRFaceValidity** (0.50) — The answer is detailed and structured but reads more like a policy document than peer advice, and it lacks a concrete action the SDR can take today (e.g., 'go ask your manager which tier applies to you').

## `territories` (normal)

**Question:** How are SDR territories defined?

**Ideal answer (rubric):** Territories are split by region and vertical (e.g. AMER Healthcare, EMEA FinTech) with revenue-band segmentation inside each.

**Expected KB doc:** `territory_definitions.md`

**Retrieved docs (top-5):** certification_rubric.md, compensation_overview.md, onboarding_policy.md, sales-development-wikipedia.md, territory_definitions.md

**Tutor confidence:** 0.92 · **best cosine:** 0.479 · **flagged:** False

**Answer:**

> Salesforce splits the SDR org into four global territories, effective January 2024 [1]: **AMER-West** (western US states, BC/Alberta/Yukon, Mexico), **AMER-East** (central/eastern US states, most of Canada, and Brazil — a common edge case), **EMEA** (all EU/EEA, UK, Middle East, Africa), and **APAC** (Australia, NZ, Japan, South Korea, Singapore, and other Southeast Asian markets, plus India in its own Bengaluru pod) [1]. A few edge cases trip up new SDRs: Brazil routes to AMER-East (not LATAM-unassigned), UAE goes to EMEA (not APAC), India goes to APAC (not EMEA), and Mexico goes to AMER-West (not LATAM-unassigned) [1]. The lead-routing engine will warn you if you try to manually reassign one of these incorrectly [1]. For questions, the owner is **Ravi Anand, Director of Sales Operations** [1].

**Next step:** Slack Ravi Anand (Director of Sales Operations) in #sdr-help with a specific edge-case question — for example, ask: 'Can you confirm which territory a lead from [country you're unsure about] falls into, and how I should manually reassign it in the lead-routing tool if needed?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the territory_definitions.md source, including the four territories, their constituent regions, the edge cases, the lead-routing engine warning, and Ravi Anand's role.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses territory definitions but focuses only on geographic regions without mentioning vertical segmentation (e.g., Healthcare, FinTech) or revenue-band segmentation within territories, which are key parts of the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and concrete but reads like internal documentation rather than peer advice, and it lacks a clear actionable step the SDR can take today (e.g., 'pull up the routing tool and look up your first lead's country').

## `escalation_silent_enterprise` (normal)

**Question:** A high-value enterprise prospect has gone silent after a discovery call. What's the escalation path?

**Ideal answer (rubric):** Loop in the AE and territory manager through the documented Slack channel within the SLA window; involve legal only if NDA or pricing has been shared.

**Expected KB doc:** `escalation_paths.md`

**Retrieved docs (top-5):** certification_questions.md, certification_rubric.md, cold-calling-wikipedia.md, cold_call_quality_rubric.md

**Tutor confidence:** 0.10 · **best cosine:** 0.532 · **flagged:** False

**Answer:**

> The sources retrieved don't contain a documented escalation path for a silent enterprise prospect after a discovery call. The sources cover cold-call scoring rubrics [1], discovery questioning techniques [2], objection handling frameworks [3], and general cold-calling research [4][5] — none of which address a post-discovery re-engagement or escalation process. To avoid giving you incorrect guidance on a high-stakes account, you should get this directly from your SDR manager or the AE on the account.

**Next step:** Send a Slack DM to your SDR manager right now with this message: 'I had a discovery call with a high-value enterprise prospect who has since gone silent — can you walk me through our escalation path and whether I should loop in the AE? Happy to share the account details.' If you don't know your SDR manager's Slack handle, find it in your company directory or ask in #sdr-help.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly identified that none of the retrieved sources address a post-discovery escalation path and refused to speculate, directing the user to their manager instead.
- ❌ **AnswerRelevancy** (0.00) — The answer does not address the escalation path at all, instead deflecting by saying the information isn't in its sources, whereas the rubric expects specific guidance about looping in AE and territory manager via Slack within SLA window and involving legal only if NDA/pricing was shared.
- ❌ **SDRFaceValidity** (0.50) — Honest about knowledge limits and ends with a concrete action (talk to manager/AE), but gives zero actual tactical guidance on re-engaging a silent prospect, making it only half-helpful for a week-one SDR.

## `tooling_first_week` (normal)

**Question:** Which tools should I have access to in my first week as an SDR?

**Ideal answer (rubric):** Core stack: Salesforce, Salesloft, Gong, and Clari. Request access through the tooling checklist, with IT and the SDR manager as approvers.

**Expected KB doc:** `tooling_access_checklist.md`

**Retrieved docs (top-5):** onboarding_policy.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.92 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> Here's what you should have access to in your first week, based on the tooling checklist [1]:
> 
> **Day 1 (before your first login):**
> - **Salesforce CRM** — production org with the `SDR Standard` profile [1]
> - **Outreach** — full seat with the default cadence library (note: your Trail Guide must review personal sequences before you send them) [1]
> - **Slack** — added to `#sdr-global`, your regional pod channel, and `#trail-guides-cohort-2024` [1]
> - **Google Workspace** — calendar, Meet, and mailbox with the SDR signature template [1]
> 
> **Day 3:**
> - **Gong** — recording and review seat; auto-recording is on by default for outbound dials [1]
> 
> **Week 2 (not your first week):**
> - LinkedIn Sales Navigator and ZoomInfo come later and require additional approvals [1]
> 
> If anything is missing on Day 1, it gets escalated to **Linh Truong** by 11:00 AM local time [1]. A common Day-1 issue is Outreach not being preinstalled on your laptop — the fix involves pushing image `MAC-SDR-2024-08` from the MDM console [4].

**Next step:** Open Slack and post in #sdr-help tagging Linh Truong: 'Hi Linh, I'm a new SDR hire checking my Day-1 tool access per ACCESS-2024-NEWSDR. Can you confirm Salesforce CRM, Outreach, Slack, and Google Workspace are all provisioned for me?' Do this within the next hour so any gaps are caught before the 11:00 AM escalation deadline.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the retrieved sources, including tool names, profiles, Slack channels, Day-1/Day-3/Week-2 timing, escalation to Linh Truong, and the MDM image fix.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses the question about tools but mentions Outreach instead of Salesloft, and omits Clari entirely, while also not mentioning the correct approvers (IT and SDR manager) from the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and well-structured but reads like it was pulled from a made-up internal document with fabricated details (specific names, image IDs, profile names) that have no grounding, and it lacks a concrete action the SDR can take today.

## `competitor_pricing_legal` (normal)

**Question:** What can I say about a competitor's pricing in outbound emails?

**Ideal answer (rubric):** Don't quote a competitor's pricing or make comparative claims you can't back to a published source. Anything past public info needs legal review before sending.

**Expected KB doc:** `legal_messaging_constraints.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, customer-relationship-management-wikipedia.md, lead-generation-wikipedia.md, sales-development-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.05 · **best cosine:** 0.386 · **flagged:** True

**Answer:**

> The available sources [1][2][3][4][5] do not contain any guidance on what SDRs can or cannot say about competitor pricing in outbound emails. This is an important topic that touches on legal risk, company messaging policy, and ethical sales practices — none of which are covered in the retrieved knowledge base. You should not make up rules here, as getting this wrong could expose Salesforce to legal liability.

**Next step:** Send a Slack message to your SDR manager in #sdr-help asking: 'What is Salesforce's approved policy on referencing competitor pricing in outbound prospecting emails — is there a written guideline or approved messaging I should follow?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly identified that none of the retrieved sources contain guidance on competitor pricing in outbound emails and refused to speculate, which is fully faithful to the sources provided.
- ❌ **AnswerRelevancy** (0.00) — The answer refuses to provide any guidance, while the rubric expects a direct answer about not quoting competitor pricing or making unverifiable comparative claims without legal review.
- ❌ **SDRFaceValidity** (0.50) — The answer honestly admits it lacks sourced guidance and flags real risks, but it leaves the new SDR with no concrete next step to actually answer their question today.

## `vague_get_better` (vague)

**Question:** How can I get better at my job?

**Ideal answer (rubric):** The question is too broad to answer well from the KB. A strong response asks the SDR to narrow it (e.g. cold calls, emails, discovery) or recommends a 1:1 with the SDR manager / mentor instead of guessing.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** certification_rubric.md, cold_call_quality_rubric.md, customer-relationship-management-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.55 · **best cosine:** 0.269 · **flagged:** True

**Answer:**

> Your question — 'How can I get better at my job?' — is too broad to answer well from the knowledge base. It could go in at least five directions: cold-call skills, discovery technique, objection handling, certification prep, or pipeline management. Here are 2–3 narrower questions that the sources *can* actually help with: (1) 'How is my cold-call scored, and where do I lose the most points?' [4] (2) 'What does a strong discovery conversation look like vs. a weak one?' [2] (3) 'What is the Acknowledge–Reframe–Redirect pattern for handling objections?' [4]. Pick one of these and bring it to a 1:1 with your Trail Guide or SDR manager so you get targeted coaching rather than generic advice.

**Next step:** Slack your Trail Guide in #sdr-help within the next hour with this message: 'Hey — I want to improve one specific skill this week. Can we do a 15-min 1:1 to review my cold-call scores using the Cold-call coaching rubric and identify my lowest-weighted dimension?' That gives them a concrete starting point.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — The tutor's references to cold-call scoring [4] and discovery/MEDDIC [2] are grounded in the sources, but the 'Acknowledge–Reframe–Redirect' pattern is attributed to [4] when source [4] only mentions it exists and points to a separate file ('objection_handling_top10.md'), and the suggestion to bring questions to a 'Trail Guide' is an unsupported specific claim not found in the retrieved sources shown.
- ✅ **AnswerRelevancy** (1.00) — The answer explicitly acknowledges the question is too broad, offers narrower specific questions to focus on, and recommends a 1:1 with the SDR manager/Trail Guide, fully matching the rubric.
- ❌ **SDRFaceValidity** (0.50) — Helpful redirect with concrete follow-up questions, but it doesn't actually answer anything and the actionable step (bring it to a 1:1) is vague rather than something the SDR can do right now.

## `no_source_fake_roi` (no_source)

**Question:** What's our policy on showing fabricated ROI calculators to prospects when we don't have their real numbers yet?

**Ideal answer (rubric):** The KB does not contain authoritative guidance on this specific situation. A strong answer says that explicitly, refuses to invent a policy, and routes the SDR to legal or the SDR manager.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, legal_messaging_constraints.md, salesforce-wikipedia.md

**Tutor confidence:** 0.82 · **best cosine:** 0.349 · **flagged:** True

**Answer:**

> Fabricated ROI calculators are not allowed. Under Legal Approval Workflow LMG-2024 [2], SDRs cannot share any specific financial claim — percentages, dollar figures, or multipliers — unless it comes from a Legal-approved asset (like an approved case study, press release, or 10-Q) [2]. Showing a prospect made-up numbers, even as a 'placeholder,' could trigger regulatory inquiries or litigation [2]. If you want to use an ROI figure, it must carry an internal approval code (e.g., a CSQ-XXXX-XXX reference) from Legal [2]. Until you have the prospect's real numbers and a Legal-approved framework to use, stick to describing Salesforce's capabilities qualitatively and let the prospect draw their own conclusions. To get custom language approved, draft it and submit via the LMG-2024 intake form on the Legal portal — turnaround is 1 business day for low-risk paraphrasing [2].

**Next step:** Message your SDR manager in #sdr-help on Slack right now: 'I want to use an ROI calculator in outreach but don't have the prospect's real numbers yet — can you point me to any Legal-approved ROI assets with CSQ codes I can reference, or help me submit language through the LMG-2024 intake form on the Legal portal?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every specific claim in the tutor's answer (LMG-2024 workflow, prohibition on financial figures without legal-approved assets, CSQ-XXXX-XXX codes, regulatory/litigation risk, 1-business-day SLA for low-risk paraphrasing, LMG-2024 intake form) is directly supported by source [2], and the qualitative advice to describe capabilities without fabricated numbers aligns with the approved-pattern guidance in that source.
- ❌ **AnswerRelevancy** (0.00) — The answer invents a specific policy (Legal Approval Workflow LMG-2024, CSQ reference codes, 1-day turnaround) rather than acknowledging the KB lacks authoritative guidance and routing the SDR to legal or their manager.
- ❌ **SDRFaceValidity** (0.50) — The answer is clear and has a concrete action (submit via LMG-2024 intake form), but the specific policy codes and 1-business-day turnaround claim feel fabricated/hallucinated, which undermines trust for a new SDR relying on this guidance.

## `confident_incomplete_perfect_call` (confident_incomplete)

**Question:** Walk me through every step of a perfect first cold call.

**Ideal answer (rubric):** A complete answer cites both the cold-call rubric (opening, discovery, value, objection handling, CTA) AND the vertical playbook for tailored language. Citing only one of those is incomplete.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, gold_plan_healthcare_entry.md

**Tutor confidence:** 0.55 · **best cosine:** 0.385 · **flagged:** True

**Answer:**

> This question is too broad to answer fully from the available knowledge base — 'every step of a perfect cold call' could go in several directions (opener, discovery, objection handling, closing, CRM logging, etc.). Here are 2–3 narrower questions the sources can actually help with: (1) 'What does a strong opening and framing look like in the first 15 seconds of a cold call?' [2] (2) 'How do I handle objections using the Acknowledge–Reframe–Redirect pattern?' [2] (3) 'What does the Coaching Rubric v3.1 score me on, and how is my overall score weighted?' [2] The sources do confirm that cold calls are scored across four dimensions — Opening & Framing, Discovery Quality, Objection Handling, and Close & Next Step [2] — but a step-by-step walkthrough requires your Trail Guide to tailor it to your specific territory and ramp plan [4]. Book a 1:1 with your Trail Guide or SDR manager to walk through one dimension at a time.

**Next step:** Slack your Trail Guide in #sdr-help with this message: 'I want to break down the cold call rubric one section at a time — can we start with Opening & Framing from Coaching Rubric v3.1 in our next 1:1 or a quick 15-min call this week?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — All specific claims in the tutor's answer are directly supported by source [2] (four scored dimensions, their names, the Acknowledge–Reframe–Redirect pattern) and source [4] (Trail Guide reference), and the tutor appropriately declined to fabricate a step-by-step walkthrough not present in the sources.
- ❌ **AnswerRelevancy** (0.10) — The answer refuses to walk through the steps and instead deflects with narrower questions, failing to cover both the cold-call rubric (opening, discovery, value, objection handling, CTA) and the vertical playbook for tailored language as required by the rubric.
- ❌ **SDRFaceValidity** (0.00) — The answer dodges the question entirely by refusing to walk through the steps, offers no concrete cold call guidance, and the 'action' is just to book a meeting rather than something the SDR can do right now.
