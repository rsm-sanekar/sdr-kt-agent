# DeepEval results — 20260603T215953Z (standalone)

**10 cases · 40 metric runs · 23 passed · 17 failed** (pass threshold = 0.70)

| # | Case | Category | Citation+NextStep | Faithfulness | AnswerRelevancy | SDRFaceValidity | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | `price_objection` | normal | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | ❌ 0.50 | **FAIL** |
| 2 | `cold_call_rubric` | normal | ✅ 1.00 | ✅ 1.00 | ✅ 0.70 | ✅ 1.00 | **PASS** |
| 3 | `quota_ramp` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | **FAIL** |
| 4 | `territories` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 5 | `escalation_silent_enterprise` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 6 | `tooling_first_week` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 7 | `competitor_pricing_legal` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.00 | **FAIL** |
| 8 | `vague_get_better` | vague | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 9 | `no_source_fake_roi` | no_source | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ✅ 0.90 | **FAIL** |
| 10 | `confident_incomplete_perfect_call` | confident_incomplete | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | ❌ 0.50 | **FAIL** |

## `price_objection` (normal)

**Question:** How do I handle a price objection on a cold call?

**Ideal answer (rubric):** Acknowledge the budget concern, reframe to value or ROI, and ask a discovery question to surface the real driver. Never lead with a discount on the first call.

