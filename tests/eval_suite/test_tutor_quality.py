"""DeepEval suite for the SDR AI Tutor.

Two ways to run:

    # Pytest (opt-in — excluded from the default suite by the `deepeval` marker):
    uv run pytest tests/eval_suite/test_tutor_quality.py -m deepeval -v -s

    # Standalone runner (also produces the Markdown results table):
    uv run python -m tests.eval_suite.test_tutor_quality

The standalone form writes ``tests/eval_suite/results/run_<UTC>.md`` and prints
the same table to stdout. The pytest form asserts on each metric per case
(individual failures surface as the usual pytest red/green).
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pytest
from deepeval.test_case import LLMTestCase

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from rag.embeddings_retrieval import EmbedChunk, ensure_index, retrieve  # noqa: E402
from tests.eval_suite.dataset import CASES, TutorCase  # noqa: E402
from tests.eval_suite.metrics import (  # noqa: E402
    PASS_THRESHOLD,
    AnswerRelevancyMetric,
    CitationAndNextStepMetric,
    FaithfulnessMetric,
    SDRFaceValidityMetric,
)

_TUTOR_SCRIPT = REPO_ROOT / "skills" / "answer-sdr-question" / "scripts" / "answer_sdr_question.py"
_TUTOR_MODULE = None


def _load_tutor_module():
    global _TUTOR_MODULE
    if _TUTOR_MODULE is None:
        spec = importlib.util.spec_from_file_location("answer_sdr_question_deepeval", _TUTOR_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _TUTOR_MODULE = mod
    return _TUTOR_MODULE


# ---------------------------------------------------------------------------
# Test-case construction — run the real tutor once per case, build LLMTestCase.
# ---------------------------------------------------------------------------

@dataclass
class TutorRun:
    case: TutorCase
    chunks: list[EmbedChunk]
    answer: str
    next_step: str
    confidence: float
    confidence_score: float
    flagged: bool
    elapsed_s: float
    error: str | None = None

    def as_llm_test_case(self) -> LLMTestCase:
        ctx = [f"{c.doc_name}::{c.passage}" for c in self.chunks]
        tc = LLMTestCase(
            input=self.case.question,
            actual_output=self.answer,
            expected_output=self.case.ideal_answer,
            retrieval_context=ctx,
        )
        # Stash next_step so the deterministic metric can read it.
        tc.additional_metadata = {"next_step": self.next_step}
        return tc


def _run_tutor(case: TutorCase, *, system_prompt_override: str | None = None) -> TutorRun:
    """Run the tutor pipeline against one case using the real LLM.

    Wraps ``do_work`` in try/except so one bad LLM response doesn't kill the
    whole pass — schema-validation failures (and similar) are surfaced as a
    TutorRun with ``error`` set and empty answer/next_step (metrics then score
    that case as a hard fail).

    ``system_prompt_override`` is used by the before/after runner to swap in a
    tighter prompt without permanently editing the skill file.
    """
    mod = _load_tutor_module()
    class _Args:
        question = case.question
        in_step = None
        out_dir = None
        run_id = None
    ensure_index()
    chunks = retrieve(case.question, top_k=5)

    original_prompt = mod.BASE_SYSTEM_PROMPT
    if system_prompt_override is not None:
        mod.BASE_SYSTEM_PROMPT = system_prompt_override
    t0 = time.perf_counter()
    try:
        envelope = mod.do_work(_Args())
        elapsed = time.perf_counter() - t0
        outputs = envelope.get("outputs", {}) or {}
        return TutorRun(
            case=case,
            chunks=chunks,
            answer=outputs.get("answer", ""),
            next_step=outputs.get("next_step", ""),
            confidence=float(envelope.get("confidence") or 0.0),
            confidence_score=float(outputs.get("confidence_score") or 0.0),
            flagged=bool(outputs.get("flagged")),
            elapsed_s=elapsed,
        )
    except Exception as exc:  # noqa: BLE001 — record any failure as a metric fail
        return TutorRun(
            case=case,
            chunks=chunks,
            answer="",
            next_step="",
            confidence=0.0,
            confidence_score=max((c.score for c in chunks), default=0.0),
            flagged=True,
            elapsed_s=time.perf_counter() - t0,
            error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        if system_prompt_override is not None:
            mod.BASE_SYSTEM_PROMPT = original_prompt


# ---------------------------------------------------------------------------
# Pytest entry — one parametrized case, asserts on every metric.
# ---------------------------------------------------------------------------

@pytest.mark.deepeval
@pytest.mark.parametrize("case", CASES, ids=[c.id for c in CASES])
def test_tutor_case(case: TutorCase, request) -> None:
    if not os.environ.get("TRITONAI_API_KEY"):
        pytest.skip("DeepEval suite requires TRITONAI_API_KEY")

    run = _run_tutor(case)
    metric_results = _score_one(case, run)

    # Stash for the session-end report.
    bucket = request.config.stash.setdefault(_RESULTS_KEY, [])
    bucket.append({"case": case, "run": run, "metrics": metric_results})

    failed = [m for m in metric_results if not m["pass"]]
    assert not failed, (
        f"{case.id}: {len(failed)}/{len(metric_results)} metrics failed → "
        + "; ".join(f"{m['name']} ({m['score']:.2f}) {m['reason']}" for m in failed)
    )


_RESULTS_KEY = pytest.StashKey[list]() if hasattr(pytest, "StashKey") else "deepeval_results"


def pytest_terminal_summary(terminalreporter):  # noqa: D401 — pytest hook
    """Emit the Markdown results table at the end of the pytest session."""
    config = terminalreporter.config
    bucket = config.stash.get(_RESULTS_KEY, []) if hasattr(_RESULTS_KEY, "__hash__") else []
    if not bucket:
        return
    md_path = _write_results_markdown(bucket, label="pytest")
    terminalreporter.write_sep("=", "DeepEval results")
    terminalreporter.write_line(f"results table -> {md_path}")


# ---------------------------------------------------------------------------
# Standalone runner — `uv run python -m tests.eval_suite.test_tutor_quality`
# ---------------------------------------------------------------------------

def _score_one(case: TutorCase, run: TutorRun) -> list[dict]:
    """Score every metric for one tutor run.

    If the tutor failed (empty answer or `run.error` set), short-circuit all 4
    metrics to a 0.0 fail rather than spending judge calls on empty input.
    """
    if run.error or not (run.answer or "").strip():
        reason = f"Tutor failed to produce an answer: {run.error or 'empty output'}."
        return [
            {"name": "CitationAndNextStep", "score": 0.0, "pass": False, "reason": reason},
            {"name": "Faithfulness", "score": 0.0, "pass": False, "reason": reason},
            {"name": "AnswerRelevancy", "score": 0.0, "pass": False, "reason": reason},
            {"name": "SDRFaceValidity", "score": 0.0, "pass": False, "reason": reason},
        ]
    tc = run.as_llm_test_case()
    out: list[dict] = []
    for metric_cls in (
        CitationAndNextStepMetric,
        FaithfulnessMetric,
        AnswerRelevancyMetric,
        SDRFaceValidityMetric,
    ):
        metric = metric_cls()
        metric.measure(tc)
        out.append(
            {
                "name": metric.__name__,
                "score": metric.score,
                "pass": metric.is_successful(),
                "reason": metric.reason,
            }
        )
    return out


def run_all(write_table: bool = True) -> list[dict]:
    """Run every case, score every metric, optionally write the table."""
    results: list[dict] = []
    for i, case in enumerate(CASES, start=1):
        print(f"[{i:2d}/{len(CASES)}] {case.id} …", flush=True)
        run = _run_tutor(case)
        if run.error:
            print(f"    ⚠️  tutor errored: {run.error}", flush=True)
        metric_results = _score_one(case, run)
        for m in metric_results:
            status = "✅" if m["pass"] else "❌"
            print(f"    {status} {m['name']:24s} {m['score']:.2f}  — {m['reason']}", flush=True)
        results.append({"case": case, "run": run, "metrics": metric_results})

    if write_table:
        path = _write_results_markdown(results, label="standalone")
        print(f"\nResults table written to: {path}")
    return results


def _write_results_markdown(results: list[dict], *, label: str) -> Path:
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"run_{stamp}_{label}.md"

    total_metric_runs = sum(len(r["metrics"]) for r in results)
    pass_count = sum(1 for r in results for m in r["metrics"] if m["pass"])

    lines: list[str] = []
    lines.append(f"# DeepEval results — {stamp} ({label})")
    lines.append("")
    lines.append(
        f"**{len(results)} cases · {total_metric_runs} metric runs · "
        f"{pass_count} passed · {total_metric_runs - pass_count} failed** "
        f"(pass threshold = {PASS_THRESHOLD:.2f})"
    )
    lines.append("")
    header = "| # | Case | Category | Citation+NextStep | Faithfulness | AnswerRelevancy | SDRFaceValidity | Verdict |"
    lines.append(header)
    lines.append("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(results, start=1):
        c: TutorCase = r["case"]
        run: TutorRun = r["run"]
        metric_cells = []
        all_pass = True
        for m in r["metrics"]:
            mark = "✅" if m["pass"] else "❌"
            metric_cells.append(f"{mark} {m['score']:.2f}")
            if not m["pass"]:
                all_pass = False
        verdict = "PASS" if all_pass else "FAIL"
        lines.append(
            f"| {i} | `{c.id}` | {c.category} | "
            + " | ".join(metric_cells)
            + f" | **{verdict}** |"
        )
    lines.append("")

    for r in results:
        c: TutorCase = r["case"]
        run: TutorRun = r["run"]
        lines.append(f"## `{c.id}` ({c.category})")
        lines.append("")
        lines.append(f"**Question:** {c.question}")
        lines.append("")
        lines.append(f"**Ideal answer (rubric):** {c.ideal_answer}")
        lines.append("")
        lines.append(f"**Expected KB doc:** `{c.expected_doc or '(none — should be flagged)'}`")
        lines.append("")
        retrieved_docs = sorted({ch.doc_name for ch in run.chunks})
        lines.append(f"**Retrieved docs (top-5):** {', '.join(retrieved_docs) if retrieved_docs else '(none)'}")
        lines.append("")
        lines.append(
            f"**Tutor confidence:** {run.confidence:.2f} · "
            f"**best cosine:** {run.confidence_score:.3f} · "
            f"**flagged:** {run.flagged}"
        )
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append("> " + run.answer.replace("\n", "\n> "))
        lines.append("")
        lines.append(f"**Next step:** {run.next_step}")
        lines.append("")
        lines.append("**Metric findings:**")
        lines.append("")
        for m in r["metrics"]:
            mark = "✅" if m["pass"] else "❌"
            lines.append(f"- {mark} **{m['name']}** ({m['score']:.2f}) — {m['reason']}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


if __name__ == "__main__":
    run_all()
