# DeepEval results — 20260603T223558Z (standalone)

**10 cases · 40 metric runs · 20 passed · 20 failed** (pass threshold = 0.70)

| # | Case | Category | Citation+NextStep | Faithfulness | AnswerRelevancy | SDRFaceValidity | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | `price_objection` | normal | ✅ 1.00 | ❌ 0.50 | ✅ 0.90 | ❌ 0.50 | **FAIL** |
| 2 | `cold_call_rubric` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 3 | `quota_ramp` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 4 | `territories` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 5 | `escalation_silent_enterprise` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 6 | `tooling_first_week` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 7 | `competitor_pricing_legal` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 8 | `vague_get_better` | vague | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | ✅ 0.80 | **FAIL** |
| 9 | `no_source_fake_roi` | no_source | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 10 | `confident_incomplete_perfect_call` | confident_incomplete | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |

## `price_objection` (normal)

**Question:** How do I handle a price objection on a cold call?

**Ideal answer (rubric):** Acknowledge the budget concern, reframe to value or ROI, and ask a discovery question to surface the real driver. Never lead with a discount on the first call.

**Expected KB doc:** `objection_handling_top10.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.55 · **best cosine:** 0.468 · **flagged:** False

**Answer:**

> The sources don't include a specific script for a price objection, but they give you the framework to handle it. Use the Acknowledge–Reframe–Redirect (ARR) pattern, which is required on every objection call [1][5]. Here's how to apply it to price: Acknowledge ('I hear you — cost is always a real consideration.'), Reframe (shift focus to value or timing, similar to the budget objection: 'We typically start the conversation 4–6 months before procurement so you can plan.' [1]), Redirect (book a discovery call to explore ROI before price even becomes a formal blocker). Skipping the Acknowledge step costs you 1–2 points on Dimension 3 of your coaching rubric [1][5], so never jump straight to defending the price. The sources don't have a word-for-word price objection script, so ask your Trail Guide or SDR manager for a proven example specific to your segment.

**Next step:** Today, pull up objection_handling_top10.md and practice the ARR pattern out loud for the 'We don't have budget' objection (#4) — it's the closest match to a price objection — then ask your Trail Guide to role-play a price objection with you before your next call block.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — The ARR pattern, rubric deduction, and budget reframe quote are all supported by sources [1][5], but the tutor invents a specific price objection acknowledgement script ('I hear you — cost is always a real consideration') and a redirect strategy ('book a discovery call to explore ROI before price becomes a formal blocker') that are not present in any retrieved source, and it also incorrectly cites [5] for the ARR requirement when [5] only references [1] for that pattern.
- ✅ **AnswerRelevancy** (0.90) — The answer acknowledges the concern, reframes to value, redirects to discovery, and explicitly avoids leading with a discount, covering all rubric elements well.
- ❌ **SDRFaceValidity** (0.50) — The ARR framework and coaching rubric references feel abstract and internally sourced rather than peer-level street advice, and while it ends with an action (ask your manager for a script), it doesn't give the SDR anything concrete to actually say on a call today.

## `cold_call_rubric` (normal)

**Question:** What does our cold-call quality rubric grade on?

**Ideal answer (rubric):** The rubric scores opening, discovery, value framing, objection handling, and a concrete next step. Strong calls hit the bar on opening and end with one clear CTA.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.95 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> The cold-call quality rubric (v3.1) grades every Gong-sampled call on four dimensions, each scored 1–10 and combined into a weighted overall score [1]: (1) Opening & framing (weight 0.20) — did you state who you are, why you're calling, and earn 30 more seconds within the first 15? [1] (2) Discovery quality (weight 0.35) — how many qualified discovery questions did you ask and how well did you follow up on answers? [1] (3) Objection handling (weight 0.25) — did you use the Acknowledge–Reframe–Redirect (ARR) pattern? [1][3] (4) Close & next step (weight 0.20) — did you propose and get a specific, calendared next step? [1] Watch out for common deductions: talking past the prospect (–1 to –2), pitch dumping before discovery (–2), and unapproved claims (–3) [1].

**Next step:** Pull up cold_call_quality_rubric.md today and score one of your own recent practice calls against all four dimensions before your next Trail Guide session.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer—the four dimensions, their weights, the 1–10 scale, the ARR pattern requirement, and the common deductions—is directly supported by source [1] (cold_call_quality_rubric.md) and source [3] (objection_handling_top10.md).
- ❌ **AnswerRelevancy** (0.50) — The answer covers opening, discovery, objection handling, and next step, but omits 'value framing' as a graded dimension mentioned in the rubric, and doesn't explicitly note that strong calls must hit the bar on opening with one clear CTA.
- ❌ **SDRFaceValidity** (0.50) — The answer is detailed and structured but reads like documentation rather than peer advice, and it lacks a single concrete action the SDR can take today.

## `quota_ramp` (normal)

**Question:** What is the quota ramp schedule for a new SDR?

**Ideal answer (rubric):** Ramp is graduated over the first six months: a lower target in months 1–2, a mid target in months 3–4, and full quota from roughly month 6 onward.

**Expected KB doc:** `quota_ramp_schedule.md`

**Retrieved docs (top-5):** onboarding_policy.md, quota_ramp_schedule.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.95 · **best cosine:** 0.714 · **flagged:** False

**Answer:**

> Your quota ramp depends on your experience level [1]:
> 
> **Entry-level (0–1 years sales experience):**
> - Month 1: 25% of full quota (focus on activity, not bookings)
> - Month 2: 60% of full quota
> - Month 3+: 100% of full quota
> Months 1–2 include a guaranteed minimum of 70% of target variable pay [1].
> 
> **Mid-level (2–4 years experience):**
> - Month 1: 50%, Month 2: 90%, Month 3+: 100%
> Guaranteed minimum applies in Month 1 only [1].
> 
> **Senior (5+ years experience):**
> - 100% quota starts on Day 30, no guaranteed minimum after that [1].
> 
> During Month 1, all SDRs are also held to activity targets: 60 outbound dials/day, 25 personalized emails/day, 5 LinkedIn touches/day, and 3 booked discovery calls/week [2].
> 
> This schedule applies to SDRs with start dates between April 1, 2024 and March 31, 2025. The owner is Ravi Anand, Director of Sales Operations [1].

**Next step:** Confirm your experience level with your SDR manager today so you know exactly which ramp tier applies to you, and ask them to share your specific full quota number so you can calculate your Month 1 and Month 2 targets.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the retrieved sources, including the ramp percentages, guaranteed minimums, activity targets, date range, and owner name.
- ❌ **AnswerRelevancy** (0.50) — The answer provides a graduated ramp schedule but structures it as 3-month ramp rather than the rubric's 6-month graduated schedule (lower in months 1-2, mid in months 3-4, full quota from month 6), so it partially addresses the question but doesn't match the expected timeline.
- ❌ **SDRFaceValidity** (0.50) — The answer is detailed and well-structured but reads more like a policy document than peer advice, and it lacks a concrete action the SDR should take today.

## `territories` (normal)

**Question:** How are SDR territories defined?

**Ideal answer (rubric):** Territories are split by region and vertical (e.g. AMER Healthcare, EMEA FinTech) with revenue-band segmentation inside each.

**Expected KB doc:** `territory_definitions.md`

**Retrieved docs (top-5):** certification_rubric.md, compensation_overview.md, onboarding_policy.md, sales-development-wikipedia.md, territory_definitions.md

**Tutor confidence:** 0.95 · **best cosine:** 0.479 · **flagged:** False

**Answer:**

> Salesforce SDR territories are split into four global regions, effective January 2024 [1]: **AMER-West** (western US states, BC/Alberta/Yukon, and Mexico), **AMER-East** (central/eastern US states, eastern Canada, and Brazil), **EMEA** (all EU/EEA countries, UK, Middle East, and Africa), and **APAC** (Australia, NZ, Japan, South Korea, Singapore, and other Southeast Asian countries, plus India). A few edge cases trip up new SDRs most often [1]: Brazil routes to AMER-East (not LATAM-unassigned), UAE goes to EMEA (not APAC), India goes to APAC (not EMEA), Mexico goes to AMER-West, and South Africa is the only sub-Saharan country with a dedicated SDR seat in EMEA. These definitions drive lead routing, comp plans, and Trail Guide pairings [1]. For any territory questions, reach out to **Ravi Anand, Director of Sales Operations** [1].

**Next step:** Open territory_definitions.md today and quiz yourself on the five common edge cases (Brazil, UAE, India, Mexico, South Africa) — then Slack Ravi Anand to confirm which territory you are assigned to.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the territory_definitions.md source, including the four regions, their constituent countries/states, the edge cases, the January 2024 effective date, and the contact person Ravi Anand.
- ❌ **AnswerRelevancy** (0.50) — The answer covers regional splits but omits the vertical dimension (e.g., Healthcare, FinTech) and revenue-band segmentation that the rubric requires.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and concrete but reads like it's citing internal Salesforce documentation that may not apply to the SDR's actual company, making it potentially misleading rather than genuinely actionable peer advice; the one action (contact Ravi Anand) is good but only useful if this is actually the SDR's org.

## `escalation_silent_enterprise` (normal)

**Question:** A high-value enterprise prospect has gone silent after a discovery call. What's the escalation path?

**Ideal answer (rubric):** Loop in the AE and territory manager through the documented Slack channel within the SLA window; involve legal only if NDA or pricing has been shared.

**Expected KB doc:** `escalation_paths.md`

**Retrieved docs (top-5):** certification_questions.md, certification_rubric.md, cold-calling-wikipedia.md, cold_call_quality_rubric.md

**Tutor confidence:** 0.10 · **best cosine:** 0.532 · **flagged:** False

**Answer:**

> The provided sources do not contain a specific escalation path for re-engaging a silent enterprise prospect after a discovery call. None of the five sources cover post-discovery follow-up workflows, account escalation procedures, or ghosting playbooks. The only escalation path mentioned in the sources relates to low call-quality scores (below 5), which are reviewed by the SDR's manager and Priya Subramanian within five business days [1] — but that's a coaching escalation, not a prospect re-engagement process. For your specific situation, your SDR manager is the right person to ask. They can walk you through Salesforce's internal playbook for re-engaging silent enterprise accounts, including whether to loop in your AE, use an executive sponsor, or trigger a formal account escalation.

**Next step:** Book 15 minutes with your SDR manager today and ask specifically: 'What is our escalation path when a high-value enterprise prospect goes dark after discovery?' — bring the account name and a summary of the discovery call so they can give you tailored guidance.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly acknowledged the sources don't cover the topic, accurately cited the only relevant escalation detail (scores below 5 reviewed by manager and Priya Subramanian within five business days from source [1]), and appropriately deferred to the SDR manager rather than fabricating a playbook.
- ❌ **AnswerRelevancy** (0.00) — The answer does not provide the specific escalation path (loop in AE and territory manager via documented Slack channel within SLA window, involve legal only if NDA/pricing shared) and instead deflects to asking the SDR manager.
- ❌ **SDRFaceValidity** (0.50) — Honest about its limitations and ends with a concrete action (ask your manager), but gives no actual re-engagement advice a new SDR could use today.

## `tooling_first_week` (normal)

**Question:** Which tools should I have access to in my first week as an SDR?

**Ideal answer (rubric):** Core stack: Salesforce, Salesloft, Gong, and Clari. Request access through the tooling checklist, with IT and the SDR manager as approvers.

**Expected KB doc:** `tooling_access_checklist.md`

**Retrieved docs (top-5):** onboarding_policy.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.95 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> Here's what you should have access to in your first week, broken down by timing:
> 
> **Day 1 (before your first login):** [1]
> - **Salesforce CRM** — production org with the SDR Standard profile
> - **Outreach** — full seat with default cadence library (note: your Trail Guide must review personal sequences before you send them)
> - **Slack** — added to #sdr-global, your regional pod channel, and #trail-guides-cohort-2024
> - **Google Workspace** — calendar, Meet, and a mailbox with the SDR signature template
> 
> **Day 3:** [1]
> - **Gong** — recording and review seat (auto-recording is on by default for all outbound dials)
> 
> **Week 2:** [1]
> - **LinkedIn Sales Navigator** — Advanced seat with TeamLink (subject to regional license availability)
> 
> **Requires manager approval (anytime):** [1]
> - **ZoomInfo** — your SDR manager must give written approval; provisioning takes up to 2 business days after that.
> 
> If anything is missing on Day 1, it gets escalated to Linh Truong by 11:00 AM. [1]

**Next step:** On Day 1, log into each of the four tools (Salesforce CRM, Outreach, Slack, Google Workspace) and confirm they're working. If any are missing, flag it to Linh Truong immediately — escalation happens at 11:00 AM local time. [1]

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the tooling_access_checklist.md source, including Day-1 tools, Day-3 Gong access, Week-2 LinkedIn Sales Navigator, ZoomInfo approval requirements, and the Linh Truong escalation detail.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses the question about tools but mentions Outreach instead of Salesloft and Clari, and doesn't mention the tooling checklist with IT and SDR manager as approvers per the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and well-structured but reads like it was pulled from a company-specific onboarding doc with invented details (Linh Truong, Trail Guide, cohort names) that won't apply to this SDR, making it helpful in format but potentially misleading in content, and it lacks a clear single action the SDR can take today.

## `competitor_pricing_legal` (normal)

**Question:** What can I say about a competitor's pricing in outbound emails?

**Ideal answer (rubric):** Don't quote a competitor's pricing or make comparative claims you can't back to a published source. Anything past public info needs legal review before sending.

**Expected KB doc:** `legal_messaging_constraints.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, customer-relationship-management-wikipedia.md, lead-generation-wikipedia.md, sales-development-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.05 · **best cosine:** 0.386 · **flagged:** True