**Expected KB doc:** `objection_handling_top10.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.55 · **best cosine:** 0.468 · **flagged:** False

**Answer:**

> Price objections on a cold call aren't covered directly in the sources, but the closest match is the 'We don't have budget' objection [1]. Use the required Acknowledge–Reframe–Redirect (ARR) pattern [1][5]: (1) Acknowledge: 'That makes total sense — budget is always a real constraint.' (2) Reframe: 'Budget cycles vary; we typically start the conversation 4–6 months before procurement, so you're set up when the time comes.' [1] (3) Redirect: Propose a future-dated discovery call to explore fit without pressure [1]. Skipping the Acknowledge step costs you 1–2 points on Dimension 3 of the Coaching Rubric v3.1 [5], so never jump straight to defending price. The goal on a cold call is a meeting, not a price negotiation — keep redirecting there.

**Next step:** Pull up objection_handling_top10.md today, practice the ARR script for the 'We don't have budget' objection out loud, then ask your Trail Guide or SDR manager to role-play a price objection with you before your next call block.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — The tutor correctly applies ARR from source [1] and cites the rubric penalty from [5], but the specific 'budget' objection reframe is used to answer a 'price objection' question—the sources don't cover price objections directly—and the tutor adds an unsupported claim ('The goal on a cold call is a meeting, not a price negotiation') not found in the retrieved sources.
- ✅ **AnswerRelevancy** (1.00) — The answer acknowledges the concern, reframes to value/timing, redirects with a discovery question, and explicitly states not to negotiate price on a cold call, fully covering the rubric.
- ❌ **SDRFaceValidity** (0.50) — The ARR framework and closing advice are solid and concrete, but the answer is cluttered with internal rubric references (Coaching Rubric v3.1, Dimension 3) that mean nothing to a week-one SDR, and it lacks a single clear action to take today.

## `cold_call_rubric` (normal)

**Question:** What does our cold-call quality rubric grade on?

**Ideal answer (rubric):** The rubric scores opening, discovery, value framing, objection handling, and a concrete next step. Strong calls hit the bar on opening and end with one clear CTA.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.95 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> Our cold-call quality rubric (v3.1) grades every Gong-sampled call on four dimensions, each scored 1–10 and combined into a weighted overall score [1]: (1) Opening & framing (20% weight) — did you state who you are, why you're calling, and earn 30 more seconds within the first 15? [1] (2) Discovery quality (35% weight) — how many qualified discovery questions did you ask, and how well did you follow up on prospect answers? [1] (3) Objection handling (25% weight) — did you use the Acknowledge–Reframe–Redirect (ARR) pattern? [1][3] (4) Close & next step (20% weight) — did you propose and get a specific, calendared next step? [1] Watch out for common deductions: talking past the prospect (–1 to –2), pitch dumping before discovery (–2), and unapproved claims (–3) [1].

**Next step:** Pull up cold_call_quality_rubric.md today and score one of your own recent practice calls against all four dimensions before your next Trail Guide session.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer—the four dimensions, their weights, the 1–10 scale, the ARR pattern reference, and the common deductions—is directly supported by source [1] (cold_call_quality_rubric.md) and source [3] (objection_handling_top10.md).
- ✅ **AnswerRelevancy** (0.70) — The answer covers opening, discovery, objection handling, and next step, but omits 'value framing' as a distinct graded dimension mentioned in the rubric, and lists only four dimensions instead of five.
- ✅ **SDRFaceValidity** (1.00) — Concrete rubric breakdown with weights, real examples of deductions, plain peer-level language, and an implicit action (know these four dimensions before your next call).

## `quota_ramp` (normal)

**Question:** What is the quota ramp schedule for a new SDR?

**Ideal answer (rubric):** Ramp is graduated over the first six months: a lower target in months 1–2, a mid target in months 3–4, and full quota from roughly month 6 onward.

**Expected KB doc:** `quota_ramp_schedule.md`

**Retrieved docs (top-5):** onboarding_policy.md, quota_ramp_schedule.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.95 · **best cosine:** 0.714 · **flagged:** False

**Answer:**

> Your quota ramp depends on your prior sales experience [1]. If you're entry-level (0–1 years), you'll be at 25% of full quota in Month 1 (focus on activity, not bookings), 60% in Month 2 (first real attainment month), and 100% from Month 3 onward [1]. For months 1 and 2, you're guaranteed a minimum of 70% of your target variable pay [1]. If you have 2–4 years of experience, you ramp faster: 50% in Month 1, 90% in Month 2, then 100% [1]. Senior hires (5+ years) hit 100% quota on Day 30 with no guaranteed minimum after that [1]. During Month 1, everyone is also held to activity targets: 60 outbound dials/day, 25 personalized emails/day, 5 LinkedIn touches/day, and 3 booked discovery calls/week [2]. The schedule owner is Ravi Anand, Director of Sales Operations [1].

**Next step:** Find your offer letter or ask your SDR manager to confirm your experience tier (entry, mid, or senior) so you know exactly which ramp curve applies to you starting Day 1.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the retrieved sources, including ramp percentages, guaranteed minimums, activity targets, and the schedule owner.
- ❌ **AnswerRelevancy** (0.50) — The answer provides a quota ramp schedule but it doesn't match the rubric's description of a graduated ramp over six months (lower in months 1-2, mid in months 3-4, full from month 6); instead it describes a faster ramp reaching 100% by month 3 or earlier depending on experience level.
- ✅ **SDRFaceValidity** (1.00) — Concrete ramp percentages by experience tier, guaranteed minimums, daily activity targets, and a named owner give a week-one SDR everything they need to understand their situation today.

## `territories` (normal)

**Question:** How are SDR territories defined?

**Ideal answer (rubric):** Territories are split by region and vertical (e.g. AMER Healthcare, EMEA FinTech) with revenue-band segmentation inside each.

**Expected KB doc:** `territory_definitions.md`

**Retrieved docs (top-5):** certification_rubric.md, compensation_overview.md, onboarding_policy.md, sales-development-wikipedia.md, territory_definitions.md

**Tutor confidence:** 0.95 · **best cosine:** 0.479 · **flagged:** False

**Answer:**

> Salesforce SDR territories are split into four global regions, effective January 2024 [1]: (1) AMER-West covers the western US states, parts of Canada (BC, Alberta, Yukon), and Mexico. (2) AMER-East covers the eastern/central US states, eastern Canada, and — importantly — Brazil (not LATAM-unassigned) [1]. (3) EMEA covers all of Europe, the Middle East, and Africa. Note: UAE, Israel, and Turkey are in EMEA, not APAC [1]. (4) APAC covers Australia, NZ, Japan, South Korea, Singapore, and other Southeast Asian countries. India is in APAC with its own Bengaluru pod — do not route Indian leads through EMEA [1]. A few edge cases trip up new SDRs most often: Brazil → AMER-East, UAE → EMEA, India → APAC, Mexico → AMER-West [1]. For any territory questions, reach out to Ravi Anand, Director of Sales Operations [1].

**Next step:** Open territory_definitions.md today and quiz yourself on the four edge cases (Brazil, UAE, India, Mexico) — then send a quick Slack message to your Trail Guide confirming which territory you're assigned to.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by territory_definitions.md, including the four regions, their constituent countries/states, the edge cases, and the contact person Ravi Anand.
- ❌ **AnswerRelevancy** (0.50) — The answer covers regional splits in detail but does not mention vertical segmentation (e.g., Healthcare, FinTech) or revenue-band segmentation within territories, which are key parts of the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and concrete with useful edge cases, but it reads like internal documentation rather than peer advice, and lacks a clear single action the SDR can take today (mentioning Ravi is buried at the end without a direct call-to-action like 'Slack Ravi right now with your assigned accounts and confirm your territory').

## `escalation_silent_enterprise` (normal)

**Question:** A high-value enterprise prospect has gone silent after a discovery call. What's the escalation path?

**Ideal answer (rubric):** Loop in the AE and territory manager through the documented Slack channel within the SLA window; involve legal only if NDA or pricing has been shared.

**Expected KB doc:** `escalation_paths.md`

**Retrieved docs (top-5):** certification_questions.md, certification_rubric.md, cold-calling-wikipedia.md, cold_call_quality_rubric.md

**Tutor confidence:** 0.15 · **best cosine:** 0.532 · **flagged:** False

**Answer:**

> The provided sources do not contain a specific escalation path for re-engaging a silent enterprise prospect after a discovery call. The sources cover cold-call scoring rubrics [1], discovery question techniques [2], objection handling methods [3], and general cold-calling research [4][5] — but none outline a formal 'gone silent' escalation process for high-value accounts. That said, source [3] offers a useful starting point: if the prospect resurfaces with an objection or pushback, use the Defuse-Discover-Deliver method to re-engage rather than reacting defensively [3]. For the actual escalation path (e.g., when to loop in your AE, when to flag to your manager, how many touches before escalating), your SDR manager is the right person to ask — they'll know Salesforce's internal playbook for enterprise accounts.

**Next step:** Send your SDR manager a quick Slack message today: 'Hey — I have a high-value enterprise prospect who went silent after discovery. Can you walk me through our escalation path and re-engagement playbook for this scenario?' Bring the account name and discovery call notes so they can give you specific guidance.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly identified that the sources don't cover a 'gone silent' escalation path, accurately described what each source does cover, made only one supported claim from source [3] about the Defuse-Discover-Deliver method, and appropriately deferred to the SDR manager for the actual playbook without fabricating any specifics.
- ❌ **AnswerRelevancy** (0.00) — The answer explicitly states it cannot provide the escalation path and defers to the SDR manager, failing to address the rubric's specific steps of looping in AE and territory manager via Slack within SLA window and involving legal only if NDA/pricing was shared.
- ❌ **SDRFaceValidity** (0.50) — Honest about its limitations and redirects appropriately, but gives no concrete next step the SDR can take today (e.g., send a specific follow-up, check in with AE now) — just says 'ask your manager.'

## `tooling_first_week` (normal)

**Question:** Which tools should I have access to in my first week as an SDR?

**Ideal answer (rubric):** Core stack: Salesforce, Salesloft, Gong, and Clari. Request access through the tooling checklist, with IT and the SDR manager as approvers.

**Expected KB doc:** `tooling_access_checklist.md`

**Retrieved docs (top-5):** onboarding_policy.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.95 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> Here's what you should have access to in your first week:
> 
> **Day 1 (before you even log in):** Salesforce CRM (with the SDR Standard profile), Outreach (full seat with cadence library), Slack (added to #sdr-global, your regional pod, and #trail-guides-cohort-2024), and Google Workspace (email + calendar). [1] If anything is missing by 11:00 AM on Day 1, it gets escalated to Linh Truong. [1]
> 
> **Day 3:** Gong recording and review seat — auto-recording is on by default for all your outbound dials. [1]
> 
> **Week 2:** LinkedIn Sales Navigator (Advanced seat with TeamLink), though there may be a wait if the regional license pool is full. [1]
> 
> **Needs manager approval (anytime):** ZoomInfo requires written approval from your SDR manager before it's provisioned. [1]
> 
> Note: A common Day-1 hiccup is Outreach not being preinstalled on your laptop — flag it to Linh's team right away if that happens. [1]

**Next step:** On Day 1, log into each of the four tools (Salesforce CRM, Outreach, Slack, Google Workspace) and confirm they're working. If any are missing by 11:00 AM, immediately message Linh Truong so the issue gets escalated and resolved fast. [1]

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the retrieved sources from tooling_access_checklist.md, including Day-1 tools, Day-3 Gong access, Week-2 LinkedIn Sales Navigator, ZoomInfo approval requirements, escalation to Linh Truong, and the common Outreach preinstall issue.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses the question about tools but mentions different tools (Outreach instead of Salesloft, no mention of Clari) and doesn't mention the tooling checklist with IT and SDR manager as approvers per the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and concrete but reads like it's pulled from a specific company's onboarding doc (with names, dates, and internal channels) rather than peer advice, and it lacks a clear single action the SDR should take today.

## `competitor_pricing_legal` (normal)

**Question:** What can I say about a competitor's pricing in outbound emails?

**Ideal answer (rubric):** Don't quote a competitor's pricing or make comparative claims you can't back to a published source. Anything past public info needs legal review before sending.

**Expected KB doc:** `legal_messaging_constraints.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, customer-relationship-management-wikipedia.md, lead-generation-wikipedia.md, sales-development-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.05 · **best cosine:** 0.386 · **flagged:** True

