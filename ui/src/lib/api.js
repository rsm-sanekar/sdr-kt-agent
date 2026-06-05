export const getHires = () =>
  fetch(`http://localhost:8000/hires`).then(r => r.json())

export const startRun = (hireId) =>
  fetch(`http://localhost:8000/run/${hireId}`, {method: "POST"}).then(r => r.json())

export const getRun = (runId) =>
  fetch(`http://localhost:8000/runs/${runId}`).then(r => r.json())

export const approveStep = (runId, decision, note = "", edited_content = null) =>
  fetch(`http://localhost:8000/runs/${runId}/approve`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({decision, note, edited_content}),
  }).then(r => r.json())

export const getRuns = () =>
  fetch(`http://localhost:8000/runs`).then(r => r.json())

// ---------------------------------------------------------------------------
// AI Tutor (Phase 1+2 of M04)
// ---------------------------------------------------------------------------

export const askTutor = (question) =>
  fetch(`http://localhost:8000/tutor/ask`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question}),
  }).then(r => r.json())

export const approveTutorAnswer = (question, answer, edited_answer = null) =>
  fetch(`http://localhost:8000/tutor/approve`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question, answer, edited_answer}),
  }).then(r => r.json())

export const rejectTutorAnswer = (question, answer, reason = "") =>
  fetch(`http://localhost:8000/tutor/reject`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question, answer, reason}),
  }).then(r => r.json())

// ---------------------------------------------------------------------------
// Coaching Notes (M04 — standalone transcript scoring)
// ---------------------------------------------------------------------------

export const scoreCoaching = ({ hire_id, transcript_text, call_context = "", outcome = "unknown" }) =>
  fetch(`http://localhost:8000/coaching/score`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({hire_id, transcript_text, call_context, outcome}),
  }).then(r => r.json())

export const approveCoaching = ({ session_id, decision, note = "", edited_content = null }) =>
  fetch(`http://localhost:8000/coaching/approve`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({session_id, decision, note, edited_content}),
  }).then(r => r.json())

export const getCoachingSession = (sessionId) =>
  fetch(`http://localhost:8000/coaching/sessions/${sessionId}`).then(r => r.json())

// Local Whisper transcription of an uploaded call recording (no API key).
export const transcribeAudio = async (file) => {
  const form = new FormData()
  form.append("file", file)
  const res = await fetch(`http://localhost:8000/coaching/transcribe`, {
    method: "POST",
    body: form,
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail.detail || `Transcription failed (${res.status})`)
  }
  return res.json()
}

// ---------------------------------------------------------------------------
// Onboarding debrief (M04 — post-cert process questions → manager debrief)
// ---------------------------------------------------------------------------

export const synthesizeOffboarding = ({ rep_info, qa_pairs }) =>
  fetch(`http://localhost:8000/offboarding/synthesize`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({rep_info, qa_pairs}),
  }).then(r => r.json())

export const approveOffboarding = ({ session_id, decision, note = "", edited_content = null }) =>
  fetch(`http://localhost:8000/offboarding/${session_id}/approve`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({session_id, decision, note, edited_content}),
  }).then(r => r.json())

export const getOffboardingSession = (sessionId) =>
  fetch(`http://localhost:8000/offboarding/${sessionId}`).then(r => r.json())

export const listOffboardingSessions = () =>
  fetch(`http://localhost:8000/offboarding/sessions`).then(r => r.json())

// ---------------------------------------------------------------------------
// Cold Call Simulation (M04 round 2 — trainee feature)
// ---------------------------------------------------------------------------

export const getPersonas = () =>
  fetch(`http://localhost:8000/simulation/personas`).then(r => r.json())

export const simulateTurn = ({ persona_id, messages }) =>
  fetch(`http://localhost:8000/simulation/turn`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({persona_id, messages}),
  }).then(r => r.json())

export const debriefSimulation = ({ persona_id, messages }) =>
  fetch(`http://localhost:8000/simulation/debrief`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({persona_id, messages}),
  }).then(r => r.json())

// ---------------------------------------------------------------------------
// Certification Gap Analysis (M04 step 7 — manager-view cohort roster)
// ---------------------------------------------------------------------------

export const getCertificationRoster = () =>
  fetch(`http://localhost:8000/certification/roster`).then(r => r.json())

export const getCertificationSDR = (sdrId) =>
  fetch(`http://localhost:8000/certification/sdr/${sdrId}`).then(r => r.json())

export const analyzeCertification = (sdrId) =>
  fetch(`http://localhost:8000/certification/sdr/${sdrId}/analyze`, {
    method: "POST",
  }).then(r => r.json())

export const decideCertification = ({ sdr_id, decision, comment }) =>
  fetch(`http://localhost:8000/certification/decide`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({sdr_id, decision, comment}),
  }).then(r => r.json())

// ---------------------------------------------------------------------------
// Dashboard (Phase 4 of M04)
// ---------------------------------------------------------------------------

export const getDashboardMetrics = () =>
  fetch(`http://localhost:8000/dashboard/metrics`).then(r => r.json())

export const getDashboardGaps = () =>
  fetch(`http://localhost:8000/dashboard/gaps`).then(r => r.json())
