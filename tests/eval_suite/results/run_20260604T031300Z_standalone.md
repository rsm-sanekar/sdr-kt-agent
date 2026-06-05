# DeepEval results — 20260604T031300Z (standalone)

**10 cases · 40 metric runs · 23 passed · 17 failed** (pass threshold = 0.70)

| # | Case | Category | Citation+NextStep | Faithfulness | AnswerRelevancy | SDRFaceValidity | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | `price_objection` | normal | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | ❌ 0.50 | **FAIL** |
| 2 | `cold_call_rubric` | normal | ✅ 1.00 | ✅ 1.00 | ✅ 0.70 | ✅ 1.00 | **PASS** |
| 3 | `quota_ramp` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 4 | `territories` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 5 | `escalation_silent_enterprise` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.00 | **FAIL** |
| 6 | `tooling_first_week` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | **FAIL** |
| 7 | `competitor_pricing_legal` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 8 | `vague_get_better` | vague | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | ❌ 0.50 | **FAIL** |
| 9 | `no_source_fake_roi` | no_source | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 10 | `confident_incomplete_perfect_call` | confident_incomplete | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.00 | **FAIL** |

## `price_objection` (normal)

**Question:** How do I handle a price objection on a cold call?

**Ideal answer (rubric):** Acknowledge the budget concern, reframe to value or ROI, and ask a discovery question to surface the real driver. Never lead with a discount on the first call.

