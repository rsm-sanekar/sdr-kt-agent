"""DeepEval test cases for the SDR AI Tutor (skills/answer-sdr-question).

Each case has:
- id:             short identifier used in the results table
- category:       normal | vague | no_source | confident_incomplete | wrong_doc
- question:       what the user types
- ideal_answer:   one or two sentences describing what a strong answer looks like;
                  used by the relevancy and faithfulness judges
- expected_doc:   the KB doc whose passage SHOULD appear in retrieval (None for
                  cases that have no good source — those should be flagged
                  rather than answered confidently)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TutorCase:
    id: str
    category: str
    question: str
    ideal_answer: str
    expected_doc: str | None


CASES: list[TutorCase] = [
    TutorCase(
        id="price_objection",
        category="normal",
        question="How do I handle a price objection on a cold call?",
        ideal_answer=(
            "Acknowledge the budget concern, reframe to value or ROI, and ask a discovery "
            "question to surface the real driver. Never lead with a discount on the first call."
        ),
        expected_doc="objection_handling_top10.md",
    ),
    TutorCase(
        id="cold_call_rubric",
        category="normal",
        question="What does our cold-call quality rubric grade on?",
        ideal_answer=(
            "The rubric scores opening, discovery, value framing, objection handling, and a "
            "concrete next step. Strong calls hit the bar on opening and end with one clear CTA."
        ),
        expected_doc="cold_call_quality_rubric.md",
    ),
    TutorCase(
        id="quota_ramp",
        category="normal",
        question="What is the quota ramp schedule for a new SDR?",
        ideal_answer=(
            "Ramp is graduated over the first six months: a lower target in months 1–2, a "
            "mid target in months 3–4, and full quota from roughly month 6 onward."
        ),
        expected_doc="quota_ramp_schedule.md",
    ),
    TutorCase(
        id="territories",
        category="normal",
        question="How are SDR territories defined?",
        ideal_answer=(
            "Territories are split by region and vertical (e.g. AMER Healthcare, EMEA FinTech) "
            "with revenue-band segmentation inside each."
        ),
        expected_doc="territory_definitions.md",
    ),
    TutorCase(
        id="escalation_silent_enterprise",
        category="normal",
        question=(
            "A high-value enterprise prospect has gone silent after a discovery call. "
            "What's the escalation path?"
        ),
        ideal_answer=(
            "Loop in the AE and territory manager through the documented Slack channel within "
            "the SLA window; involve legal only if NDA or pricing has been shared."
        ),
        expected_doc="escalation_paths.md",
    ),
    TutorCase(
        id="tooling_first_week",
        category="normal",
        question="Which tools should I have access to in my first week as an SDR?",
        ideal_answer=(
            "Core stack: Salesforce, Salesloft, Gong, and Clari. Request access through the "
            "tooling checklist, with IT and the SDR manager as approvers."
        ),
        expected_doc="tooling_access_checklist.md",
    ),
    TutorCase(
        id="competitor_pricing_legal",
        category="normal",
        question="What can I say about a competitor's pricing in outbound emails?",
        ideal_answer=(
            "Don't quote a competitor's pricing or make comparative claims you can't back to a "
            "published source. Anything past public info needs legal review before sending."
        ),
        expected_doc="legal_messaging_constraints.md",
    ),
    TutorCase(
        id="vague_get_better",
        category="vague",
        question="How can I get better at my job?",
        ideal_answer=(
            "The question is too broad to answer well from the KB. A strong response asks the "
            "SDR to narrow it (e.g. cold calls, emails, discovery) or recommends a 1:1 with the "
            "SDR manager / mentor instead of guessing."
        ),
        expected_doc=None,
    ),
    TutorCase(
        id="no_source_fake_roi",
        category="no_source",
        question=(
            "What's our policy on showing fabricated ROI calculators to prospects when "
            "we don't have their real numbers yet?"
        ),
        ideal_answer=(
            "The KB does not contain authoritative guidance on this specific situation. A "
            "strong answer says that explicitly, refuses to invent a policy, and routes the "
            "SDR to legal or the SDR manager."
        ),
        expected_doc=None,
    ),
    TutorCase(
        id="confident_incomplete_perfect_call",
        category="confident_incomplete",
        question="Walk me through every step of a perfect first cold call.",
        ideal_answer=(
            "A complete answer cites both the cold-call rubric (opening, discovery, value, "
            "objection handling, CTA) AND the vertical playbook for tailored language. Citing "
            "only one of those is incomplete."
        ),
        expected_doc="cold_call_quality_rubric.md",
    ),
]


def get_case(case_id: str) -> TutorCase:
    for c in CASES:
        if c.id == case_id:
            return c
    raise KeyError(f"No DeepEval case with id={case_id!r}")
