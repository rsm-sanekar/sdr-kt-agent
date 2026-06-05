// Canonical 7-question post-certification debrief script. Mirrors
// skills/generate-handoff-doc/QUESTIONS.md — keep both in sync. The frontend
// walks a newly-certified SDR through these in order and POSTs the answers to
// /offboarding/synthesize, which synthesizes a manager-facing onboarding debrief.
export const OFFBOARDING_QUESTIONS = [
  {
    id: 1,
    title: "Most valuable onboarding content",
    prompt: "Which parts of your onboarding plan or Trailhead modules were most valuable — and which should we drop or replace?",
    placeholder: "Name specific modules/steps and why they did (or didn't) help.",
  },
  {
    id: 2,
    title: "How the AI Tutor helped",
    prompt: "How did the AI Tutor help during your ramp, and where did it fall short?",
    placeholder: "What you asked it, what it answered well, and any gaps it didn't cover.",
  },
  {
    id: 3,
    title: "Cold-call simulation realism",
    prompt: "Did the cold-call simulation match the real prospects in your territory? Why or why not?",
    placeholder: "Personas, objections, difficulty — what felt realistic vs. off.",
  },
  {
    id: 4,
    title: "A piece of coaching that landed",
    prompt: "Describe one piece of coaching feedback you got and how it changed your approach.",
    placeholder: "The feedback, what you did differently, and whether it worked.",
  },
  {
    id: 5,
    title: "Biggest barrier to ramp",
    prompt: "What was the biggest thing that slowed your ramp — process, knowledge, tooling, or confidence?",
    placeholder: "Be concrete about what blocked you and when.",
  },
  {
    id: 6,
    title: "Territory / vertical surprises",
    prompt: "What territory- or vertical-specific knowledge surprised you or was missing from the playbook?",
    placeholder: "Things you had to learn the hard way that should be in the program.",
  },
  {
    id: 7,
    title: "One thing to change",
    prompt: "If you could change one thing about the onboarding program, what would it be?",
    placeholder: "Your single highest-impact suggestion for the next cohort.",
  },
]
