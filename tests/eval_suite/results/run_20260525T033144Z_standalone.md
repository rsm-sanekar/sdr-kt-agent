# DeepEval results — 20260525T033144Z (standalone)

**10 cases · 40 metric runs · 28 passed · 12 failed** (pass threshold = 0.70)

| # | Case | Category | Citation+NextStep | Faithfulness | AnswerRelevancy | SDRFaceValidity | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | `price_objection` | normal | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | **FAIL** |
| 2 | `cold_call_rubric` | normal | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 | **PASS** |
| 3 | `quota_ramp` | normal | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 | **PASS** |
| 4 | `territories` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | **FAIL** |
| 5 | `escalation_silent_enterprise` | normal | ❌ 0.50 | ✅ 1.00 | ❌ 0.50 | ❌ 0.00 | **FAIL** |
| 6 | `tooling_first_week` | normal | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | **FAIL** |
| 7 | `competitor_pricing_legal` | normal | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 | **PASS** |
| 8 | `vague_get_better` | vague | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | **FAIL** |
| 9 | `no_source_fake_roi` | no_source | ✅ 1.00 | ✅ 1.00 | ❌ 0.50 | ✅ 1.00 | **FAIL** |
| 10 | `confident_incomplete_perfect_call` | confident_incomplete | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 | **FAIL** |

## `price_objection` (normal)

**Question:** How do I handle a price objection on a cold call?

**Ideal answer (rubric):** Acknowledge the budget concern, reframe to value or ROI, and ask a discovery question to surface the real driver. Never lead with a discount on the first call.

**Expected KB doc:** `objection_handling_top10.md`

**Retrieved docs (top-5):** approved_qa, cold_call_quality_rubric.md, legal_messaging_constraints.md, objection_handling_top10.md

**Tutor confidence:** 0.90 · **best cosine:** 0.783 · **flagged:** False

**Answer:**

> When handling a price objection on a cold call, use the Acknowledge-Reframe-Redirect (ARR) pattern [1]. Specifically for a 'your product is too expensive' objection, Acknowledge the concern, Reframe to outcomes per dollar, and Redirect to an ROI conversation with a Subject Matter Expert (SE), not a price negotiation [4]. This approach is part of Salesforce's approved objection handling techniques and is required for scoring well on the Cold-call coaching rubric [3].

**Next step:** Review the objection_handling_top10.md document to familiarize yourself with the ARR pattern and specific responses to common objections, including price objections.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor's answer is fully supported by the retrieved sources, accurately describing the Acknowledge-Reframe-Redirect pattern for handling price objections on cold calls.
- ✅ **AnswerRelevancy** (1.00) — The answer fully addresses the rubric by outlining a specific approach (ARR pattern) that acknowledges the budget concern, reframes to value or ROI, and redirects to an ROI conversation, while also explicitly stating not to lead with a discount.
- ❌ **SDRFaceValidity** (0.50) — The answer provides a specific technique but sounds more like a training guideline than peer advice.

## `cold_call_rubric` (normal)

**Question:** What does our cold-call quality rubric grade on?

**Ideal answer (rubric):** The rubric scores opening, discovery, value framing, objection handling, and a concrete next step. Strong calls hit the bar on opening and end with one clear CTA.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** approved_qa, cold_call_quality_rubric.md, gold_plan_healthcare_entry.md, objection_handling_top10.md

**Tutor confidence:** 1.00 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> Our cold-call quality rubric grades on four dimensions: 1) Opening & framing [1], 2) Discovery quality [1], 3) Objection handling [1], and 4) Close & next step [1]. The rubric uses a 1-10 scale for each dimension, with weights applied to calculate an overall score. Common deductions include talking past the prospect, pitch dumping, unapproved claims, and skipping the recap [1].

**Next step:** Review the cold_call_quality_rubric.md document to understand the specifics of each dimension and common deductions.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor's answer is fully supported by the retrieved sources, with all claims and details accurately reflected from the cold_call_quality_rubric.md.
- ✅ **AnswerRelevancy** (1.00) — The answer directly addresses and fully covers the dimensions graded by the cold-call quality rubric.
- ✅ **SDRFaceValidity** (1.00) — The answer clearly explains what the cold-call quality rubric grades on and provides specific details, making it concrete and actionable.

## `quota_ramp` (normal)

**Question:** What is the quota ramp schedule for a new SDR?

**Ideal answer (rubric):** Ramp is graduated over the first six months: a lower target in months 1–2, a mid target in months 3–4, and full quota from roughly month 6 onward.