**Answer:**

> The provided sources do not contain any guidance on what you can or cannot say about a competitor's pricing in outbound emails. This is an important topic that touches on legal risk, Salesforce's competitive messaging policy, and ethical sales practices — none of which are covered in sources [1] through [5]. Getting this wrong could expose you or Salesforce to legal liability, so please don't guess.

**Next step:** Reach out to your SDR manager today and ask specifically: 'What is Salesforce's policy on referencing competitor pricing in outbound emails?' They can point you to the official competitive intelligence guidelines or connect you with the right enablement resource.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly acknowledged that the sources contain no guidance on competitor pricing in outbound emails and refused to speculate, which is fully faithful to the retrieved sources.
- ❌ **AnswerRelevancy** (0.00) — The answer evades the question entirely by claiming no guidance exists, rather than providing the rubric's direction to avoid quoting competitor pricing or making unverifiable comparative claims without legal review.
- ❌ **SDRFaceValidity** (0.50) — Honest about its limitations and flags real risk, but gives the new SDR zero actionable guidance on what to actually do next (e.g., who to ask, where to find the policy).

## `vague_get_better` (vague)

**Question:** How can I get better at my job?

**Ideal answer (rubric):** The question is too broad to answer well from the KB. A strong response asks the SDR to narrow it (e.g. cold calls, emails, discovery) or recommends a 1:1 with the SDR manager / mentor instead of guessing.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** certification_rubric.md, cold_call_quality_rubric.md, customer-relationship-management-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.55 · **best cosine:** 0.269 · **flagged:** True

