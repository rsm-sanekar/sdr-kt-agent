# DeepEval results — 20260604T031203Z (standalone)

**10 cases · 40 metric runs · 24 passed · 16 failed** (pass threshold = 0.70)

| # | Case | Category | Citation+NextStep | Faithfulness | AnswerRelevancy | SDRFaceValidity | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | `price_objection` | normal | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | ❌ 0.50 | **FAIL** |
| 2 | `cold_call_rubric` | normal | ✅ 1.00 | ✅ 1.00 | ✅ 0.70 | ✅ 1.00 | **PASS** |
| 3 | `quota_ramp` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 4 | `territories` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 5 | `escalation_silent_enterprise` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 6 | `tooling_first_week` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | **FAIL** |
| 7 | `competitor_pricing_legal` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 8 | `vague_get_better` | vague | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | **FAIL** |
| 9 | `no_source_fake_roi` | no_source | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 10 | `confident_incomplete_perfect_call` | confident_incomplete | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.00 | **FAIL** |

## `price_objection` (normal)

**Question:** How do I handle a price objection on a cold call?

**Ideal answer (rubric):** Acknowledge the budget concern, reframe to value or ROI, and ask a discovery question to surface the real driver. Never lead with a discount on the first call.

**Expected KB doc:** `objection_handling_top10.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.72 · **best cosine:** 0.468 · **flagged:** False

**Answer:**

> When a prospect says 'your price is too high' or raises a budget concern on a cold call, use the Acknowledge–Reframe–Redirect (ARR) pattern required by Coaching Rubric v3.1 [5]. The closest match in the sources is the 'We don't have budget' objection [1]: (1) Acknowledge — validate their concern without arguing; (2) Reframe — 'Budget cycles vary; we typically start the conversation 4–6 months before procurement' [1]; (3) Redirect — propose a future-dated discovery call to explore fit before price becomes the blocker [1]. Skipping the Acknowledge step costs you 1–2 points on dimension 3 of your call score [1][5]. Do NOT pitch features or justify price before doing discovery — that's flagged as 'pitch dumping' and costs –2 points [5]. Keep the goal simple: book the next conversation, not close a deal on the cold call.

**Next step:** Within the next hour, open the #sdr-help Slack channel and message your Trail Guide: 'Can you pull a Gong clip where someone handled a price objection well using ARR? I want to see dimension 3 scored 7+ so I can model the exact language before my next call block.'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — Most claims are supported, but the tutor applies the 'We don't have budget' objection's reframe ('Budget cycles vary; we typically start the conversation 4–6 months before procurement') to a generic 'price is too high' objection, which is a stretch not explicitly supported by the sources, and the '–2 points' deduction for pitch dumping is described in source [5] as '–2' but the source text is cut off and doesn't explicitly confirm the exact framing used.
- ✅ **AnswerRelevancy** (1.00) — The answer acknowledges the concern, reframes to value/timing, redirects with a discovery question, and explicitly warns against leading with discounts or pitching features before discovery.
- ❌ **SDRFaceValidity** (0.50) — The ARR framework and advice are solid and practical, but the answer is cluttered with internal rubric references (scoring points, 'Coaching Rubric v3.1') that mean nothing to a week-one SDR and distract from the core guidance, and it lacks a single concrete action to take today.

## `cold_call_rubric` (normal)

**Question:** What does our cold-call quality rubric grade on?

**Ideal answer (rubric):** The rubric scores opening, discovery, value framing, objection handling, and a concrete next step. Strong calls hit the bar on opening and end with one clear CTA.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.95 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> The cold-call quality rubric (Coaching Rubric v3.1) grades every Gong-sampled call on four dimensions, each scored 1–10 and combined into a weighted overall score [1]: 1) Opening & framing (weight 0.20) — did you state who you are, why you're calling, and earn 30 more seconds within the first 15? [1] 2) Discovery quality (weight 0.35) — how many qualified discovery questions did you ask, and how well did you follow up on prospect answers? [1] 3) Objection handling (weight 0.25) — did you use the Acknowledge–Reframe–Redirect (ARR) pattern? [1][3] 4) Close & next step (weight 0.20) — did you propose and get a specific, calendared next step? [1] Common deductions include pitch dumping (–2), talking past the prospect (–1 to –2), and unapproved claims (–3) [1].

**Next step:** Post a message in #sdr-help tagging your Trail Guide asking them to share a sample scored call from Gong so you can see how each of the four rubric dimensions is marked in a real review.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer—the rubric name, four dimensions, their weights, scoring scale, and common deductions—is directly supported by source [1], and the ARR pattern reference is corroborated by source [3].
- ✅ **AnswerRelevancy** (0.70) — The answer covers opening, discovery, objection handling, and next step, but omits value framing as a graded dimension mentioned in the rubric, and doesn't explicitly note that strong calls must hit the bar on opening specifically.
- ✅ **SDRFaceValidity** (1.00) — Concrete dimensions with weights, plain peer-level language, specific deduction examples, and an implicit action (know the ARR pattern and nail your opener in 15 seconds) a new SDR can apply on their next call today.

## `quota_ramp` (normal)

**Question:** What is the quota ramp schedule for a new SDR?

**Ideal answer (rubric):** Ramp is graduated over the first six months: a lower target in months 1–2, a mid target in months 3–4, and full quota from roughly month 6 onward.

**Expected KB doc:** `quota_ramp_schedule.md`

**Retrieved docs (top-5):** onboarding_policy.md, quota_ramp_schedule.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.92 · **best cosine:** 0.714 · **flagged:** False

**Answer:**

> Your quota ramp depends on your prior sales experience [1]. Here's the breakdown for FY24-Q2 (start dates April 1, 2024 – March 31, 2025) [1]:
> 
> **Entry-level (0–1 yrs experience):**
> - Month 1: 25% of full quota (activity focus, no bookings pressure) [1]
> - Month 2: 60% of full quota (partial commission) [1]
> - Month 3+: 100% of full quota (full commission) [1]
> Months 1–2 have a guaranteed minimum of 70% of target variable [1].
> 
> **Mid-level (2–4 yrs experience):**
> - Month 1: 50%, Month 2: 90%, Month 3+: 100% [1]
> Guaranteed minimum in Month 1 only [1].
> 
> **Senior (5+ yrs experience):**
> - 100% quota on Day 30, no guaranteed minimum after that [1].
> 
> During Month 1, everyone must also hit activity targets: 60 outbound dials/day, 25 personalized emails/day, 5 LinkedIn touches/day, and 3 booked discovery calls/week [2]. Quota owner is Ravi Anand, Director of Sales Operations [1].

**Next step:** Send a Slack DM to your Trail Guide in #trail-guides-cohort-2024 asking: 'Can you confirm which ramp tier applies to me (entry/mid/senior) and what my Month 1 quota dollar target is?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the retrieved sources, including ramp percentages, guaranteed minimums, activity targets, and the quota owner's name.
- ❌ **AnswerRelevancy** (0.50) — The answer provides a detailed ramp schedule but shows full quota reached at Month 3+ rather than Month 6 as the rubric specifies, only partially matching the expected graduated timeline.
- ❌ **SDRFaceValidity** (0.50) — The answer is detailed and well-structured but reads more like a policy document than peer advice, and it lacks a concrete action the SDR can take today.

## `territories` (normal)

**Question:** How are SDR territories defined?

**Ideal answer (rubric):** Territories are split by region and vertical (e.g. AMER Healthcare, EMEA FinTech) with revenue-band segmentation inside each.

**Expected KB doc:** `territory_definitions.md`

**Retrieved docs (top-5):** certification_rubric.md, compensation_overview.md, onboarding_policy.md, sales-development-wikipedia.md, territory_definitions.md

**Tutor confidence:** 0.93 · **best cosine:** 0.479 · **flagged:** False

**Answer:**

> Salesforce divides the SDR org into four global territories, effective January 2024 [1]: **AMER-West** (western US states, BC/Alberta/Yukon, and Mexico), **AMER-East** (central/eastern US states, most of Canada, and Brazil — note Brazil is AMER-East, not LATAM-unassigned [1]), **EMEA** (all EU/EEA, UK, Middle East, Africa — note UAE and Israel are EMEA, not APAC [1]), and **APAC** (Australia, NZ, Japan, South Korea, Singapore, and others — India is APAC with its own Bengaluru pod, not EMEA [1]). These territory definitions drive lead routing, comp plans, and Trail Guide pairings [1]. A few edge cases trip up new SDRs most often: Brazil→AMER-East, UAE→EMEA, India→APAC, Mexico→AMER-West [1]. For territory questions, the go-to person is **Ravi Anand, Director of Sales Operations** [1].

**Next step:** Send a Slack DM to your Trail Guide in #sdr-help asking: 'Can you confirm which territory I'm assigned to and walk me through one edge-case country from the territory_definitions doc so I can practice routing it correctly?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the territory_definitions.md source, including the four territories, their constituent regions, edge cases, effective date, and the contact person Ravi Anand.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses geographic territory splits but does not mention vertical segmentation (e.g., Healthcare, FinTech) or revenue-band segmentation within territories, which are key parts of the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and concrete but reads like it's citing an internal document with suspicious precision (exact names, dates, edge cases) that can't be verified, and while it names a contact person, it lacks a clear single action the SDR should take today.

## `escalation_silent_enterprise` (normal)

**Question:** A high-value enterprise prospect has gone silent after a discovery call. What's the escalation path?

**Ideal answer (rubric):** Loop in the AE and territory manager through the documented Slack channel within the SLA window; involve legal only if NDA or pricing has been shared.

**Expected KB doc:** `escalation_paths.md`

**Retrieved docs (top-5):** certification_questions.md, certification_rubric.md, cold-calling-wikipedia.md, cold_call_quality_rubric.md

**Tutor confidence:** 0.10 · **best cosine:** 0.532 · **flagged:** False

**Answer:**

> The sources retrieved cover cold-call quality, objection handling, and general B2B buying behavior, but none of them describe a specific escalation path for a high-value enterprise prospect who goes silent after a discovery call [1][2][3]. That process — including when to loop in your AE, how many follow-up touches to attempt, and what sequences or tools to use — is not documented in the available knowledge base. You'll need to get that guidance directly from your SDR manager or assigned AE.

**Next step:** Send a Slack message to your SDR manager in #sdr-help right now with this exact ask: 'I have a high-value enterprise prospect who went silent after a discovery call — what is our escalation path and at what point do I loop in the AE?' If you don't know your #sdr-help channel name, ask your Trail Guide to confirm it.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly identified that none of the retrieved sources address an escalation path for a silent enterprise prospect and refused to speculate, directing the user to their manager or AE instead.
- ❌ **AnswerRelevancy** (0.00) — The answer explicitly states it cannot provide the escalation path and redirects to a manager, failing to cover the rubric's specific steps about looping in AE and territory manager via Slack within SLA window.
- ❌ **SDRFaceValidity** (0.50) — Honest about knowledge gaps and correctly redirects to manager/AE, but gives zero concrete next steps the SDR could take today, making it helpful but not actionable.

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
> - **Gong** — recording and review seat; auto-recording is on by default for all outbound dials [1]
> 
> **Week 2 (not Week 1):**
> - **LinkedIn Sales Navigator** — Advanced seat with TeamLink [1]
> 
> **Requires manager approval (timing varies):**
> - **ZoomInfo** — your SDR manager must give written approval first; provisioning takes up to 2 business days after that [1]
> 
> If anything is missing on Day 1, the escalation point is **Linh Truong** by 11:00 AM local time [1].

**Next step:** Open Slack and post in #sdr-help tagging Linh Truong: 'Hi Linh — I'm a new SDR hire checking my Day-1 access against ticket ACCESS-2024-NEWSDR. Can you confirm Salesforce CRM, Outreach, Slack, and Google Workspace are all provisioned for me?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the tooling_access_checklist.md source, including Day-1 tools, Day-3 Gong access, Week-2 LinkedIn Sales Navigator, ZoomInfo approval requirements, and the Linh Truong escalation point.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses the question about tools but mentions different tools (Outreach instead of Salesloft, ZoomInfo instead of Clari) and doesn't match the rubric's core stack of Salesforce, Salesloft, Gong, and Clari, though it does cover the general topic of first-week tool access.
- ✅ **SDRFaceValidity** (1.00) — Concrete, specific tool names with access tiers and timing, peer-level tone, and ends with a clear actionable escalation step (contact Linh Truong by 11 AM if anything is missing).

## `competitor_pricing_legal` (normal)

**Question:** What can I say about a competitor's pricing in outbound emails?

**Ideal answer (rubric):** Don't quote a competitor's pricing or make comparative claims you can't back to a published source. Anything past public info needs legal review before sending.

**Expected KB doc:** `legal_messaging_constraints.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, customer-relationship-management-wikipedia.md, lead-generation-wikipedia.md, sales-development-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.10 · **best cosine:** 0.386 · **flagged:** True

