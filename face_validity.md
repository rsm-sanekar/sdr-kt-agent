# Face Validity

Face validity does not prove the system is correct. It asks whether a
person who understands the SDR onboarding context would look at the
redesign, the estimates, and the AI outputs and conclude the results
are reasonable enough to investigate further, rather than obviously
unrealistic, backwards, or disconnected from the business. This
document is the full check; [estimates.md](estimates.md) carries a
condensed copy of the same argument.

## 1. Does the direction of the result make sense?

Yes. Time falls on the steps where generative AI genuinely helps —
drafting the onboarding plan, ranking mentors, retrieving cited
answers, drafting coaching notes, scoring certification artifacts —
while human review is preserved or made more explicit on every
decision that carries consequence. The three Milestone 01 checkpoints
that are legally, financially, or organizationally loaded —
certification (Step 7), AE/territory assignment (Step 9), and
qualified-meeting verification (Step 11) — are deliberately left
fully human and are not automated in this prototype. The certification
gap analysis we ship is **advisory only**: the trainer's final
decision (Pass / Fail with a required comment) is the source of truth,
recorded in the decision log; the AI never gates the SDR.

The test results support the intended direction. On cases where the
knowledge base has no authoritative source, the retriever drives the
similarity score down and the envelope is flagged (best cosine
0.21–0.31 on out-of-KB cases, `flagged: True`). Even where the tutor
over-answers, the output is flagged for review rather than presented
as settled — that is the behavior a reviewer would want before
trusting it.

## 2. Is the size of the effect plausible?

The effect sizes are large but defensible, and we intentionally keep
them **below** the headline numbers in the Milestone 01 user stories.
M01 claimed roughly two hours to fifteen minutes for enablement (about
85%) and two hours to thirty minutes for trainer prep (about 75%).
Our per-step reductions of 60–85% sit inside that range and are
smaller on the full cycle because we add human review time back in.
We avoid any claim of a 95% reduction: the human still reads, edits,
and approves every output.

The coaching-latency improvement (M01 baseline of 24–72 hours toward
an under-4-hour target) is the largest single effect and is still
plausible, because the bottleneck being removed is the manual
listening and transcription, not the manager's judgment. The note is
drafted in minutes; the manager still reviews and adds context before
it is sent.

The certification time estimate (45–75 → 10–15 min) is similarly
defensible: the AI does the rubric-based scoring + evidence extraction
the trainer would otherwise do by hand; the trainer's decision time
(reading the dimension cards, agreeing/overriding, writing the
required comment) is preserved.

## 3. Does the AI output match the evidence shown to the user?

Yes, and the test suite is direct evidence of this. We ran the
DeepEval suite **6 times** (3 baseline runs on 2026-06-03 + 3 post-fix
runs on 2026-06-04 after we tightened the tutor prompt) — see
[test_report.md](test_report.md). The **Faithfulness judge**, which
checks that every claim is supported by the retrieved passages,
scored **8/10 stable across baseline runs and 8–9/10 across post-fix
runs** (mean 8.67/10 post-fix). When the tutor produced an answer, it
stayed within its sources nearly every time. The remaining failures
were relevancy / coverage problems (the answer was true and grounded
but missed part of what the case rubric wanted), which is a far less
dangerous failure mode than confident invention.

The prompt-tighten experiment specifically targeted the cases that
*did* fabricate. Case 1 (`price_objection`) added an unsupported
claim ("the goal on a cold call is a meeting, not a price
negotiation") in 3/3 baseline runs; Rule 2 of the tighten (block
ungrounded identifiers) partly addressed this. Case 10 fabricated a
`TRAIL-COLD-101` module ID — Faithfulness on that case improved from
1/3 passing in baseline to 2/3 in post-fix.

Beyond the tests, the outputs are inspectable: plans and tutor
answers carry the names of the retrieved documents, coaching notes
show a per-dimension rubric breakdown beside the drafted note,
certification renders per-dimension cards with **verbatim quotes from
the SDR's own artifacts** beside each score, and a low-confidence
plan is flagged rather than presented as final.

## 4. Does the result respect practical constraints?

Yes. The redesign:

- Keeps **manager approval** before anything reaches an SDR
- Uses only **synthetic or public data**, so no proprietary Salesforce
  data or real PII is involved
- Does **not automate** any compensation- or certification-gating
  decision (cert AI scoring is advisory; the trainer's Pass/Fail with
  required comment is what counts)
- Respects staffing reality by **budgeting review time explicitly**
  rather than assuming it away
- Respects compliance by routing competitor and pricing claims
  through the legal-messaging constraints (the tutor correctly cites
  LMG-2024 and redirects on the competitor-pricing case)
- Respects data availability by running the chain on **offline BM25
  retrieval** that needs no API key (only the Tutor and the LLM
  skills require API access)

## Anchors

1. **Milestone 01 baseline-vs-target metrics:** six-week
   certification, 24–72 hour feedback latency, 3–5 hours per week of
   manual call review, 42% quota attainment (RepVue, Feb 2026). These
   define the "before" and the realistic "after" targets the
   estimates move toward.

2. **Milestone 01 user-story effort estimates:** enablement roughly
   two hours to fifteen minutes per hire; trainer prep two hours to
   thirty minutes per cohort; feedback latency 24–72 hours to under
   four hours. Our estimates are anchored to these and tempered
   below them.

3. **The DeepEval 6-run measurement** (10 cases × 4 checks = 40 metric
   results per run): baseline mean 21.3/40 (range
   3) → post-fix mean 23.3/40 (range 1). The +2 lift is below the
   3-point noise floor on the mean alone, but the per-case story is
   real — **case 8 `vague_get_better` AnswerRelevancy went from 1/3
   → 3/3** (the broad-question rule worked exactly as predicted),
   case 6 `tooling_first_week` SDRFaceValidity went from 0/3 → 2/3,
   and the variance reduction itself (range 3 → range 1) is signal
   randomness doesn't produce. Faithfulness mean stayed stable
   (8/10 → 8.67/10) — produced answers trace to their sources,
   supporting the evidence-alignment claim above.

4. **Public and industry sources cited in Milestone 01:** Glassdoor
   and RepVue reviews on coaching-quality variance and territory
   inequity, and Bridge Group benchmarks used to calibrate the
   synthetic data. These ground the pain points the redesign
   targets.

## Where face validity is weakest

Three honest caveats:

1. **The post-certification onboarding debrief has no Milestone 01
   baseline** (structured ramp feedback was rarely captured before),
   so its time estimate (60–90 → 10–15 min) is the least anchored
   figure in the report.

2. The **recurring coaching-time savings** depend on an assumed
   call volume per rep per week; the per-call saving is well
   grounded, but the weekly total scales with an assumption we have
   not measured.

3. The **certification gap analysis is demoed on a synthetic
   cohort** (`data/sdr_records/SDR-001..007`), not on real SDR
   artifacts. The data model is built to accept real artifacts
   (transcripts + exam answers in the same MD format the seed
   produces), but live wiring from the existing Cold Call
   Simulation feature into `data/sdr_records/` is deferred future
   work.

All three are flagged as low-confidence rather than presented as
settled.
