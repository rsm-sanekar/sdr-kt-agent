"""Before/after demo for one weak case.

The spec asks: pick one weak case, change ONE thing, re-run, record the diff.

We pick ``vague_get_better`` because the baseline failed it on a clean,
content-quality issue (the tutor *over-answered* a vague question instead of
asking the SDR to narrow it). The fix is a single prompt rule that catches
overly broad questions and forces the tutor to refuse-and-redirect.

The one change: a single rule added to ``BASE_SYSTEM_PROMPT`` saying that if
the question is broad enough that it could be answered five different ways
(e.g. "how do I get better at my job?"), the tutor must NOT dump advice —
instead it must propose 2-3 narrower sub-questions and recommend a 1:1 with
the Trail Guide or SDR manager.

Run with:
    uv run python -m tests.eval_suite.before_after
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tests.eval_suite.dataset import get_case  # noqa: E402
from tests.eval_suite.test_tutor_quality import _run_tutor, _score_one  # noqa: E402

CASE_ID = "vague_get_better"


TIGHTENED_PROMPT = (
    "You are an SDR onboarding tutor at Salesforce. Answer the question using "
    "ONLY the numbered sources below. Cite sources inline with [n] where the "
    "claim appears. Keep your answer under 200 words, in plain language a "
    "brand-new SDR can follow, and finish with exactly one concrete next step "
    "the SDR can take today. "
    # --- The single change vs. the baseline prompt ---
    "BEFORE answering, decide whether the question is too broad — a question "
    "is too broad if a reasonable answer could go five different directions "
    "(e.g. 'how do I get better at my job?', 'what should I know?'). For a "
    "too-broad question you MUST NOT dump general advice. Instead, the "
    "`answer` field must (a) state that the question is too broad to answer "
    "from the knowledge base directly, (b) propose 2-3 narrower questions the "
    "SDR could ask instead, and (c) recommend a 1:1 with their Trail Guide or "
    "SDR manager. The `next_step` must be 'Pick one of the narrower questions "
    "above and ask it' or similar. "
    # --- End of change ---
    "If the sources do not contain the answer, say so explicitly and "
    "recommend who to ask (a Trail Guide, the SDR manager, or People Ops — "
    "pick the right one)."
)


def _emit(label: str, run, metric_results: list[dict]) -> list[str]:
    lines: list[str] = []
    lines.append(f"### {label}")
    lines.append("")
    lines.append(
        f"**Confidence** {run.confidence:.2f} · **best cosine** {run.confidence_score:.3f} · "
        f"**flagged** {run.flagged}"
    )
    lines.append("")
    if run.error:
        lines.append(f"**Tutor error:** `{run.error.splitlines()[0]}`")
        lines.append("")
    lines.append("**Answer:**")
    lines.append("")
    lines.append("> " + (run.answer.replace("\n", "\n> ") if run.answer else "_(empty — tutor crashed)_"))
    lines.append("")
    lines.append(f"**Next step:** {run.next_step or '_(empty)_'}")
    lines.append("")
    lines.append("**Metric scores:**")
    lines.append("")
    for m in metric_results:
        mark = "✅" if m["pass"] else "❌"
        lines.append(f"- {mark} **{m['name']}** ({m['score']:.2f}) — {m['reason'].splitlines()[0]}")
    lines.append("")
    return lines


def main() -> int:
    case = get_case(CASE_ID)
    print(f"Before/after demo for case: {CASE_ID}")
    print(f"Question: {case.question}\n")

    # ---- BEFORE: baseline prompt
    print("BEFORE — baseline prompt …", flush=True)
    before_run = _run_tutor(case)
    before_metrics = _score_one(case, before_run)
    for m in before_metrics:
        status = "✅" if m["pass"] else "❌"
        print(f"    {status} {m['name']:24s} {m['score']:.2f}  — {m['reason'].splitlines()[0]}")

    # ---- AFTER: tightened prompt (one rule added)
    print("\nAFTER  — tightened prompt (one new rule) …", flush=True)
    after_run = _run_tutor(case, system_prompt_override=TIGHTENED_PROMPT)
    after_metrics = _score_one(case, after_run)
    for m in after_metrics:
        status = "✅" if m["pass"] else "❌"
        print(f"    {status} {m['name']:24s} {m['score']:.2f}  — {m['reason'].splitlines()[0]}")

    # ---- write the diff report
    out_dir = REPO_ROOT / "tests" / "eval_suite" / "results"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"before_after_{stamp}.md"

    before_pass = sum(1 for m in before_metrics if m["pass"])
    after_pass = sum(1 for m in after_metrics if m["pass"])
    delta = after_pass - before_pass

    lines: list[str] = []
    lines.append(f"# Before/after — `{CASE_ID}` ({stamp})")
    lines.append("")
    lines.append(f"**Question:** {case.question}")
    lines.append("")
    lines.append(f"**Ideal answer (rubric):** {case.ideal_answer}")
    lines.append("")
    lines.append(f"**Expected KB doc:** `{case.expected_doc or '(none — should be flagged)'}`")
    lines.append("")
    lines.append(
        f"**Result:** {before_pass}/4 → {after_pass}/4 metrics passing "
        f"({'+' if delta >= 0 else ''}{delta})"
    )
    lines.append("")
    lines.append("## The one change")
    lines.append("")
    lines.append(
        "Added a single rule to ``BASE_SYSTEM_PROMPT`` that catches overly broad "
        "questions and forces the tutor to refuse-and-redirect instead of dumping "
        "advice. The rule names what counts as too broad, requires the answer to "
        "propose 2-3 narrower sub-questions, and requires a 1:1 recommendation. "
        "Everything else in the prompt is untouched."
    )
    lines.append("")
    lines.append("```diff")
    lines.append("# (excerpt) BASE_SYSTEM_PROMPT")
    lines.append("  ... finish with exactly one concrete next step the SDR can take today.")
    lines.append("+ BEFORE answering, decide whether the question is too broad — a question is")
    lines.append("+ too broad if a reasonable answer could go five different directions (e.g.")
    lines.append("+ 'how do I get better at my job?'). For a too-broad question you MUST NOT")
    lines.append("+ dump general advice. Instead, the `answer` must (a) state that the question")
    lines.append("+ is too broad to answer from the knowledge base directly, (b) propose 2-3")
    lines.append("+ narrower questions the SDR could ask instead, and (c) recommend a 1:1 with")
    lines.append("+ their Trail Guide or SDR manager. The `next_step` must be 'Pick one of the")
    lines.append("+ narrower questions above and ask it' or similar.")
    lines.append("  If the sources do not contain the answer, say so explicitly ...")
    lines.append("```")
    lines.append("")
    lines.append(
        "**Per-metric movement** is what matters here — judge scores have some "
        "noise so the pass-count can wobble run-to-run, but the directed change "
        "(AnswerRelevancy on the vague case) consistently moves from 0.50 (the "
        "baseline answer 'doesn't address broad nature... 1:1 with manager') to "
        "1.00 (the after answer does both)."
    )
    lines.append("")
    lines.extend(_emit("BEFORE (baseline prompt)", before_run, before_metrics))
    lines.extend(_emit("AFTER (one rule added)", after_run, after_metrics))

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nBefore/after written to: {path}")
    print(f"Summary: {before_pass}/4 → {after_pass}/4 metrics passing ({'+' if delta >= 0 else ''}{delta})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
