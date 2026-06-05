"""Custom DeepEval metrics for the SDR Tutor.

Three checks are LLM-judged through ``utils.connect.ask_json`` (same client the
tutor itself uses — TritonAI). One check is fully deterministic.

Each metric subclasses :class:`deepeval.metrics.BaseMetric` so the suite can be
driven via ``deepeval.evaluate`` or ``pytest`` + ``assert_test``.

Test cases carry retrieval context as a list of ``"<doc_name>::<passage>"``
strings (DeepEval's ``retrieval_context`` is a flat list of strings, so we
encode the doc name into each entry).
"""

from __future__ import annotations

import re

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from pydantic import BaseModel, Field

from utils.connect import ask_json

PASS_THRESHOLD = 0.7  # any score >= this is "pass"

JUDGE_MODEL = "claude-sonnet-4-6"


class _JudgeVerdict(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=3)


def _judge(system: str, user: str) -> _JudgeVerdict:
    """Run a 0.0-1.0 LLM judge with a short reason. Synchronous on purpose —
    DeepEval's async path adds nothing here and complicates collection."""
    return ask_json(
        user,
        schema=_JudgeVerdict,
        system=system,
        model=JUDGE_MODEL,
        temperature=0.0,
    )


# ---------------------------------------------------------------------------
# Metric 1 — deterministic: cites a numbered source AND ends with a next step
# ---------------------------------------------------------------------------

class CitationAndNextStepMetric(BaseMetric):
    """Plain-sentence quality rule:
      - answer text contains at least one ``[n]`` citation, AND
      - the envelope includes a non-trivial ``next_step``.

    The LLMTestCase carries the answer in ``actual_output`` and the next step
    in ``additional_metadata['next_step']``.
    """

    threshold: float = PASS_THRESHOLD

    def __init__(self, threshold: float = PASS_THRESHOLD):
        self.threshold = threshold
        self.score: float = 0.0
        self.success: bool = False
        self.reason: str = ""

    def measure(self, test_case: LLMTestCase) -> float:
        answer = test_case.actual_output or ""
        next_step = ""
        meta = getattr(test_case, "additional_metadata", None) or {}
        if isinstance(meta, dict):
            next_step = (meta.get("next_step") or "").strip()

        has_citation = bool(re.search(r"\[\d+\]", answer))
        has_next_step = len(next_step) >= 6 and next_step.lower() not in {"none", "n/a"}

        if has_citation and has_next_step:
            self.score = 1.0
            self.reason = "Cites [n] inline and ends with a concrete next step."
        elif has_citation or has_next_step:
            self.score = 0.5
            missing = "citation" if not has_citation else "next step"
            self.reason = f"Partial — missing {missing}."
        else:
            self.score = 0.0
            self.reason = "No [n] citation and no concrete next step."

        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self) -> str:  # type: ignore[override]
        return "CitationAndNextStep"


# ---------------------------------------------------------------------------
# Metric 2 — LLM-judged: faithfulness to retrieved sources (no hallucination)
# ---------------------------------------------------------------------------

class FaithfulnessMetric(BaseMetric):
    """Did the tutor stick to what the retrieved passages actually say?

    For "no source" or "vague" cases the right answer is to refuse confidently
    — so this metric also rewards the model for explicitly saying it can't
    answer when no passage covers the question.
    """

    threshold: float = PASS_THRESHOLD

    SYSTEM = (
        "You are an evaluator grading an SDR tutor's answer for FAITHFULNESS to its "
        "retrieved sources. Score 1.0 if every claim is supported by the sources, "
        "or if the sources don't cover the question AND the tutor refused to "
        "speculate. Score 0.5 if the answer is partly grounded but adds one or two "
        "unsupported claims. Score 0.0 if the answer fabricates policy, numbers, or "
        "specifics not present in the sources. Return JSON: {score: float in [0,1], "
        "reason: one short sentence}."
    )

    def __init__(self, threshold: float = PASS_THRESHOLD):
        self.threshold = threshold
        self.score: float = 0.0
        self.success: bool = False
        self.reason: str = ""

    def measure(self, test_case: LLMTestCase) -> float:
        sources_block = _format_retrieval_context(test_case.retrieval_context or [])
        user = (
            f"Question: {test_case.input}\n\n"
            f"Tutor answer:\n{test_case.actual_output}\n\n"
            f"Retrieved sources:\n{sources_block or '(none)'}\n\n"
            "Grade faithfulness."
        )
        verdict = _judge(self.SYSTEM, user)
        self.score = float(verdict.score)
        self.reason = verdict.reason
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self) -> str:  # type: ignore[override]
        return "Faithfulness"


