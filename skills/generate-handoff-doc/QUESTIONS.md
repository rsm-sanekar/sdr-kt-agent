---
name: post-cert-debrief-questions
description: Canonical 7-question script the Onboarding Debrief UI walks a newly-certified SDR through. The skill consumes the resulting Q&A pairs and synthesizes a manager-facing onboarding debrief. Keep this file and ui/src/lib/offboardingQuestions.js in sync.
---

# Post-certification debrief — 7 questions

After an SDR passes certification, they answer these about their 12-week ramp.
The synthesized debrief goes to the Manager / enablement team to improve the program.

| # | Question | What we want from the answer |
|---|---|---|
| 1 | Which parts of your onboarding plan or Trailhead modules were most valuable — and which should we drop or replace? | Specific modules/steps and why they did or didn't help. |
| 2 | How did the AI Tutor help during your ramp, and where did it fall short? | What was asked, what it answered well, and concrete gaps. |
| 3 | Did the cold-call simulation match the real prospects in your territory? Why or why not? | Persona/objection realism vs. what's actually encountered. |
| 4 | Describe one piece of coaching feedback you got and how it changed your approach. | The feedback, the behavior change, and whether it worked. |
| 5 | What was the biggest thing that slowed your ramp — process, knowledge, tooling, or confidence? | A concrete barrier and when it hit. Drives `ramp_barriers`. |
| 6 | What territory- or vertical-specific knowledge surprised you or was missing from the playbook? | Gaps the program should close for the next cohort. |
| 7 | If you could change one thing about the onboarding program, what would it be? | The single highest-impact improvement. |

## Synthesis contract

- The debrief skill (`skills/generate-handoff-doc/scripts/generate_handoff_doc.py`) is the only consumer of the Q&A pairs. It expects a JSON file with shape:

  ```json
  {
    "rep_info": {
      "name": "...",
      "territory": "...",
      "vertical": "..."
    },
    "qa_pairs": [
      {"question_id": 1, "question": "...", "answer": "..."}
    ]
  }
  ```

- It returns a debrief doc: `summary`, `elements` (per onboarding component: what_worked / what_to_improve), `ramp_barriers`, `program_strengths`, `suggested_improvements`, `confidence`. Low confidence flags manager review.
- The frontend mirrors this list in `ui/src/lib/offboardingQuestions.js` so the UI walks the SDR through the same script the backend prompt names. If you add or reorder a question here, update both.
