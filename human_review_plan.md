# Human Review and Control Plan

This plan covers **eight steps** of the SDR onboarding workflow: the
three steps of the orchestrated pre-boarding chain plus its review
gate, and the five on-demand AI coworker features used across the ramp,
at certification, and at offboarding. **Five** of the steps include an
explicit human review or approval point (marked **Yes** below); the
specifics of what the human sees at each are detailed under the table.

| # | Process step | What the AI does | What the human does | Human approval required? | What could go wrong? | What should happen if there is a problem? |
|---|---|---|---|---|---|---|
| 1 | **Generate onboarding plan** (chain step 1) | Adapts the gold-standard template to the hire's profile and summary, grounded in retrieved KB chunks; sets a confidence score and flags the run for review when confidence is low. | Reviews the plan, its cited sources, and the confidence warning at the gate; approves, edits, rejects, or escalates. | **Yes** | AI recommends modules outside the hire's vertical, or cites a policy the KB does not actually support. | Manager edits the plan inline (the edit overwrites the stored artifact) or rejects it and reruns the step. |
| 2 | **Rank Trail Guide mentors** (chain step 2) | Scores candidate AE mentors on a deterministic 5-component score and returns a ranked table with the top two matches. No GenAI. | Reviews the ranked table at the gate and confirms the mentor, or overrides for interpersonal context the data cannot see. | No (confirmed inside the gate) | Top-ranked mentor is a poor personality fit, or the underlying AE data is stale. | Manager overrides the ranking and assigns a different mentor; the override is recorded in the decision log. |
| 3 | **Draft welcome email** (chain step 3) | Slot-fills a 4-paragraph template from the hire profile and the top-ranked mentor. No LLM, no RAG; auto-completes at confidence 1.0. | Reads the drafted email in the run view and edits any section before it is sent. | No (editable before send) | Wrong mentor name or experience-level paragraph filled in if an upstream artifact was malformed. | Manager edits the email text directly, or rejects the run so the upstream step reruns. |
| 4 | **AI Tutor answer** (Step 4 Q&A) | Retrieves the most relevant KB chunks and answers with inline citations; refuses and redirects when no authoritative source exists. | Reviews the cited answer and either approves it or rejects it with a note. | **Yes** | AI answers confidently from a weak or irrelevant chunk, or invents a detail not in the cited source. | Manager rejects the answer with a note; the SDR is pointed to a 1:1 with their mentor or manager instead. |
| 5 | **Cold-call simulation debrief** (Step 5) | Plays a prospect persona for the trainee, then scores the conversation on 4 rubric dimensions and writes a debrief (what worked, what to improve, language alternatives). | Trainer reads the debrief and adds qualitative coaching in the following 1:1. | No (advisory) | Persona behaves unrealistically, or the rubric score does not match the conversation quality. | Trainer disregards the score and coaches from the transcript directly; the trainee can replay the session. |
| 6 | **Coaching note from transcript** (Step 10) | Scores an uploaded call transcript against Coaching Rubric v3.1 and drafts a structured coaching note. | Reviews the score breakdown and drafted note, adds relational context, and approves or edits before it reaches the SDR. | **Yes** | Unfair or inaccurate feedback reaches a ramping rep, damaging confidence; transcript was incomplete. | Manager edits the note before sending, or rejects it; the note is not delivered to the SDR until approved. |
| 7 | **Certification gap analysis** (Step 7) | Scores an SDR's simulation transcripts and certification exam answers against the 5-dimension rubric (product knowledge, objection handling, MEDDIC, value messaging, discovery); recomputes the band server-side from per-dimension scores; quotes the evidence behind each score. | Reads per-dimension cards with quoted evidence + retrieved rubric passages + journey context; submits a required-comment Pass or Fail decision. May re-run the analysis. | **Yes** | LLM quotes the wrong passage or self-reports the wrong band (verdict drift). | Server-side band-recompute overwrites the LLM's verdict; mismatch is appended to `review_reasons`; trainer overrides with their own decision + required comment in the decision log. |
| 8 | **Onboarding debrief — manager review** | Surfaces every newly-certified SDR's submitted debrief in a queue with territory, vertical, and element count. On click, renders the full debrief: summary for the manager, per-element feedback (what worked / what to improve), ramp barriers, what worked well, suggested improvements, retrieved sources. | Reads the debrief, edits or appends context, then approves (shares with enablement), edits, or rejects. | **Yes** | AI over- or under-states a program issue, or generalizes from a sparse answer. | Manager edits the affected section, or rejects the doc and asks the SDR for a fuller answer. |