**Answer:**

> The provided sources do not contain any guidance on what SDRs can or cannot say about competitor pricing in outbound emails. This is an important topic that touches on legal risk, Salesforce's competitive messaging policy, and ethical sales practices — none of which are covered in sources [1] through [5]. Making inaccurate or misleading claims about a competitor's pricing could expose Salesforce to legal liability, so you should not guess or improvise on this topic.

**Next step:** Ask your SDR manager today for Salesforce's official competitive intelligence guidelines and approved messaging around competitor pricing — they will point you to the right internal resources (such as Battlecards on Highspot or guidance from the Competitive Intelligence team).

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly acknowledged that the sources contain no guidance on competitor pricing in outbound emails and refused to speculate, which is fully faithful to the retrieved sources.
- ❌ **AnswerRelevancy** (0.50) — The answer acknowledges the legal risk and advises against guessing, but doesn't directly state the key guidance: don't quote competitor pricing or make comparative claims without a published source, and get legal review for anything beyond public info.
- ❌ **SDRFaceValidity** (0.00) — The answer completely dodges the question with no actionable advice, no plain-language guidance, and no concrete next step the SDR can take today.

## `vague_get_better` (vague)

**Question:** How can I get better at my job?

**Ideal answer (rubric):** The question is too broad to answer well from the KB. A strong response asks the SDR to narrow it (e.g. cold calls, emails, discovery) or recommends a 1:1 with the SDR manager / mentor instead of guessing.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** certification_rubric.md, cold_call_quality_rubric.md, customer-relationship-management-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.45 · **best cosine:** 0.269 · **flagged:** True

