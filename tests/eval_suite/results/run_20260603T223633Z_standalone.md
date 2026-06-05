# DeepEval results — 20260603T223633Z (standalone)

**10 cases · 40 metric runs · 21 passed · 19 failed** (pass threshold = 0.70)

| # | Case | Category | Citation+NextStep | Faithfulness | AnswerRelevancy | SDRFaceValidity | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | `price_objection` | normal | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | ❌ 0.50 | **FAIL** |
| 2 | `cold_call_rubric` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 3 | `quota_ramp` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | **FAIL** |
| 4 | `territories` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 5 | `escalation_silent_enterprise` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 6 | `tooling_first_week` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 7 | `competitor_pricing_legal` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ❌ 0.50 | **FAIL** |
| 8 | `vague_get_better` | vague | ✅ 1.00 | ❌ 0.50 | ✅ 0.75 | ❌ 0.50 | **FAIL** |
| 9 | `no_source_fake_roi` | no_source | ✅ 1.00 | ✅ 1.00 | ❌ 0.00 | ❌ 0.50 | **FAIL** |
| 10 | `confident_incomplete_perfect_call` | confident_incomplete | ✅ 1.00 | ✅ 0.90 | ❌ 0.50 | ❌ 0.50 | **FAIL** |

## `price_objection` (normal)

**Question:** How do I handle a price objection on a cold call?

**Ideal answer (rubric):** Acknowledge the budget concern, reframe to value or ROI, and ask a discovery question to surface the real driver. Never lead with a discount on the first call.