**Expected KB doc:** `quota_ramp_schedule.md`

**Retrieved docs (top-5):** approved_qa, onboarding_policy.md, quota_ramp_schedule.md, tooling_access_checklist.md

**Tutor confidence:** 0.90 · **best cosine:** 0.714 · **flagged:** False

**Answer:**

> The quota ramp schedule for a new SDR varies based on experience level. For entry-level hires (0-1 years prior sales experience), the standard ramp is: 25% of full quota in Month 1, 60% in Month 2, and 100% in Month 3 [1]. Mid-level hires (2-4 years prior sales) have a compressed schedule: 50% in Month 1, 90% in Month 2, and 100% in Month 3. Senior hires (5+ years prior sales) go to 100% quota on Day 30 [1].

**Next step:** Review the quota ramp schedule with your Trail Guide and discuss any questions or concerns you have about your specific ramp schedule.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor's answer is fully supported by the retrieved sources, with no added claims or speculation.
- ✅ **AnswerRelevancy** (1.00) — The answer provides a detailed quota ramp schedule for a new SDR, aligning with the rubric's requirement of a graduated ramp over the first six months.
- ✅ **SDRFaceValidity** (1.00) — The answer provides a clear, specific quota ramp schedule for new SDRs based on experience level and suggests an actionable step for the SDR to understand their own ramp schedule.

## `territories` (normal)

**Question:** How are SDR territories defined?

**Ideal answer (rubric):** Territories are split by region and vertical (e.g. AMER Healthcare, EMEA FinTech) with revenue-band segmentation inside each.

**Expected KB doc:** `territory_definitions.md`

**Retrieved docs (top-5):** approved_qa, compensation_overview.md, onboarding_policy.md, territory_definitions.md

**Tutor confidence:** 0.90 · **best cosine:** 0.526 · **flagged:** False

**Answer:**

> Salesforce SDR territories are defined as follows: AMER-West (United States: Alaska, Arizona, California, Colorado, Hawaii, Idaho, Montana, Nevada, New Mexico, Oregon, Utah, Washington, Wyoming; Canada: British Columbia, Alberta, Yukon; Mexico), AMER-East (United States: all states east of and including the Central time zone except those listed in AMER-West; Canada: Ontario, Quebec, Nova Scotia, New Brunswick, Newfoundland & Labrador, PEI, Manitoba, Saskatchewan; Brazil), EMEA (Europe, Middle East, Africa), and APAC (Australia, New Zealand, Japan, South Korea, Singapore, Malaysia, Thailand, Vietnam, Indonesia, Philippines, Hong Kong, Taiwan, India) [2].

**Next step:** Review the territory definitions document (territory_definitions.md) to familiarize yourself with the specific regions and countries assigned to each territory.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor's answer is entirely supported by the retrieved sources, specifically territory_definitions.md, with no added claims or speculation.
- ❌ **AnswerRelevancy** (0.50) — The answer provides specific territory definitions but lacks mention of verticals and revenue-band segmentation.
- ✅ **SDRFaceValidity** (1.00) — The answer provides a clear and concrete definition of SDR territories in plain language, making it easy for a new SDR to understand and take action.

## `escalation_silent_enterprise` (normal)

**Question:** A high-value enterprise prospect has gone silent after a discovery call. What's the escalation path?

**Ideal answer (rubric):** Loop in the AE and territory manager through the documented Slack channel within the SLA window; involve legal only if NDA or pricing has been shared.

**Expected KB doc:** `escalation_paths.md`

**Retrieved docs (top-5):** cold_call_quality_rubric.md, escalation_paths.md, objection_handling_top10.md, quota_ramp_schedule.md, tooling_access_checklist.md

**Tutor confidence:** 0.20 · **best cosine:** 0.532 · **flagged:** False

**Answer:**

> The provided sources don't explicitly outline an escalation path for a high-value enterprise prospect going silent after a discovery call. However, typical next steps in such scenarios often involve re-engagement attempts or escalating to a manager or another team member for assistance. Since the sources don't provide a clear answer, I recommend reaching out to your SDR manager for guidance on the best course of action.

**Next step:** Review your notes from the discovery call and draft a follow-up email to the prospect to re-engage them.

**Metric findings:**