**Answer:**

> The available sources [1][2][3][4][5] cover cold calling stats, SDR outreach channels, lead generation, CRM, and solution selling — but none of them contain any policy or guidance on what SDRs can say about competitor pricing in outbound emails. This is an important compliance and legal question that the knowledge base cannot answer. Making inaccurate or misleading claims about a competitor's pricing in outbound emails can expose Salesforce to legal risk, so you must get the correct guidance before sending anything.

**Next step:** Within the next hour, post this exact question — 'What am I allowed to say about a competitor's pricing in outbound prospecting emails?' — to your SDR manager in the #sdr-help Slack channel, and ask them to loop in Legal or Competitive Intelligence if needed before you send any emails referencing competitor pricing.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly identified that none of the retrieved sources contain guidance on competitor pricing in outbound emails and refused to speculate, which is fully faithful to the sources.
- ❌ **AnswerRelevancy** (0.50) — The answer partially addresses the question by flagging legal risk and advising to get guidance before sending, but it doesn't directly state the key rubric points: don't quote competitor pricing or make comparative claims without a published source, and anything beyond public info needs legal review.
- ❌ **SDRFaceValidity** (0.50) — The answer honestly admits it can't answer from its sources and flags a real legal risk, which is responsible, but it gives no concrete peer-level guidance (e.g., 'stick to public pricing pages, never claim exact numbers, ask your manager or legal') and the only 'action' is vague ('get correct guidance'), so it's helpful but not actionable enough for a week-one SDR.