**Expected KB doc:** `objection_handling_top10.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.62 · **best cosine:** 0.468 · **flagged:** False

**Answer:**

> Price objections on a cold call aren't listed by name in the sources, but the closest match is 'We don't have budget' [1]. Use the required Acknowledge–Reframe–Redirect (ARR) pattern [1][5]: (1) Acknowledge: 'That makes total sense — budget is always a factor.' (2) Reframe: 'Budget cycles vary; we typically start the conversation 4–6 months before procurement so you're ready when the time comes.' [1] (3) Redirect: Propose a future-dated discovery call to explore fit without pressure [1]. Skipping the Acknowledge step costs you 1–2 points on Dimension 3 of the Coaching Rubric [5], so always lead with it. Do NOT discuss specific pricing or make unapproved claims — that can result in a –3 deduction [5].

**Next step:** Pull up objection_handling_top10.md today, practice the ARR script for 'We don't have budget' out loud three times, then ask your Trail Guide to do a 10-minute role-play so you get live feedback before your next call block.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — Most claims are supported, but the tutor adds 'Do NOT discuss specific pricing or make unapproved claims — that can result in a –3 deduction' which partially misrepresents source [5] (the –3 is for 'unapproved claims' generally, not specifically pricing), and the specific example acknowledgement phrase 'That makes total sense — budget is always a factor' is fabricated and not present in the sources.
- ✅ **AnswerRelevancy** (1.00) — The answer acknowledges the concern, reframes to value/timing, redirects with a discovery question, and explicitly warns against leading with discounts, fully covering the rubric.
- ❌ **SDRFaceValidity** (0.50) — The ARR framework and example phrases are helpful, but the answer leans on internal rubric citations that mean nothing to a new SDR and doesn't end with a single concrete action they can take today on a live call.

## `cold_call_rubric` (normal)

**Question:** What does our cold-call quality rubric grade on?

**Ideal answer (rubric):** The rubric scores opening, discovery, value framing, objection handling, and a concrete next step. Strong calls hit the bar on opening and end with one clear CTA.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, objection_handling_top10.md

**Tutor confidence:** 0.97 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> The cold-call quality rubric (v3.1) grades every Gong-sampled call on four dimensions, each scored 1–10 and combined into a weighted overall score [1]: (1) Opening & framing (weight 0.20) — did you state who you are, why you're calling, and earn 30 more seconds within the first 15? [1] (2) Discovery quality (weight 0.35) — how many qualified discovery questions did you ask, and did you follow up on the prospect's answers? [1] (3) Objection handling (weight 0.25) — did you use the Acknowledge–Reframe–Redirect (ARR) pattern? [1][3] (4) Close & next step (weight 0.20) — did you propose and get a specific, calendared next step? [1] Watch out for common deductions like pitch dumping (–2) and unapproved claims (–3) [1].

**Next step:** Pull up cold_call_quality_rubric.md today and score yourself on your last recorded call across all four dimensions — then bring your self-score to your next Trail Guide session for comparison.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer—the four dimensions, their weights, the 1–10 scale, the ARR pattern reference, and the specific deductions (pitch dumping –2, unapproved claims –3)—is directly supported by source [1] and [3].
- ❌ **AnswerRelevancy** (0.50) — The answer covers opening, discovery, objection handling, and next step, but omits 'value framing' as a graded dimension listed in the rubric, and the rubric's emphasis on opening and a single clear CTA is only partially reflected.
- ❌ **SDRFaceValidity** (0.50) — The answer is detailed and structured but reads like a policy document rather than peer advice, and it lacks a concrete action the SDR can take today.

## `quota_ramp` (normal)

**Question:** What is the quota ramp schedule for a new SDR?

**Ideal answer (rubric):** Ramp is graduated over the first six months: a lower target in months 1–2, a mid target in months 3–4, and full quota from roughly month 6 onward.

**Expected KB doc:** `quota_ramp_schedule.md`

**Retrieved docs (top-5):** onboarding_policy.md, quota_ramp_schedule.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.95 · **best cosine:** 0.714 · **flagged:** False

**Answer:**

> Your quota ramp depends on your prior sales experience [1]:
> 
> **Entry-level (0–1 years):** Month 1 = 25% of full quota, Month 2 = 60%, Month 3+ = 100%. You get a guaranteed minimum of 70% of target variable pay in months 1 and 2 [1].
> 
> **Mid-level (2–4 years):** Month 1 = 50%, Month 2 = 90%, Month 3+ = 100%. Guaranteed minimum applies in Month 1 only [1].
> 
> **Senior (5+ years):** You hit 100% quota on Day 30 with no guaranteed minimum after that [1].
> 
> During Month 1, regardless of tier, you're also held to activity targets: 60 outbound dials/day, 25 personalized emails/day, 5 LinkedIn touches/day, and 3 booked discovery calls/week [2]. If something disrupts your ramp (territory split, training hold), your ramp calendar is adjusted — not waived — by Ravi Anand's Sales Operations team [1].

**Next step:** Confirm your experience tier with your SDR manager today so you know exactly which ramp curve applies to you, then log into Trailhead and check which required modules you need to complete before your first live dial [3].

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the retrieved sources: the ramp percentages, guaranteed minimums, activity targets, and quota relief adjustment policy all match sources [1] and [2] exactly.
- ❌ **AnswerRelevancy** (0.50) — The answer provides a ramp schedule but doesn't match the rubric's description of a six-month graduated ramp (lower in months 1-2, mid in months 3-4, full from month 6); instead it describes a 3-month ramp varying by experience level, which partially addresses the question but diverges from the expected structure.
- ✅ **SDRFaceValidity** (1.00) — Concrete tier-by-tier breakdown with specific percentages, activity targets, and a named contact for exceptions — exactly the peer-level detail a week-one SDR needs, ending with implicit next steps embedded in the structure.

## `territories` (normal)

**Question:** How are SDR territories defined?

**Ideal answer (rubric):** Territories are split by region and vertical (e.g. AMER Healthcare, EMEA FinTech) with revenue-band segmentation inside each.

**Expected KB doc:** `territory_definitions.md`

**Retrieved docs (top-5):** certification_rubric.md, compensation_overview.md, onboarding_policy.md, sales-development-wikipedia.md, territory_definitions.md

**Tutor confidence:** 0.95 · **best cosine:** 0.479 · **flagged:** False

**Answer:**

> Salesforce SDR territories are split into four global regions, effective January 2024 [1]: (1) AMER-West covers the western US states, parts of Canada (BC, Alberta, Yukon), and Mexico [1]; (2) AMER-East covers eastern/central US states, eastern Canadian provinces, and — importantly — Brazil [1]; (3) EMEA covers all of Europe, the Middle East, and Africa, including the UAE, Israel, Turkey, and South Africa [1]; (4) APAC covers Australia, NZ, Japan, South Korea, Singapore, and other Southeast Asian countries, plus India (with its own Bengaluru pod) [1]. A few common mistakes to avoid: Brazil goes to AMER-East (not LATAM-unassigned), UAE goes to EMEA (not APAC), India goes to APAC (not EMEA), and Mexico goes to AMER-West [1]. Territory definitions tie directly into lead routing, comp plans, and Trail Guide pairings [1]. For questions, contact Ravi Anand, Director of Sales Operations [1].

**Next step:** Open territory_definitions.md today and quiz yourself on the five edge-case countries (Brazil, UAE, India, Mexico, South Africa) until you can recall their correct territories without looking.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the territory_definitions.md source, including the four regions, their constituent countries/states, edge cases, effective date, and contact person.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses geographic region splits in detail but does not mention vertical segmentation (e.g., Healthcare, FinTech) or revenue-band segmentation within territories, which are key parts of the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and concrete but reads like it's describing one company's (Salesforce's) internal setup as if it's universal SDR territory definition, which is misleading for a new SDR who needs to understand how territories are generally defined; it lacks a truly actionable next step beyond 'contact Ravi Anand.'

## `escalation_silent_enterprise` (normal)

**Question:** A high-value enterprise prospect has gone silent after a discovery call. What's the escalation path?

**Ideal answer (rubric):** Loop in the AE and territory manager through the documented Slack channel within the SLA window; involve legal only if NDA or pricing has been shared.

**Expected KB doc:** `escalation_paths.md`

**Retrieved docs (top-5):** certification_questions.md, certification_rubric.md, cold-calling-wikipedia.md, cold_call_quality_rubric.md

**Tutor confidence:** 0.10 · **best cosine:** 0.532 · **flagged:** False

**Answer:**

> The provided sources do not contain a specific escalation path for re-engaging a silent enterprise prospect after a discovery call. The sources cover cold-call scoring rubrics [1], discovery questioning techniques [2], objection handling frameworks [3], and general cold-calling research [4][5] — but none outline a formal 'gone silent' escalation process for high-value accounts. That said, source [3] suggests using the Defuse-Discover-Deliver method when a prospect pushes back, which could inform a follow-up attempt — but this is not a documented escalation path. For the official process, you should ask your SDR manager directly, as they will know whether to loop in your Account Executive, a Senior SDR, or a Sales Leader for strategic re-engagement on high-value enterprise accounts.

**Next step:** Send a Slack message or calendar invite to your SDR manager today and ask: 'What is our team's escalation process when a high-value enterprise prospect goes dark after a discovery call — do I loop in the AE, and is there a standard re-engagement sequence I should follow?'

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly identified that the sources don't contain a specific escalation path for silent enterprise prospects, accurately described what the sources do cover, and appropriately flagged the Defuse-Discover-Deliver method as only tangentially relevant rather than a documented escalation path, without fabricating any unsupported specifics.
- ❌ **AnswerRelevancy** (0.00) — The answer does not provide the specific escalation path described in the rubric (looping in AE and territory manager via documented Slack channel within SLA window, involving legal only if NDA/pricing shared), instead deflecting to ask a manager.
- ❌ **SDRFaceValidity** (0.50) — Honest about its limitations and points to the right people (AE, manager), but gives no concrete next step the SDR can take today beyond 'ask your manager.'

## `tooling_first_week` (normal)

**Question:** Which tools should I have access to in my first week as an SDR?

**Ideal answer (rubric):** Core stack: Salesforce, Salesloft, Gong, and Clari. Request access through the tooling checklist, with IT and the SDR manager as approvers.

**Expected KB doc:** `tooling_access_checklist.md`

**Retrieved docs (top-5):** onboarding_policy.md, sales-development-wikipedia.md, tooling_access_checklist.md

**Tutor confidence:** 0.95 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> Here's what you should have access to in your first week:
> 
> **Day 1 (before your first login):** [1]
> - **Salesforce CRM** — production org with the SDR Standard profile
> - **Outreach** — full seat with the default cadence library (note: your Trail Guide must review personal sequences before you send them)
> - **Slack** — added to #sdr-global, your regional pod channel, and #trail-guides-cohort-2024
> - **Google Workspace** — calendar, Meet, and a mailbox with the SDR signature template
> 
> **Day 3:** [1]
> - **Gong** — recording and review seat (auto-recording is on by default for all outbound dials)
> 
> **Week 2:** [1]
> - **LinkedIn Sales Navigator** — Advanced seat with TeamLink (subject to regional license availability)
> 
> **Requires manager approval (no set week):** [1]
> - **ZoomInfo** — your SDR manager must give written approval; provisioning takes up to 2 business days after that.
> 
> If anything is missing on Day 1, it gets escalated to Linh Truong by 11:00 AM your local time. [1]

**Next step:** Log into all four Day-1 tools (Salesforce CRM, Outreach, Slack, Google Workspace) before 11:00 AM today and confirm they're working — if any are missing, flag it immediately so Linh Truong's team can resolve it before the SLA deadline. [1]

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by the tooling_access_checklist.md source, including Day-1 tools, Day-3 Gong access, Week-2 LinkedIn Sales Navigator, ZoomInfo approval requirements, and the Linh Truong escalation detail.
- ❌ **AnswerRelevancy** (0.50) — The answer addresses the question about tools but lists Outreach instead of Salesloft, and omits Clari entirely, while also not mentioning the tooling checklist with IT and SDR manager as approvers per the rubric.
- ❌ **SDRFaceValidity** (0.50) — The answer is specific and well-structured but reads like it was pulled from an internal onboarding doc with suspiciously precise details (e.g., 'Linh Truong by 11:00 AM') that feel fabricated rather than peer advice, and it lacks a concrete action the SDR can take today.

## `competitor_pricing_legal` (normal)

**Question:** What can I say about a competitor's pricing in outbound emails?

**Ideal answer (rubric):** Don't quote a competitor's pricing or make comparative claims you can't back to a published source. Anything past public info needs legal review before sending.

**Expected KB doc:** `legal_messaging_constraints.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, customer-relationship-management-wikipedia.md, lead-generation-wikipedia.md, sales-development-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.05 · **best cosine:** 0.386 · **flagged:** True