- ❌ **CitationAndNextStep** (0.50) — Partial — missing citation.
- ✅ **Faithfulness** (1.00) — The tutor's answer accurately reflects that the provided sources do not explicitly outline an escalation path for a high-value enterprise prospect going silent after a discovery call and recommends reaching out to the SDR manager for guidance.
- ❌ **AnswerRelevancy** (0.50) — The answer partially addresses the question by suggesting reaching out to the SDR manager for guidance, but does not directly follow the specified escalation path outlined in the rubric.
- ❌ **SDRFaceValidity** (0.00) — The answer does not provide a concrete escalation path and instead advises reaching out to a manager, offering no direct action the SDR can take today.

## `tooling_first_week` (normal)

**Question:** Which tools should I have access to in my first week as an SDR?

**Ideal answer (rubric):** Core stack: Salesforce, Salesloft, Gong, and Clari. Request access through the tooling checklist, with IT and the SDR manager as approvers.

**Expected KB doc:** `tooling_access_checklist.md`

**Retrieved docs (top-5):** approved_qa, onboarding_policy.md, tooling_access_checklist.md

**Tutor confidence:** 0.90 · **best cosine:** 0.516 · **flagged:** False

**Answer:**

> As a new SDR, you should have access to the following tools in your first week: Salesforce CRM [1], Outreach [1], Slack [1], and Google Workspace [1]. These tools are provisioned on Day 1. Additionally, you will get access to Gong [1] by Day 3. For other tools like LinkedIn Sales Navigator [1] and ZoomInfo [1], the access timing may vary. If you have any questions or concerns about tool access, reach out to Linh Truong or your Trail Guide.

**Next step:** Review the tooling access checklist [1] and verify that you have access to the required tools. If not, reach out to Linh Truong or your Trail Guide for assistance.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor's answer is fully supported by the retrieved sources, specifically the tooling_access_checklist.md file.
- ❌ **AnswerRelevancy** (0.50) — The answer lists some relevant tools but does not mention the core stack or the process for requesting access.
- ✅ **SDRFaceValidity** (1.00) — The answer provides a clear list of specific tools and access timelines, and suggests a concrete action for the SDR to take if they have questions.

## `competitor_pricing_legal` (normal)

**Question:** What can I say about a competitor's pricing in outbound emails?

**Ideal answer (rubric):** Don't quote a competitor's pricing or make comparative claims you can't back to a published source. Anything past public info needs legal review before sending.

**Expected KB doc:** `legal_messaging_constraints.md`

**Retrieved docs (top-5):** approved_qa, cold_call_quality_rubric.md, legal_messaging_constraints.md, objection_handling_top10.md

**Tutor confidence:** 0.90 · **best cosine:** 0.367 · **flagged:** True

**Answer:**

> When discussing a competitor's pricing in outbound emails, SDRs should not make specific revenue or financial claims without legal review [2]. Additionally, comparative claims about named competitors are not allowed without LMG-2024 approval [2]. Instead of directly comparing prices, describe Salesforce's capability and let the prospect draw the comparison [2]. If a prospect asks about pricing, you can acknowledge the question, reframe it to focus on outcomes or value, and redirect the conversation to an ROI discussion with an SE [3]. The approved pattern is to use the Acknowledge-Reframe-Redirect (ARR) pattern [1].

**Next step:** Review the Legal messaging constraints (LMG-2024) document and familiarize yourself with the approval process for specific claims

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor's answer is fully supported by the retrieved sources, with no added claims or speculation.
- ✅ **AnswerRelevancy** (1.00) — The answer fully addresses the user's question about what to say regarding a competitor's pricing in outbound emails, aligning with the provided rubric.
- ✅ **SDRFaceValidity** (1.00) — The answer provides specific guidance on handling competitor pricing in outbound emails, offers a clear approach using the Acknowledge-Reframe-Redirect pattern, and implies actionable steps for the SDR to take today.

## `vague_get_better` (vague)

**Question:** How can I get better at my job?

**Ideal answer (rubric):** The question is too broad to answer well from the KB. A strong response asks the SDR to narrow it (e.g. cold calls, emails, discovery) or recommends a 1:1 with the SDR manager / mentor instead of guessing.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** cold_call_quality_rubric.md, gold_plan_healthcare_entry.md, tooling_access_checklist.md, trailhead_module_catalog.md

**Tutor confidence:** 0.90 · **best cosine:** 0.213 · **flagged:** True

**Answer:**