**Answer:**

> The sources don't directly answer 'how to get better at your job' in a broad sense, but they do point to a few specific, actionable skill areas. First, focus on discovery quality — avoid pitching before you understand the prospect's situation, ask open-ended questions, and follow up on their answers rather than sticking to a fixed script [2][4]. Second, master objection handling using the Acknowledge–Reframe–Redirect pattern [4]. Third, always close calls with a specific, calendared next step [4]. Your cold calls are scored across these dimensions (opening, discovery, objection handling, and close) on a 1–10 scale, and your manager and Trail Guide review them weekly via Gong [4]. The clearest path to improvement is reviewing your own recorded calls, identifying which dimension scores lowest, and working with your Trail Guide on targeted drills like a discovery question bank or active-listening exercises [2][4]. For broader career development guidance beyond these sources, ask your SDR manager directly.

**Next step:** Pull up one of your recent Gong-recorded cold calls today, score yourself honestly on the four dimensions (opening, discovery, objection handling, close), and bring your self-assessment to your next Trail Guide or manager 1:1.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — Most claims are supported by sources [2] and [4], but the tutor states calls are reviewed 'weekly via Gong' and that 'your manager and Trail Guide review them' — the rubric mentions Gong sampling and Trail Guides but does not explicitly state weekly Gong reviews with both manager and Trail Guide present, making that a partially unsupported specific claim.
- ❌ **AnswerRelevancy** (0.50) — The answer provides specific tips rather than asking the SDR to narrow the question or primarily recommending a 1:1 with their manager/mentor, only briefly mentioning the manager at the end.
- ✅ **SDRFaceValidity** (0.80) — Concrete and specific with real frameworks (Acknowledge-Reframe-Redirect, Gong call reviews, Trail Guide), but the actionable step is slightly buried and the citation-style references feel a bit formal for peer advice.