**Answer:**

> The provided sources do not contain any guidance on what you can or cannot say about a competitor's pricing in outbound emails. This is an important topic that touches on legal risk, Salesforce's competitive messaging policies, and ethical selling standards — none of which are covered in sources [1] through [5]. Making inaccurate or disparaging claims about a competitor's pricing in writing can expose Salesforce to legal liability, so you should get the official answer before sending anything.

**Next step:** Ask your SDR manager today for Salesforce's official competitive messaging guidelines and any approved 'battle cards' — these will tell you exactly what you're allowed to say about competitors' pricing in outbound emails.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor correctly acknowledged that the sources contain no guidance on competitor pricing in outbound emails and refused to speculate, which is fully faithful to the retrieved sources.
- ❌ **AnswerRelevancy** (0.50) — The answer partially addresses the question by warning about legal liability and recommending getting official guidance, but doesn't directly state the rubric's key points about not quoting competitor pricing or limiting claims to publicly sourced information.
- ❌ **SDRFaceValidity** (0.50) — The answer honestly admits it can't answer from sources and flags real legal risk, which is helpful, but it doesn't give the SDR a concrete action to take today (e.g., 'Slack your manager or legal/compliance contact right now and ask before sending anything').

## `vague_get_better` (vague)

**Question:** How can I get better at my job?