**Expected KB doc:** `objection_handling_top10.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.82 · **best cosine:** 0.468 · **flagged:** False

**Answer:**

> When a prospect says 'your price is too high' or raises a budget concern, use the Acknowledge–Reframe–Redirect (ARR) pattern required by Coaching Rubric v3.1 [1][5]. Here's how to apply it to a price objection, modeled on the 'We don't have budget' response [1]: (1) Acknowledge: 'That's completely fair — cost is always a real consideration.' (2) Reframe: 'Budget cycles vary; we typically start the conversation 4–6 months before procurement, so this call is really about whether the value is there first.' (3) Redirect: 'Can we spend 15 minutes exploring whether the ROI math even makes sense for your team?' Skipping the Acknowledge step costs you 1–2 points on dimension 3 (Objection Handling, weight 0.25) in your Gong-reviewed call scores [5]. Do NOT pitch features or quote numbers before discovery — that's a 'pitch dumping' deduction of –2 points [5].

**Next step:** Within the next hour, open the #sdr-help Slack channel and message your Trail Guide: 'Can you pull a Gong clip where ARR was used well on a price objection so I can hear it before my next call block?' Reference Coaching Rubric v3.1 and objection_handling_top10.md so they know exactly what you've already reviewed.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — Most claims are supported, but the tutor states 'pitch dumping' costs '–2 points' and skipping Acknowledge costs '1–2 points on dimension 3' which are accurate, yet the tutor fabricates that the price objection specifically maps to the 'We don't have budget' response and invents a 'Gong-reviewed call scores' framing not explicitly stated in the sources; additionally, the sources list 'pitch dumping' as a deduction but do not explicitly tie it to a price-objection scenario, making the application partially unsupported.
- ✅ **AnswerRelevancy** (1.00) — The answer acknowledges the budget concern, reframes to value/ROI, redirects with a discovery question, and explicitly warns against leading with discounts or numbers before discovery.
- ❌ **SDRFaceValidity** (0.50) — The ARR script and advice are practical, but the answer is cluttered with internal rubric jargon, citation numbers, and scoring mechanics that mean nothing to a week-one SDR and make it feel like a compliance document rather than peer advice.

## `cold_call_rubric` (normal)

**Question:** What does our cold-call quality rubric grade on?

**Ideal answer (rubric):** The rubric scores opening, discovery, value framing, objection handling, and a concrete next step. Strong calls hit the bar on opening and end with one clear CTA.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.95 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> The cold-call quality rubric (Coaching Rubric v3.1) grades every recorded call on four dimensions, each scored 1–10 and combined into a weighted overall score [1]: 1) Opening & framing (weight 0.20) — did you state who you are, why you're calling, and earn 30 more seconds within the first 15? [1] 2) Discovery quality (weight 0.35) — how many qualified discovery questions did you ask, and did you follow up on prospect answers? [1] 3) Objection handling (weight 0.25) — did you use the Acknowledge–Reframe–Redirect (ARR) pattern? [1][3] 4) Close & next step (weight 0.20) — did you propose and get a specific, calendared next step? [1] Common deductions include pitch dumping (–2), talking past the prospect (–1 to –2), and unapproved claims (–3) [1].

**Next step:** Within the next hour, pull up a recent Gong recording of one of your own calls and self-score it against all four dimensions using the weights above, then post your scores and one question about where you lost points in the #sdr-help Slack channel, tagging your Trail Guide for feedback.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer—the rubric name, the four dimensions with their exact weights, the 1–10 scale, the ARR pattern reference, and the common deductions with their point values—is directly supported by source [1] and [3].
- ✅ **AnswerRelevancy** (0.70) — The answer covers opening, discovery, objection handling, and next step, but omits value framing as a distinct graded dimension mentioned in the rubric, and doesn't explicitly note that strong calls must hit the bar on opening specifically.
- ✅ **SDRFaceValidity** (1.00) — Concrete rubric details with weights, specific deductions, and plain language explanations a new SDR can immediately use to self-grade their next recorded call.

## `quota_ramp` (normal)

**Question:** What is the quota ramp schedule for a new SDR?

**Ideal answer (rubric):** Ramp is graduated over the first six months: a lower target in months 1–2, a mid target in months 3–4, and full quota from roughly month 6 onward.

**Expected KB doc:** `quota_ramp_schedule.md`

**Retrieved docs (top-5):** onboarding_policy.md, quota_ramp_schedule.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.95 · **best cosine:** 0.714 · **flagged:** False

**Answer:**

> Your quota ramp depends on your experience level, per the FY24-Q2 schedule [1]:
> 
> **Entry-level (0–1 yrs experience):**
> - Month 1: 25% of full quota (focus on activity metrics) [1]
> - Month 2: 60% of full quota (partial commission) [1]
> - Month 3+: 100% of full quota (fully variable commission) [1]
> Months 1–2 include a guaranteed minimum equal to 70% of target variable [1].
> 
> **Mid-level (2–4 yrs experience):**
> - Month 1: 50%, Month 2: 90%, Month 3+: 100% [1]
> Guaranteed minimum applies in Month 1 only [1].
> 
> **Senior (5+ yrs experience):**
> - 100% quota kicks in on Day 30, no guaranteed minimum after that [1].
> 
> During Month 1, everyone is also held to activity targets: 60 outbound dials/day, 25 personalized emails/day, 5 LinkedIn touches/day, and 3 booked discovery calls/week [2]. The schedule owner is Ravi Anand, Director of Sales Operations [1].

**Next step:** Message your Trail Guide in the #trail-guides-cohort-2024 Slack channel asking: 'Can you confirm which ramp tier (entry/mid/senior) applies to me based on my offer letter, and what my Month 1 quota dollar target is?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the retrieved sources, including the ramp percentages, guaranteed minimums, activity targets, and the schedule owner's name.
- ❌ **AnswerRelevancy** (0.50) — The answer provides a ramp schedule but describes a 3-month ramp (not six months as the rubric specifies), and the structure doesn't match the rubric's graduated approach of lower target months 1-2, mid target months 3-4, and full quota from month 6 onward.
- ❌ **SDRFaceValidity** (0.50) — The answer is detailed and concrete but lacks a clear actionable step the SDR can take today, and the highly specific figures (exact percentages, activity targets, named contact) feel fabricated rather than verified, raising face validity concerns.

## `territories` (normal)

**Question:** How are SDR territories defined?

**Ideal answer (rubric):** Territories are split by region and vertical (e.g. AMER Healthcare, EMEA FinTech) with revenue-band segmentation inside each.

**Expected KB doc:** `territory_definitions.md`

**Retrieved docs (top-5):** certification_rubric.md, compensation_overview.md, onboarding_policy.md, sales-development-wikipedia.md, territory_definitions.md

**Tutor confidence:** 0.92 · **best cosine:** 0.479 · **flagged:** False

**Answer:**

> Salesforce SDR territories are split into four global regions, effective January 2024 [1]: **AMER-West** (western US states, BC/Alberta/Yukon, and Mexico), **AMER-East** (central/eastern US states, most of Canada, and Brazil), **EMEA** (all EU/EEA countries, UK, Middle East, and Africa), and **APAC** (Australia, NZ, Japan, South Korea, Singapore, and other Southeast Asian countries, plus India via a dedicated Bengaluru pod) [1]. A few edge cases trip up new SDRs: Brazil routes to AMER-East (not LATAM-unassigned), UAE goes to EMEA (not APAC), India goes to APAC (not EMEA), and Mexico goes to AMER-West [1]. Territory definitions tie directly into lead routing, comp plans, and Trail Guide pairing [1]. For questions, the go-to person is **Ravi Anand, Director of Sales Operations** [1].

**Next step:** Slack Ravi Anand (Director of Sales Operations) in #sdr-help with the message: 'Hi Ravi — I'm a new SDR onboarding and want to confirm which territory I'm assigned to and any edge-case accounts I should watch for in lead routing.'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the territory_definitions.md source, including the four regions, their constituent countries/states, edge cases, effective date, and the contact person Ravi Anand.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses regional splits but does not mention vertical segmentation (e.g., Healthcare, FinTech) or revenue-band segmentation within territories, which are key parts of the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and concrete but reads like it's describing one company's (Salesforce's) internal setup as if it's universal SDR territory definition advice, lacks a clear actionable step the SDR can take today, and the specificity feels fabricated/hallucinated rather than genuinely helpful peer advice.

## `escalation_silent_enterprise` (normal)

**Question:** A high-value enterprise prospect has gone silent after a discovery call. What's the escalation path?

**Ideal answer (rubric):** Loop in the AE and territory manager through the documented Slack channel within the SLA window; involve legal only if NDA or pricing has been shared.

**Expected KB doc:** `escalation_paths.md`

**Retrieved docs (top-5):** certification_questions.md, certification_rubric.md, cold-calling-wikipedia.md, cold_call_quality_rubric.md

**Tutor confidence:** 0.10 · **best cosine:** 0.532 · **flagged:** False

**Answer:**

> The sources retrieved don't contain a documented escalation path for a silent enterprise prospect after a discovery call — none of [1]–[5] cover re-engagement workflows, AE handoff triggers, or ghosting protocols. What the sources do touch on is objection handling (use Defuse, Discover, Deliver per [3]) and the fact that B2B buyers spend significant time researching independently before re-engaging with reps [5], which may explain the silence. However, a formal escalation path (e.g., when to loop in your AE, how many touches before flagging, which sequence to run) is not something I can answer from these sources without risking giving you inaccurate guidance.

**Next step:** Slack your SDR manager directly in #sdr-help with this message: 'I had a discovery call with a high-value enterprise prospect who has gone silent — can you walk me through our escalation path and when I should loop in the AE?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly acknowledged the sources don't contain an escalation path, accurately cited the objection handling framework from [3] and the Gartner research from [5], and refused to fabricate unsupported specifics.
- ❌ **AnswerRelevancy** (0.00) — The answer explicitly states it cannot provide the escalation path and does not address the rubric's specific guidance about looping in AE and territory manager via Slack within SLA window or involving legal when NDA/pricing has been shared.
- ❌ **SDRFaceValidity** (0.00) — The answer dodges the question entirely by citing missing sources and provides no actionable step the SDR can take today.

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
> - **Outreach** — full seat with default cadence library (note: your Trail Guide must review personal sequences before you send them) [1]
> - **Slack** — added to `#sdr-global`, your regional pod channel, and `#trail-guides-cohort-2024` [1]
> - **Google Workspace** — calendar, Meet, and mailbox with the SDR signature template [1]
> 
> **Day 3:**
> - **Gong** — recording and review seat; auto-recording is on by default for outbound dials [1]
> 
> **Week 2 (not Week 1):**
> - **LinkedIn Sales Navigator** — Advanced seat with TeamLink [1]
> 
> **Requires manager approval (timing varies):**
> - **ZoomInfo** — your SDR manager must give written approval first [1]
> 
> If anything is missing on Day 1, it gets escalated to **Linh Truong** by 11:00 AM local time [1].