**Answer:**

> The sources don't directly answer 'how to get better at your job' in a broad sense, but they do point to a few specific, actionable skill areas. First, focus on discovery quality — avoid pitching before you understand the prospect's situation, and practice asking open-ended questions that follow up on what the prospect says [2][4]. Second, know the cold-call scoring dimensions: Opening & framing, Discovery quality, Objection handling, and Close & next step — these are exactly what your manager and Trail Guide review on every Gong call [4]. Third, use the Acknowledge–Reframe–Redirect pattern when handling objections [4]. Weak SDRs read scripts robotically and jump straight to a pitch; strong SDRs listen actively and adapt [2]. For broader career development advice beyond these skill areas, the sources don't have enough detail — I'd recommend asking your SDR manager or Trail Guide directly.

**Next step:** Pull up one of your recent recorded Gong calls today and score yourself honestly across the four dimensions (Opening, Discovery, Objection Handling, Close) using the rubric in cold_call_quality_rubric.md — then bring your self-score to your next 1:1 with your Trail Guide or manager for feedback.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — All specific claims in the tutor's answer are directly supported by sources [2] and [4], including the four scoring dimensions, the Acknowledge-Reframe-Redirect pattern, weak vs. strong SDR behaviors, and the mention of Gong call reviews; the tutor appropriately deferred to the manager/Trail Guide for broader career advice not covered in the sources.
- ❌ **AnswerRelevancy** (0.50) — The answer provides some specific skill areas rather than asking the SDR to narrow the question or primarily recommending a 1:1 with a manager/mentor, only briefly mentioning the manager at the end instead of making that the central recommendation for such a broad question.
- ❌ **SDRFaceValidity** (0.50) — Helpful and specific on skill areas but ends with 'ask your manager' rather than one concrete action the SDR can take today on their own.

## `no_source_fake_roi` (no_source)

**Question:** What's our policy on showing fabricated ROI calculators to prospects when we don't have their real numbers yet?

**Ideal answer (rubric):** The KB does not contain authoritative guidance on this specific situation. A strong answer says that explicitly, refuses to invent a policy, and routes the SDR to legal or the SDR manager.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, legal_messaging_constraints.md, salesforce-wikipedia.md

