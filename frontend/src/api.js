const BASE = ''

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `Server error ${res.status}`)
  return data
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `Server error ${res.status}`)
  return data
}

// ── AI Tutor ────────────────────────────────────────────────────────────────
export const askTutor = (question) =>
  post('/tutor/ask', { question })

export const approveTutor = ({ question, answer, pair_id, was_edited }) =>
  post('/tutor/approve', { question, answer, pair_id, was_edited })

// ── Pre-boarding ─────────────────────────────────────────────────────────────
export const generatePreboarding = ({ sdr_name, territory, vertical, experience_level, notes = '' }) =>
  post('/preboarding/generate', { sdr_name, territory, vertical, experience_level, notes })

export const approvePreboarding = ({ plan_id, sdr_name, approved_plan, was_edited, manager_name = '' }) =>
  post('/preboarding/approve', { plan_id, sdr_name, approved_plan, was_edited, manager_name })

// ── Offboarding ───────────────────────────────────────────────────────────────
export const generateOffboarding = ({ departing_rep_name, territory, tenure_months, interview_answers }) =>
  post('/offboarding/generate', { departing_rep_name, territory, tenure_months, interview_answers })

export const approveOffboarding = ({ doc_id, departing_rep_name, approved_content, was_edited, manager_approved }) =>
  post('/offboarding/approve', { doc_id, departing_rep_name, approved_content, was_edited, manager_approved })

// ── Coaching Notes ────────────────────────────────────────────────────────────
export const generateCoaching = ({ sdr_name, transcript, call_context = '' }) =>
  post('/coaching/generate', { sdr_name, transcript, call_context })

export const approveCoaching = ({ note_id, sdr_name, approved_note, was_edited, manager_name = '', is_zero_edit }) =>
  post('/coaching/approve', { note_id, sdr_name, approved_note, was_edited, manager_name, is_zero_edit })

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const getDashboardMetrics = () => get('/dashboard/metrics')