**Ideal answer (rubric):** The question is too broad to answer well from the KB. A strong response asks the SDR to narrow it (e.g. cold calls, emails, discovery) or recommends a 1:1 with the SDR manager / mentor instead of guessing.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** certification_rubric.md, cold_call_quality_rubric.md, customer-relationship-management-wikipedia.md, solution-selling-wikipedia.md

**Tutor confidence:** 0.45 · **best cosine:** 0.269 · **flagged:** True

**Answer:**

> The available sources don't directly answer 'how to get better at your job' in a broad sense, but they do point to a few specific, actionable skill areas. Source [4] shows that cold calls are scored on four dimensions: Opening & Framing, Discovery Quality, Objection Handling, and Close & Next Step — so improving in these areas directly raises your performance score. Source [2] highlights a common SDR gap: pitching before understanding the prospect. The fix is practicing discovery questions and active-listening drills. Source [4] also warns against 'pitch dumping' and 'talking past the prospect,' both of which cost you points on call reviews. For broader career development advice beyond these specific skills, I'd recommend speaking with your SDR manager or Trail Guide — they can review your Gong call recordings and give you personalized coaching based on your actual scores.

**Next step:** Pull up one of your recent recorded calls in Gong today and score yourself honestly on the four dimensions from the cold-call rubric [4] — Opening, Discovery, Objection Handling, and Close — then bring your self-assessment to your next 1:1 with your manager or Trail Guide.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ❌ **Faithfulness** (0.50) — Most claims about the four scored dimensions, pitch dumping, talking past the prospect, and the discovery gap are supported by sources [4] and [2], but the mention of 'Gong call recordings' and 'Trail Guide' as specific resources for personalized coaching are not found in the retrieved sources (though Gong is mentioned in [4] as a tool for sampling calls, the specific coaching recommendation to speak with a 'Trail Guide' for Gong review is not directly supported).
- ✅ **AnswerRelevancy** (0.75) — The answer partially meets the rubric by recommending a 1:1 with the SDR manager/Trail Guide, but it also attempts to answer the broad question with specific tips rather than primarily asking the SDR to narrow down the focus area first.
- ❌ **SDRFaceValidity** (0.50) — Helpful and specific about skill areas (discovery, objection handling, avoiding pitch dumping) but ends with a soft redirect to a manager rather than one concrete action the SDR can take today on their own.

## `no_source_fake_roi` (no_source)

**Question:** What's our policy on showing fabricated ROI calculators to prospects when we don't have their real numbers yet?