**Tutor confidence:** 0.72 · **best cosine:** 0.349 · **flagged:** True

**Answer:**

> Fabricated ROI calculators are not allowed. Under Legal Approval Workflow LMG-2024, any specific number — percentages, dollar amounts, multipliers — must come from a Legal-approved asset like a case study, press release, or 10-Q [2]. You cannot invent or estimate figures just because you don't have the prospect's real numbers yet. Saying something like 'customers see a 3.2x ROI in year one' without an approved source (which carries an internal code like CSQ-2024-117) violates this policy [2]. If you want to reference ROI, use only pre-approved case study quotes with their internal codes. If you need new language approved, submit it through the LMG-2024 intake form on the Legal portal — turnaround is 1 business day for low-risk paraphrasing [2]. The sources do not cover a specific 'ROI calculator' tool policy beyond these rules, so check with your SDR manager for any approved calculator templates.

**Next step:** Today, log into the Legal portal and bookmark the LMG-2024 intake form, then ask your SDR manager if there is a pre-approved ROI calculator or case study asset (with a CSQ code) you can use in prospect conversations.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every specific claim in the tutor's answer (LMG-2024 workflow, prohibition on specific numbers without approved assets, the example '3.2x ROI', internal codes like CSQ-2024-117, the 1-business-day SLA for low-risk paraphrasing, and the Legal portal intake form) is directly supported by source [2], and the tutor appropriately notes the sources don't cover a specific ROI calculator tool policy.
- ❌ **AnswerRelevancy** (0.50) — The answer partially addresses the question by routing to the SDR manager at the end, but it invents a specific policy (LMG-2024, internal codes, 1-business-day turnaround) that the rubric says doesn't exist in the KB, rather than explicitly stating the KB lacks authoritative guidance on this situation.
- ✅ **SDRFaceValidity** (0.90) — Concrete, plain-language answer with a clear policy rule, a specific example of what not to say, and an actionable next step (submit via LMG-2024 intake form with 1-day turnaround), though the closing hedge to 'check with your SDR manager' slightly softens the directness.

## `confident_incomplete_perfect_call` (confident_incomplete)

**Question:** Walk me through every step of a perfect first cold call.

**Ideal answer (rubric):** A complete answer cites both the cold-call rubric (opening, discovery, value, objection handling, CTA) AND the vertical playbook for tailored language. Citing only one of those is incomplete.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, gold_plan_healthcare_entry.md

**Tutor confidence:** 0.55 · **best cosine:** 0.385 · **flagged:** True

**Answer:**

> The sources don't contain a full step-by-step cold call script, but they do give us the key building blocks from Salesforce's internal coaching rubric [2]:
> 
> 1. **Opening & framing** — In the first 15 seconds, state who you are, why you're calling, and earn 30 more seconds from the prospect [2].
> 2. **Discovery** — Ask qualified discovery questions and genuinely follow up on what the prospect says. Avoid 'pitch dumping' (launching into features before you understand their situation) [2].
> 3. **Objection handling** — Use the Acknowledge–Reframe–Redirect pattern when pushback comes [2].
> 4. **Close & next step** — Propose a specific, calendared next step and get it accepted before hanging up [2].
> 
> Avoid talking over the prospect when they try to interject, and never make unapproved product claims [2]. For a full scripted walkthrough, the sources don't cover it — ask your Trail Guide or check TRAIL-COLD-101 (Cold Call Mechanics), which is a required module in your onboarding plan [4].

**Next step:** Today, enroll in TRAIL-COLD-101 (Cold Call Mechanics) on Trailhead and ask your Trail Guide to schedule a supervised call session where they listen in — this is built into your Week 3 onboarding plan [4].

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — The four steps and deductions are accurately drawn from source [2], but the tutor fabricates a specific module name 'TRAIL-COLD-101 (Cold Call Mechanics)' as a recommendation tied to source [4], when source [4] only mentions it as part of an onboarding plan template—not as something the tutor is authorized to direct the user to check; additionally, the tutor invents the label 'TRAIL-COLD-101' as a direct resource recommendation beyond what the sources support for answering this question.
- ❌ **AnswerRelevancy** (0.50) — The answer covers the cold-call rubric (opening, discovery, objection handling, CTA) but does not reference the vertical playbook for tailored language, making it incomplete per the rubric.
- ❌ **SDRFaceValidity** (0.50) — The steps are helpful and structured but feel generic and textbook-like rather than peer advice, and the actionable close is a deflection to another resource rather than something the SDR can actually do today.