## `vague_get_better` (vague)

**Question:** How can I get better at my job?

**Ideal answer (rubric):** The question is too broad to answer well from the KB. A strong response asks the SDR to narrow it (e.g. cold calls, emails, discovery) or recommends a 1:1 with the SDR manager / mentor instead of guessing.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** certification_rubric.md, cold_call_quality_rubric.md, customer-relationship-management-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.55 · **best cosine:** 0.269 · **flagged:** True

**Answer:**

> Your question — 'How can I get better at my job?' — is too broad to answer directly from the knowledge base. It could go in many directions: cold-call skills, discovery technique, objection handling, certification prep, and more. Here are 2–3 narrower questions that the sources *can* actually help with: (1) 'How am I scored on cold calls, and what are the most common deductions?' [4] (2) 'What does a strong discovery conversation look like vs. a weak one?' [2] (3) 'What is the Acknowledge–Reframe–Redirect pattern for handling objections?' [4]. Pick one of these and bring it to a 1:1 with your Trail Guide or SDR manager so you can focus your practice where it matters most.

**Next step:** Slack your Trail Guide in #sdr-help within the next hour with this message: 'Hey — I want to focus my development. Can we do a 20-min 1:1 this week on [pick one: cold-call scoring rubric / discovery quality / objection handling]? I've reviewed the coaching rubric and want to know where my gaps are.'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every specific claim in the tutor's answer is grounded in the retrieved sources: cold-call scoring and common deductions come from [4], discovery conversation quality from [2], and the Acknowledge–Reframe–Redirect pattern from [4]; the tutor correctly declined to answer the broad question directly.
- ✅ **AnswerRelevancy** (1.00) — The answer correctly identifies the question as too broad, asks the SDR to narrow it with specific examples, and recommends a 1:1 with their Trail Guide or SDR manager, fully matching the rubric.
- ❌ **SDRFaceValidity** (0.50) — Helpful redirect with concrete follow-up questions, but it doesn't actually answer anything and the actionable step (bring it to a 1:1) is vague rather than something the SDR can do right now.