# ---------------------------------------------------------------------------
# Metric 3 — LLM-judged: did the answer answer the question?
# ---------------------------------------------------------------------------

class AnswerRelevancyMetric(BaseMetric):
    """Did the tutor answer the question that was asked?

    The judge sees the question, the ideal answer (the rubric), and the
    actual answer. Refusals on "no source" / "vague" cases score 1.0 when
    they match the ideal refusal posture.
    """

    threshold: float = PASS_THRESHOLD

    SYSTEM = (
        "You are an evaluator grading whether an SDR tutor's answer ADDRESSES the "
        "user's question. You are given the question, a rubric describing what a "
        "good answer looks like, and the actual answer. Score 1.0 if the answer "
        "covers the rubric, 0.5 if it answers part of the question or stays high "
        "level, 0.0 if it is off-topic or evades a question that the rubric says "
        "should be answered directly. Return JSON: {score: float in [0,1], reason: "
        "one short sentence}."
    )

    def __init__(self, threshold: float = PASS_THRESHOLD):
        self.threshold = threshold
        self.score: float = 0.0
        self.success: bool = False
        self.reason: str = ""

    def measure(self, test_case: LLMTestCase) -> float:
        user = (
            f"Question: {test_case.input}\n\n"
            f"Rubric (what a good answer looks like):\n{test_case.expected_output}\n\n"
            f"Actual answer:\n{test_case.actual_output}\n\n"
            "Grade relevancy."
        )
        verdict = _judge(self.SYSTEM, user)
        self.score = float(verdict.score)
        self.reason = verdict.reason
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self) -> str:  # type: ignore[override]
        return "AnswerRelevancy"


# ---------------------------------------------------------------------------
# Metric 4 — LLM-judged: face validity for an SDR context
# ---------------------------------------------------------------------------

class SDRFaceValidityMetric(BaseMetric):
    """Would a brand-new SDR find this useful and immediately actionable?

    Cares about tone (plain, peer-level), specificity (not generic advice),
    and whether the suggested next step is something an SDR can do today.
    """

    threshold: float = PASS_THRESHOLD

    SYSTEM = (
        "You are an SDR manager reviewing an AI tutor's answer for a brand-new "
        "SDR (week one). Score 1.0 if the answer is concrete, in plain "
        "language, sounds like advice from a peer, and ends with one action the "
        "SDR could actually take today. Score 0.5 if it's helpful but generic. "
        "Score 0.0 if it sounds like marketing copy, dodges the question, or has "
        "no actionable step. Return JSON: {score: float in [0,1], reason: one short "
        "sentence}."
    )

    def __init__(self, threshold: float = PASS_THRESHOLD):
        self.threshold = threshold
        self.score: float = 0.0
        self.success: bool = False
        self.reason: str = ""

    def measure(self, test_case: LLMTestCase) -> float:
        user = (
            f"Question: {test_case.input}\n\n"
            f"Answer:\n{test_case.actual_output}\n\n"
            "Grade face validity."
        )
        verdict = _judge(self.SYSTEM, user)
        self.score = float(verdict.score)
        self.reason = verdict.reason
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self) -> str:  # type: ignore[override]
        return "SDRFaceValidity"


def _format_retrieval_context(ctx: list[str]) -> str:
    parts: list[str] = []
    for i, item in enumerate(ctx, start=1):
        # We encode entries as "<doc_name>::<passage>". Fall back if missing.
        if "::" in item:
            doc, passage = item.split("::", 1)
        else:
            doc, passage = "unknown", item
        parts.append(f"[{i}] {doc}\n{passage}")
    return "\n\n".join(parts)


ALL_METRIC_CLASSES = [
    CitationAndNextStepMetric,
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    SDRFaceValidityMetric,
]