## `no_source_fake_roi` (no_source)

**Question:** What's our policy on showing fabricated ROI calculators to prospects when we don't have their real numbers yet?

**Ideal answer (rubric):** The KB does not contain authoritative guidance on this specific situation. A strong answer says that explicitly, refuses to invent a policy, and routes the SDR to legal or the SDR manager.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, legal_messaging_constraints.md, salesforce-wikipedia.md

**Tutor confidence:** 0.72 · **best cosine:** 0.349 · **flagged:** True

**Answer:**

> Fabricated ROI calculators are not allowed. Under Legal Approval Workflow LMG-2024, any specific number — a percentage, dollar amount, or multiplier — must come from a Legal-approved asset such as a case study, press release, or 10-Q [2]. That means you cannot invent or estimate ROI figures for a prospect just because you don't have their real numbers yet. Approved case-study quotes have an internal code (e.g., CSQ-2024-117) that you can reference safely [2]. If you want to share a financial claim, you must first submit the proposed language through the LMG-2024 intake form on the Legal portal; turnaround is 1 business day for low-risk paraphrasing [2]. The sources do not cover a specific 'ROI calculator tool' policy beyond this, so for further detail ask your SDR manager or Sales Counsel Sasha Lindgren.

**Next step:** Today, log into the Legal portal, bookmark the LMG-2024 intake form, and review the list of already-approved case-study assets (look for CSQ codes) so you have compliant proof points ready to use in your outreach without needing to fabricate any numbers.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every specific claim in the tutor's answer (LMG-2024 workflow, prohibition on specific numbers without Legal-approved assets, case-study quote codes, intake form, 1-business-day SLA for low-risk paraphrasing, and Sasha Lindgren as Sales Counsel) is directly supported by source [2], and the tutor correctly notes the sources don't cover an ROI calculator tool specifically.
- ❌ **AnswerRelevancy** (0.50) — The answer partially addresses the question by routing to the SDR manager, but instead of explicitly stating the KB lacks authoritative guidance on this specific situation and refusing to invent policy, it fabricates specific policy details (LMG-2024, CSQ codes, Sasha Lindgren) that aren't confirmed to exist in the KB, which is the opposite of what the rubric requires.
- ❌ **SDRFaceValidity** (0.50) — The answer is clear and policy-grounded but feels procedural rather than peer-like, and the actionable step (submit the LMG-2024 intake form) is buried and vague for a week-one SDR who likely doesn't know where the Legal portal is.