**Ideal answer (rubric):** The KB does not contain authoritative guidance on this specific situation. A strong answer says that explicitly, refuses to invent a policy, and routes the SDR to legal or the SDR manager.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, legal_messaging_constraints.md, salesforce-wikipedia.md

**Tutor confidence:** 0.92 · **best cosine:** 0.349 · **flagged:** True

**Answer:**

> Fabricated ROI calculators are not allowed. Under Legal Approval Workflow LMG-2024, any specific number — a percentage, dollar amount, or multiplier — must come from a Legal-approved asset like a case study, press release, or 10-Q [2]. That means you cannot invent or estimate ROI figures for a prospect just because you don't have their real numbers yet. Doing so could trigger regulatory inquiries or litigation [2]. If you want to reference ROI, use only approved case-study quotes that carry an internal code (e.g., CSQ-2024-117) [2]. If you'd like to create new ROI language, draft it and submit it through the LMG-2024 intake form on the Legal portal — low-risk paraphrasing gets a 1-business-day turnaround [2]. The owner of this policy is Sasha Lindgren, Sales Counsel [2].

**Next step:** Today, log into the Legal portal, bookmark the LMG-2024 intake form, and review the list of already-approved case-study quotes (look for CSQ codes) so you have compliant ROI references ready to use on your next call.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — Every claim in the tutor's answer is directly supported by source [2] (LMG-2024): the prohibition on specific numbers without legal-approved assets, the risk of regulatory inquiries or litigation, the case-study quote codes, the LMG-2024 intake form, the 1-business-day SLA for low-risk paraphrasing, and Sasha Lindgren as owner.
- ❌ **AnswerRelevancy** (0.00) — The rubric requires the answer to explicitly state that the KB lacks authoritative guidance on this specific situation and route the SDR to legal or their manager, but instead the answer invents a detailed policy with fabricated references (LMG-2024, CSQ-2024-117, Sasha Lindgren) rather than acknowledging the knowledge gap.
- ❌ **SDRFaceValidity** (0.50) — The answer is clear and policy-grounded but reads more like a compliance memo than peer advice, and the 'action today' (submit through LMG-2024 intake form) is buried and conditional rather than a direct next step the SDR would actually take right now.

## `confident_incomplete_perfect_call` (confident_incomplete)

**Question:** Walk me through every step of a perfect first cold call.

**Ideal answer (rubric):** A complete answer cites both the cold-call rubric (opening, discovery, value, objection handling, CTA) AND the vertical playbook for tailored language. Citing only one of those is incomplete.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** cold-calling-wikipedia.md, cold_call_quality_rubric.md, gold_plan_healthcare_entry.md

**Tutor confidence:** 0.55 · **best cosine:** 0.385 · **flagged:** True

**Answer:**

> The sources don't contain a full step-by-step cold call script, but they do reveal the key building blocks Salesforce scores you on. Based on the internal coaching rubric [2], a strong cold call has four parts: (1) Opening & framing — within the first 15 seconds, state who you are, why you're calling, and earn 30 more seconds [2]; (2) Discovery — ask qualified questions and genuinely follow up on what the prospect says — this is the highest-weighted dimension [2]; (3) Objection handling — use the Acknowledge–Reframe–Redirect pattern when pushback comes [2]; (4) Close with a specific, calendared next step [2]. Avoid these common traps: talking over the prospect, dumping product features before any discovery, and making unapproved claims [2]. Modern best practice also suggests researching the prospect before calling so you understand their situation [3]. Your Trail Guide scores every Gong-recorded call against exactly these four dimensions [2].

**Next step:** Pull up the Cold-call coaching rubric (v3.1) and complete module TRAIL-COLD-101 today, then ask your Trail Guide to schedule your first 5 supervised cold calls this week so you get live feedback against the rubric.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (0.90) — All four dimensions, weights, common deductions, and the Acknowledge–Reframe–Redirect pattern are directly supported by source [2]; the pre-call research point is loosely supported by source [3]'s 'warm calling' methodology; the only minor unsupported claim is attributing the rubric specifically to 'Salesforce' and the Gong recording detail, though [2] does mention Gong sampling, making the answer largely faithful.
- ❌ **AnswerRelevancy** (0.50) — The answer covers the cold-call rubric (opening, discovery, objection handling, CTA) but does not mention the vertical playbook for tailored language, which the rubric requires for a complete answer.
- ❌ **SDRFaceValidity** (0.50) — The four-part framework is helpful and reasonably concrete, but it reads more like a rubric summary than peer advice walking through an actual call, and there's no single actionable step the SDR can take today.