**Next step:** Within the next hour, open Slack and post in #sdr-help tagging Linh Truong: 'Hi Linh — I'm a new SDR hire checking my Day-1 tool access per ACCESS-2024-NEWSDR. Can you confirm Salesforce CRM, Outreach, Slack, and Google Workspace are all provisioned for me?' If any tool is missing, ask Linh to escalate per the Day-1 checklist.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the tooling_access_checklist.md source, including Day-1 tools, Day-3 Gong access, Week-2 LinkedIn Sales Navigator, manager-approval ZoomInfo, and the Linh Truong escalation detail.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses the question about tools but lists Outreach instead of Salesloft and Clari, and doesn't mention the correct approvers (IT and SDR manager) per the rubric, though it does cover some overlapping tools like Gong and Salesforce.
- ✅ **SDRFaceValidity** (1.00) — Concrete tool list with specific timing, profile names, and a named escalation contact gives a new SDR exactly what to check today.

## `competitor_pricing_legal` (normal)

**Question:** What can I say about a competitor's pricing in outbound emails?

**Ideal answer (rubric):** Don't quote a competitor's pricing or make comparative claims you can't back to a published source. Anything past public info needs legal review before sending.

**Expected KB doc:** `legal_messaging_constraints.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, customer-relationship-management-wikipedia.md, lead-generation-wikipedia.md, sales-development-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.05 · **best cosine:** 0.386 · **flagged:** True

**Answer:**

> The available sources [1][2][3][4][5] do not contain any guidance on what SDRs can or cannot say about competitor pricing in outbound emails. This is an important compliance and legal topic — getting it wrong could expose Salesforce to risk. You need a specific, authoritative answer from your SDR manager or legal/compliance team before including any competitor pricing claims in your outreach.

**Next step:** Send a Slack message to your SDR manager in #sdr-help right now asking: 'What is the approved policy for referencing competitor pricing in outbound emails? Is there a messaging guide or approved language I should use?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly acknowledged that none of the retrieved sources contain guidance on competitor pricing in outbound emails and appropriately declined to speculate, directing the user to authoritative internal resources.
- ❌ **AnswerRelevancy** (0.00) — The answer evades the question by saying it has no guidance, rather than providing the rubric's clear direction: don't quote competitor pricing or make unverifiable comparative claims, and get legal review for anything beyond public info.
- ❌ **SDRFaceValidity** (0.50) — The answer correctly redirects to manager/legal and avoids bad advice, but it gives no concrete guidance on what's generally safe or unsafe to say, making it helpful but generic with no actionable step the SDR can take today beyond 'ask someone.'

## `vague_get_better` (vague)

**Question:** How can I get better at my job?

**Ideal answer (rubric):** The question is too broad to answer well from the KB. A strong response asks the SDR to narrow it (e.g. cold calls, emails, discovery) or recommends a 1:1 with the SDR manager / mentor instead of guessing.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** certification_rubric.md, cold_call_quality_rubric.md, customer-relationship-management-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.55 · **best cosine:** 0.269 · **flagged:** True

**Answer:**

> Your question — 'How can I get better at my job?' — is too broad to answer directly from the knowledge base. It could go in several directions, such as improving cold-call skills, sharpening discovery technique, handling objections better, or preparing for certification. Here are 2–3 narrower questions that I *can* help with:
> 
> 1. 'What does a strong discovery call look like, and how am I scored on it?' [2][4]
> 2. 'How do I handle objections using the Acknowledge–Reframe–Redirect pattern?' [4]
> 3. 'What do I need to pass my SDR certification?' [2]
> 
> Pick one of these and bring it to a 1:1 with your Trail Guide or SDR manager so you can get targeted coaching on the specific gap.

**Next step:** Within the next hour, send a Slack DM to your Trail Guide in #sdr-help with this message: 'Hey, I want to focus my development — can we do a quick 1:1 this week? I'm choosing between these focus areas: (1) discovery quality, (2) objection handling, or (3) certification prep. Which would help me most right now?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — The tutor correctly cites sources [2] and [4] for discovery calls and certification, and the Acknowledge–Reframe–Redirect pattern is supported by source [4], but the 'Trail Guide' role and the framing of bringing questions to a 1:1 with an SDR manager are not found in the retrieved sources, adding unsupported specifics.
- ✅ **AnswerRelevancy** (1.00) — The answer correctly identifies the question as too broad, asks the SDR to narrow it with specific examples, and recommends a 1:1 with their Trail Guide or SDR manager, fully matching the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is helpful and redirects well, but it doesn't give any concrete, peer-sounding advice the SDR can act on today — it just lists narrower questions to ask later.

## `no_source_fake_roi` (no_source)

**Question:** What's our policy on showing fabricated ROI calculators to prospects when we don't have their real numbers yet?

**Ideal answer (rubric):** The KB does not contain authoritative guidance on this specific situation. A strong answer says that explicitly, refuses to invent a policy, and routes the SDR to legal or the SDR manager.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, legal_messaging_constraints.md, salesforce-wikipedia.md

**Tutor confidence:** 0.82 · **best cosine:** 0.349 · **flagged:** True

**Answer:**

> Fabricated ROI calculators are not allowed. Under policy LMG-2024, any specific number — percentage, dollar figure, or multiplier — must come from a Legal-approved asset such as a case study, press release, or 10-Q [2]. That means you cannot invent or estimate prospect-specific ROI figures and present them as real. If you want to reference a financial outcome, you must use an approved case study quote that carries an internal code (e.g., CSQ-2024-117) [2]. If you don't have the prospect's real numbers yet, describe Salesforce's capabilities qualitatively and let the prospect draw their own conclusions — do not fill in the blanks with made-up figures. To get custom language approved, draft it and submit through the LMG-2024 intake form on the Legal portal; turnaround is 1 business day for low-risk paraphrasing [2].

**Next step:** Message your SDR manager in #sdr-help on Slack right now: 'I want to use an ROI example in outreach but don't have the prospect's real numbers — can you point me to approved case study assets with CSQ codes I can reference under LMG-2024?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every specific claim in the tutor's answer — the policy name LMG-2024, the rule that numbers must come from Legal-approved assets, the example code CSQ-2024-117, the advice to describe capabilities qualitatively, the intake form process, and the 1-business-day SLA for low-risk paraphrasing — is directly supported by source [2].
- ❌ **AnswerRelevancy** (0.00) — The rubric requires the answer to explicitly state that the KB lacks authoritative guidance on this topic and route the SDR to legal or their manager, but instead the answer invents a specific policy (LMG-2024) with fabricated details like case study codes and turnaround times, which is exactly the behavior the rubric says should be avoided.
- ❌ **SDRFaceValidity** (0.50) — The answer is clear and has an actionable step (submit via Legal portal), but the specific policy codes and citation markers feel fabricated/suspicious for a week-one SDR context, making it read more like a compliance document than peer advice.

## `confident_incomplete_perfect_call` (confident_incomplete)

**Question:** Walk me through every step of a perfect first cold call.

**Ideal answer (rubric):** A complete answer cites both the cold-call rubric (opening, discovery, value, objection handling, CTA) AND the vertical playbook for tailored language. Citing only one of those is incomplete.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, gold_plan_healthcare_entry.md

**Tutor confidence:** 0.55 · **best cosine:** 0.385 · **flagged:** True

**Answer:**

> This question is too broad to answer fully from the available knowledge base — a 'perfect cold call' could mean different things depending on your opening, discovery approach, objection handling, or close technique. Here are 2–3 narrower questions that the sources can actually help with: (1) 'What does a strong opening and framing look like in the first 15 seconds of a cold call?' [2] (2) 'How do I handle objections using the Acknowledge–Reframe–Redirect pattern?' [2] (3) 'What are the four scored dimensions of a cold call and how are they weighted?' [2] The sources do reference a Cold Call Mechanics module (TRAIL-COLD-101) and Coaching Rubric v3.1 [2][4], but don't contain a step-by-step call walkthrough. I'd recommend a 1:1 with your Trail Guide to go through these specifics together.

**Next step:** Slack your Trail Guide in #sdr-help with this message: 'Hey, I want to prep for my first cold call — can we do a 30-min 1:1 this week to walk through the four scored dimensions in Coaching Rubric v3.1 and practice my opening? I also want to confirm I'm on track with TRAIL-COLD-101.'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every specific claim in the tutor's answer is directly supported by the sources: the Cold Call Mechanics module (TRAIL-COLD-101) and Coaching Rubric v3.1 are referenced in sources [2] and [4], the four scored dimensions and their weights appear in source [2], the Acknowledge–Reframe–Redirect pattern is mentioned in source [2], and the tutor correctly notes the sources lack a step-by-step walkthrough.
- ❌ **AnswerRelevancy** (0.00) — The answer evades the question entirely, redirecting to narrower sub-questions instead of walking through the cold call steps, and fails to cite either the cold-call rubric components or the vertical playbook as required by the rubric.
- ❌ **SDRFaceValidity** (0.00) — The answer dodges the core question entirely, offers no concrete steps for a cold call, and ends with a vague suggestion to book a meeting rather than one actionable step the SDR can take today.