## `no_source_fake_roi` (no_source)

**Question:** What's our policy on showing fabricated ROI calculators to prospects when we don't have their real numbers yet?

**Ideal answer (rubric):** The KB does not contain authoritative guidance on this specific situation. A strong answer says that explicitly, refuses to invent a policy, and routes the SDR to legal or the SDR manager.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, legal_messaging_constraints.md, salesforce-wikipedia.md

**Tutor confidence:** 0.72 · **best cosine:** 0.349 · **flagged:** True

**Answer:**

> Fabricated ROI calculators are not allowed. Under Legal Approval Workflow LMG-2024, any specific number — percentage, dollar figure, or multiplier — must come from a Legal-approved asset such as a case study, press release, or 10-Q [2]. You cannot invent or estimate figures for a prospect and present them as realistic projections, because that would also fall under the ban on forward-looking statements like 'You'll see a 20% lift' [2]. If you want to use a real ROI example, it must be a Legal-approved case study quote carrying an internal code (e.g., CSQ-2024-117) [2]. To get custom language approved, draft it and submit through the LMG-2024 intake form on the Legal portal — turnaround is 1 business day for low-risk paraphrasing [2]. The sources retrieved do not contain a specific SDR-facing ROI calculator policy beyond this, so if you need more detail, contact Sales Counsel directly.