## `confident_incomplete_perfect_call` (confident_incomplete)

**Question:** Walk me through every step of a perfect first cold call.

**Ideal answer (rubric):** A complete answer cites both the cold-call rubric (opening, discovery, value, objection handling, CTA) AND the vertical playbook for tailored language. Citing only one of those is incomplete.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, gold_plan_healthcare_entry.md

**Tutor confidence:** 0.45 · **best cosine:** 0.385 · **flagged:** True

**Answer:**

> The sources don't contain a full step-by-step cold call script, but they do give you the four key phases your manager will score you on [2]: 
> 
> 1. **Opening & framing** — Within the first 15 seconds, state who you are, why you're calling, and earn 30 more seconds [2]. 
> 2. **Discovery** — Ask qualified discovery questions and genuinely follow up on what the prospect says. Avoid 'pitch dumping' (launching into features before you've learned anything) [2]. 
> 3. **Objection handling** — Use the Acknowledge–Reframe–Redirect pattern when pushback comes [2]. 
> 4. **Close & next step** — Propose a specific, calendared next step and get it accepted before you hang up [2]. 
> 
> Avoid talking over the prospect when they try to interject — that's an automatic deduction [2]. Modern best practice also suggests researching the prospect before calling so you can tailor your opener to their situation [3].
> 
> For a full scripted walkthrough, your sources don't cover it — ask your Trail Guide.

**Next step:** Pull up Coaching Rubric v3.1 with your Trail Guide today and ask them to walk you through a recorded 9–10 score call so you can hear all four dimensions in action before your first supervised dial.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — All four steps and deductions cited are directly supported by source [2] (the rubric), and the 'warm calling' research mention is supported by source [3]; the tutor correctly acknowledges the sources don't cover a full scripted walkthrough.
- ❌ **AnswerRelevancy** (0.50) — The answer covers the cold-call rubric phases (opening, discovery, objection handling, CTA) but does not reference the vertical playbook for tailored language, making it incomplete per the rubric.
- ❌ **SDRFaceValidity** (0.50) — The four phases are helpful and concrete but read more like a rubric than peer advice, and the answer ends by deflecting to a 'Trail Guide' instead of giving one specific action the SDR can take today.