The trainee-side debrief intake (a newly-certified SDR picks their own name
from a dropdown that auto-fills territory/vertical/experience from
`sdr_profiles.csv`, then answers 7 process-feedback questions about their
12-week ramp) is a separate step with no approval gate — the debrief
synthesis routes directly to the manager's review queue, where step 8
applies.

## What the human sees at each review point

**Generate onboarding plan (chain gate).** When a run pauses, the gate
surfaces the full AI-generated plan, the names of the KB documents
that were retrieved (from `retrieved_docs` on the envelope), the
step's confidence score, and an explicit low-confidence warning when
present. Controls: approve, edit, reject, escalate. An approve-with-edit
overwrites the stored artifact so any downstream step and the run view
see the human-approved version.

**AI Tutor answer.** The reviewer sees the tutor's answer with its
inline `[n]` citation markers, the KB passages those citations point
to (rendered in an `EvidencePanel`), and the answer's required next
step. Controls: approve, or reject with a note. A refusal (no
authoritative source found) is shown as such rather than as a confident
answer; refusals still cite at least one `[n]` from the retrieved set
to show what was checked.

**Coaching note.** The manager sees the per-dimension score breakdown
(rendered as `ScoreBreakdown` + `ScoreBadge`), the overall score
badge, the 3 note sections (what worked / what to improve / language
alternatives), and the underlying transcript. Controls: approve, or
edit then approve. The note does not reach the SDR until the manager
signs off.

**Certification gap analysis.** The trainer sees 5 dimension cards
(one per rubric dimension), each with a 1–10 score, the verdict band
(pass / borderline / fail) coloured by the **server-side band
recompute** (the source of truth — the LLM's self-reported verdict is
overwritten if it disagrees), the evidence quoted from the SDR's own
artifacts (simulation transcripts + certification exam), the gap to
close, and the coaching action drawn from the rubric. Below the cards,
an `EvidencePanel` shows the retrieved rubric passages; a "Supporting
context — not scored" panel shows coaching-note history and tutor
activity so the trainer sees trajectory beyond the scored artifacts.
Raw artifact MDs are expandable inline. Controls: Pass, Fail, and a
**required-comment textarea** (submit disabled until comment present).
A separate "Re-run gap analysis" button overwrites the cache with a
fresh LLM call. The header banner notes the AI recommendation is
advisory.

**Onboarding debrief (manager review).** The reviewer sees the
synthesized debrief: a summary, per-element feedback (what worked / what
to improve for the onboarding plan, AI Tutor, simulation, coaching,
playbook), ramp barriers, program strengths, suggested improvements, and
the source passages the synthesis used. Controls: approve, edit, or
reject. Approval is logged and the debrief is shared with the enablement
team to improve the program.

## Where the controls send the case

- **Approve** resumes the chain to the next step, or marks a standalone
  feature's output as delivered.
- **Edit** stores the human-corrected version as the artifact of
  record, then proceeds as an approval.
- **Reject** stops the run (status `rejected`) so the step can be
  rerun with corrected input.
- **Escalate** stops the run (status `escalated`) and routes it out of
  the automated chain to a human owner.

Every decision (approve / edit / reject / escalate) is appended to
[data/decision_log.json](data/decision_log.json) with the feature, the
action, the context (artifact refs, comments where required), and a
timestamp. The dashboard reads this log to report approve/edit/reject/
escalate rates per feature.