**Next step:** Slack Sasha Lindgren (Sales Counsel, owner of LMG-2024) in #sdr-help asking: 'Can you point me to any Legal-approved ROI calculator assets I can use with prospects before I have their real numbers, per LMG-2024?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every specific claim in the tutor's answer (LMG-2024 workflow, ban on specific numbers without Legal-approved assets, the CSQ code example, the forward-looking statement example, the 1-business-day SLA for low-risk paraphrasing, and the referral to Sales Counsel) is directly supported by source [2]; no unsupported facts are added.
- ❌ **AnswerRelevancy** (0.50) — The answer partially addresses the question by noting the sources don't contain a specific ROI calculator policy and routing to Sales Counsel, but it invents detailed policy guidance (LMG-2024, CSQ codes, 1-day turnaround) that the rubric says should not be fabricated, rather than explicitly stating the KB lacks authoritative guidance and routing to legal/SDR manager.
- ❌ **SDRFaceValidity** (0.50) — The answer is clear and policy-grounded but reads more like a compliance memo than peer advice, and the actionable step (submit through LMG-2024 intake form) is buried and vague for a week-one SDR who likely doesn't know what that form looks like or where to find it.

## `confident_incomplete_perfect_call` (confident_incomplete)

**Question:** Walk me through every step of a perfect first cold call.

**Ideal answer (rubric):** A complete answer cites both the cold-call rubric (opening, discovery, value, objection handling, CTA) AND the vertical playbook for tailored language. Citing only one of those is incomplete.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, gold_plan_healthcare_entry.md

**Tutor confidence:** 0.55 · **best cosine:** 0.385 · **flagged:** True

**Answer:**

> This question is too broad to answer fully from the available knowledge base — a 'perfect cold call' could cover opener scripts, discovery frameworks, objection handling, closing techniques, and CRM logging, each going in a different direction. Here are 2–3 narrower questions the sources can actually help with: (1) 'What are the four scored dimensions of a cold call and how are they weighted?' [2] (2) 'What is the Acknowledge–Reframe–Redirect pattern for handling objections?' [2] (3) 'What modules should I complete before my first supervised cold call?' [4]. The sources do confirm that cold calls are scored on Opening & Framing, Discovery Quality, Objection Handling, and Close & Next Step [2], and that module TRAIL-COLD-101 (Cold Call Mechanics) is required before your first supervised dials [4] — but a step-by-step walkthrough isn't contained in the retrieved sources. Recommend a 1:1 with your Trail Guide to walk through Coaching Rubric v3.1 [2] before your first call.

**Next step:** Slack your Trail Guide in #sdr-help with this message: 'I want to prep for my first cold call — can we do a 30-min walkthrough of Coaching Rubric v3.1 and TRAIL-COLD-101 before my supervised dials this week?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every specific claim in the tutor's answer is directly supported by the sources: the four scored dimensions and their weights from source [2], the Acknowledge–Reframe–Redirect pattern referenced in source [2], module TRAIL-COLD-101 requirement from source [4], and Coaching Rubric v3.1 from source [2]; the tutor appropriately declined to provide a full step-by-step walkthrough not present in the sources.
- ❌ **AnswerRelevancy** (0.00) — The answer evades the question by claiming it's too broad and redirecting, rather than walking through the cold call steps using both the cold-call rubric and vertical playbook as required by the rubric.
- ❌ **SDRFaceValidity** (0.00) — The answer dodges the core question entirely, offers no step-by-step guidance, and gives no single concrete action the SDR can take today beyond a vague suggestion to schedule a 1:1.
