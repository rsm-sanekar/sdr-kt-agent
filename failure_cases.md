# Predicted Failure Cases

Eight realistic ways the AI coworker or workflow could fail, focused
on practical failures rather than abstract risk. The rightmost column
names the mechanism in the prototype that catches or contains each
one. **Four** of these are exercised directly by the DeepEval suite
(noted below the table).

| # | Failure case | Why it might happen | Business consequence | How the user would notice | How your process handles it |
|---|---|---|---|---|---|
| 1 | **AI invents a policy when the KB has no source** | The user asks something outside the 16 knowledge-base docs and the model tries to be helpful anyway. | An SDR follows a fabricated policy (e.g. a made-up rule on ROI calculators), creating compliance or legal exposure. | The Evidence panel shows no relevant source, or only weak ones; the answer is flagged for review. | A best-match score below the threshold sets `flagged: true` and `review_required: true`; the tutor is instructed to answer only from numbered sources, and the tightened prompt forces it to cite at least one `[n]` even when refusing. The reviewer rejects an unsupported answer. |
| 2 | **Confident but incomplete answer** | A question needs two documents (e.g. the rubric *and* a vertical playbook) but retrieval surfaces only one. | The SDR gets a polished but partial playbook and misses vertical-specific guidance. | Only one source doc is cited where two were needed; the answer reads complete but omits a required element. | The relevancy and quality checks flag it; the case is reviewed; the fix is better chunking or multi-document retrieval. |
| 3 | **Wrong or weak document retrieved** | Lexical or semantic retrieval matches a superficially similar passage rather than the right one. | A wrong recommendation, such as the wrong escalation path for a silent enterprise prospect. | The source shown in the EvidencePanel does not match the case; the source carries a `weak` flag. | Sources are always surfaced for inspection, weak ones marked; the human rejects the output and reruns the query. |
| 4 | **Vague input produces generic output** | The starting question is under-specified ("how can I get better at my job?"). | The SDR receives generic advice, wastes time, and loses trust in the tool. | The output lacks specifics and offers no concrete next step. | The tightened prompt's **broad-question rule** forces the tutor to refuse and redirect: it names why the question is too broad, proposes 2–3 narrower questions, and recommends a 1:1. Validated by the DeepEval before/after experiment: case 8 AnswerRelevancy went from 1/3 → 3/3. |
| 5 | **Low-confidence onboarding plan** | A thin per-hire summary or a profile mismatch leaves the planner uncertain, e.g. recommending the wrong vertical's modules. | A new hire studies the wrong material in their critical first week. | A confidence warning and the list of retrieved docs are shown at the review gate. | Confidence below 0.60 sets `review_required: true`, which pauses the chain at the gate so the manager edits or rejects before anything reaches the hire. |
| 6 | **Unfair or inaccurate coaching note** | An incomplete or garbled transcript, or a miscalibrated rubric score. | A demoralizing or misleading note reaches a ramping rep. | The score breakdown does not match the transcript, or required fields are blank. | The note requires manager approval or edit before delivery; it is not sent to the SDR until a human signs off. |
| 7 | **A workflow step fails or returns nothing** | A malformed upstream artifact, a missing input file, or a subprocess error. | The pre-boarding run stalls and no package is produced. | The run status shows `rejected` and an error envelope is displayed instead of an artifact. | The orchestrator detects an error or empty envelope, stops the chain, and surfaces it in the run view so the step can be rerun with corrected input. |
| 8 | **Certification verdict drift** (LLM self-reports a different band than the scores warrant) | The LLM gives, say, three dimension scores of 5 but self-reports "PASS"; or quotes an evidence string that does not appear in the SDR's artifact. | Wrong recommendation gets in front of the trainer; an SDR is passed when they are borderline, or vice versa. | The detail view shows the **server-recomputed band** (which differs from what the LLM wrote); `review_reasons` lists the mismatch; the trainer also sees the actual dimension scores beside the verdict. | The server overwrites the LLM's overall verdict and per-dimension verdicts with deterministic re-bandings (≥7 PASS, 5–6 BORDERLINE, ≤4 FAIL); any mismatch sets `review_required: true` and is added to `review_reasons` so the trainer is told *why* the case is flagged. |

## Which of these the tests cover

Four of the failures above are exercised directly by cases in
[tests/eval_suite/dataset.py](tests/eval_suite/dataset.py):

- **#1 — AI invents a policy when the KB has no source** →
  `no_source_fake_roi` (category `no_source`). The case asks for the
  policy on fabricated ROI calculators; the KB has no authoritative
  guidance. The tutor is graded on whether it explicitly says so and
  routes the SDR to legal/manager rather than inventing.

- **#2 — Confident but incomplete answer** →
  `confident_incomplete_perfect_call` (category `confident_incomplete`).
  Asks for "every step of a perfect first cold call"; a complete
  answer needs both the cold-call rubric AND the vertical playbook,
  and citing only one is incomplete.

- **#3 — Wrong or weak document retrieved** → the `wrong_doc`
  category, and in practice the `escalation_silent_enterprise` case,
  which needs more than one source and exposes weak-retrieval
  behavior.

- **#4 — Vague input produces generic output** → `vague_get_better`
  (category `vague`). The DeepEval suite confirmed the tightened
  prompt's broad-question rule fixed this case (AnswerRelevancy
  went from 1/3 in baseline runs to 3/3 in post-fix runs — see
  [test_report.md](test_report.md)).

The remaining four failures (low-confidence plan, unfair coaching
note, step failure, **certification verdict drift**) are contained by
workflow mechanics (`review_required`, the manager approval gate,
the orchestrator's error handling, and the certification server-side
band recompute) rather than by the tutor test suite.