> To get better at your job as a Sales Development Representative (SDR), focus on improving your cold-call skills. The Cold-call coaching rubric [1] is a useful tool to evaluate and enhance your performance. It assesses calls across four dimensions: Opening & framing, Discovery quality, Objection handling, and Close & next step. Review this rubric to identify areas for improvement. Additionally, complete relevant Trailhead modules [4] such as Cold Call Mechanics (TRAIL-COLD-101) and Objection Handling Patterns (TRAIL-OBJ-101) to build your skills. Shadowing experienced reps and receiving feedback from your Trail Guide and manager are also crucial. Your onboarding plan [2] outlines specific activities and modules to help you progress.

**Next step:** Review the Cold-call coaching rubric (v3.1) document and discuss with your Trail Guide or manager to identify areas for improvement.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor's answer is fully supported by the retrieved sources, with no added claims or speculation.
- ❌ **AnswerRelevancy** (0.50) — The answer provides some relevant advice but doesn't directly address the broad nature of the question or suggest a 1:1 with the manager/mentor to provide more tailored guidance.
- ✅ **SDRFaceValidity** (1.00) — The answer provides concrete advice, uses plain language, and suggests a specific action the SDR can take today, such as reviewing the Cold-call coaching rubric.

## `no_source_fake_roi` (no_source)

**Question:** What's our policy on showing fabricated ROI calculators to prospects when we don't have their real numbers yet?

**Ideal answer (rubric):** The KB does not contain authoritative guidance on this specific situation. A strong answer says that explicitly, refuses to invent a policy, and routes the SDR to legal or the SDR manager.

**Expected KB doc:** `(none — should be flagged)`

**Retrieved docs (top-5):** cold_call_quality_rubric.md, compensation_overview.md, legal_messaging_constraints.md, objection_handling_top10.md, vertical_playbook_fintech.md

**Tutor confidence:** 0.90 · **best cosine:** 0.313 · **flagged:** True

**Answer:**

> Our policy on showing fabricated ROI calculators to prospects is clear: no specific revenue or financial claims are allowed without legal review [1]. This means you can't create or present custom ROI calculators with fictional numbers to prospects. Instead, use Legal-approved assets like case studies or press releases that have an internal code (e.g., `CSQ-2024-117`) [1]. If you're unsure about what you can share, submit a draft of your proposed language through the LMG-2024 intake form on the Legal portal [1].

**Next step:** Review the Legal messaging constraints (LMG-2024) document and familiarize yourself with the approved language patterns.

**Metric findings:**

- ✅ **CitationAndNextStep** (1.00) — Cites [n] inline and ends with a concrete next step.
- ✅ **Faithfulness** (1.00) — The tutor's answer is fully supported by the retrieved sources, specifically [1], and does not include any unsupported claims or speculation.
- ❌ **AnswerRelevancy** (0.50) — The answer provides policy guidance but does not explicitly state that there is no authoritative guidance on using fabricated ROI calculators without real numbers and does not directly route the SDR to legal or the manager.
- ✅ **SDRFaceValidity** (1.00) — The answer provides clear policy guidance, uses plain language, and suggests a concrete action for the SDR to take today.

## `confident_incomplete_perfect_call` (confident_incomplete)

**Question:** Walk me through every step of a perfect first cold call.

**Ideal answer (rubric):** A complete answer cites both the cold-call rubric (opening, discovery, value, objection handling, CTA) AND the vertical playbook for tailored language. Citing only one of those is incomplete.

**Expected KB doc:** `cold_call_quality_rubric.md`

**Retrieved docs (top-5):** approved_qa, cold_call_quality_rubric.md, gold_plan_healthcare_entry.md, objection_handling_top10.md

**Tutor confidence:** 0.00 · **best cosine:** 0.371 · **flagged:** True

**Answer:**

> 

**Next step:** 

**Metric findings:**

- ❌ **CitationAndNextStep** (0.00) — Tutor failed to produce an answer: ValidationError: 3 validation errors for TutorAnswer
answer
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
next_step
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
confidence
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing.
- ❌ **Faithfulness** (0.00) — Tutor failed to produce an answer: ValidationError: 3 validation errors for TutorAnswer
answer
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
next_step
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
confidence
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing.
- ❌ **AnswerRelevancy** (0.00) — Tutor failed to produce an answer: ValidationError: 3 validation errors for TutorAnswer
answer
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
next_step
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
confidence
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing.
- ❌ **SDRFaceValidity** (0.00) — Tutor failed to produce an answer: ValidationError: 3 validation errors for TutorAnswer
answer
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
next_step
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
confidence
  Field required [type=missing, input_value={'properties': {'answer':...nce'], 'type': 'object'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing.
