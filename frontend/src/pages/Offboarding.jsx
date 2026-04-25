import { useState } from 'react'
import { generateOffboarding, approveOffboarding } from '../api.js'
import ApprovalCard from '../components/ApprovalCard.jsx'

const QUESTIONS = [
  'What are your top 3 accounts and what makes each one strategic?',
  'What objections do you encounter most, and how do you handle them?',
  'What outreach sequences or tools have worked best in your territory?',
  'What do you wish you had known when you started this role?',
  'Any ongoing relationships or warm opportunities the incoming SDR should know about?',
]

function RiskBadge({ risk }) {
  if (!risk) return null
  const upper = risk.toUpperCase()
  const style = upper.startsWith('HIGH')
    ? 'bg-red-100 text-red-700'
    : upper.startsWith('MEDIUM')
      ? 'bg-amber-100 text-amber-700'
      : 'bg-emerald-100 text-emerald-700'
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${style}`}>{risk}</span>
  )
}

function AccountCard({ acct }) {
  return (
    <div className="bg-white rounded-lg p-5 border-l-4 border-blue-500">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-bold text-gray-900">{acct.company}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">{acct.stage}</span>
            {acct.deal_size_usd && (
              <span className="text-xs font-semibold text-gray-600">
                ${(acct.deal_size_usd / 1000).toFixed(0)}k
              </span>
            )}
            <RiskBadge risk={acct.risk} />
          </div>
        </div>
      </div>

      <div className="space-y-1.5 text-sm text-gray-600">
        {acct.champion && (
          <div className="flex gap-2">
            <span className="font-medium text-gray-500 w-28 shrink-0">Champion</span>
            <span>{acct.champion}</span>
          </div>
        )}
        {acct.economic_buyer && (
          <div className="flex gap-2">
            <span className="font-medium text-gray-500 w-28 shrink-0">Econ. Buyer</span>
            <span>{acct.economic_buyer}</span>
          </div>
        )}
        {acct.next_action && (
          <div className="flex gap-2">
            <span className="font-medium text-gray-500 w-28 shrink-0">Next action</span>
            <span className="text-blue-700">{acct.next_action}</span>
          </div>
        )}
        {acct.notes && (
          <div className="mt-2 bg-gray-50 rounded px-3 py-2 text-xs text-gray-500 italic">
            {acct.notes}
          </div>
        )}
      </div>
    </div>
  )
}

function docToText(result, repName, territory) {
  if (!result) return ''
  const lines = [`HANDOFF DOCUMENT — ${repName} | ${territory}\n`]
  if (result.summary) lines.push(`Summary: ${result.summary}\n`)
  if (result.key_accounts?.length) {
    lines.push('KEY ACCOUNTS:')
    result.key_accounts.forEach(a => {
      lines.push(`  ${a.company} (${a.stage}, $${(a.deal_size_usd / 1000).toFixed(0)}k)`)
      if (a.champion) lines.push(`    Champion: ${a.champion}`)
      if (a.economic_buyer) lines.push(`    Econ. Buyer: ${a.economic_buyer}`)
      if (a.next_action) lines.push(`    Next: ${a.next_action}`)
      if (a.risk) lines.push(`    Risk: ${a.risk}`)
      if (a.notes) lines.push(`    Notes: ${a.notes}`)
    })
  }
  if (result.territory_insights?.length) {
    lines.push('\nTERRITORY INSIGHTS:')
    result.territory_insights.forEach(i => lines.push(`  • ${i}`))
  }
  if (result.lessons_learned?.length) {
    lines.push('\nLESSONS LEARNED:')
    result.lessons_learned.forEach(l => lines.push(`  • ${l}`))
  }
  return lines.join('\n')
}

export default function Offboarding() {
  const [phase, setPhase] = useState('setup')

  const [repName, setRepName] = useState('')
  const [territory, setTerritory] = useState('')
  const [tenureMonths, setTenureMonths] = useState('')

  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState(Array(QUESTIONS.length).fill(''))

  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [approvalStatus, setApprovalStatus] = useState('idle')
  const [managerApproved, setManagerApproved] = useState(false)

  function setAnswer(val) {
    setAnswers(prev => { const next = [...prev]; next[step] = val; return next })
  }

  function handleStart() {
    if (!repName.trim() || !territory.trim()) return
    setStep(0)
    setAnswers(Array(QUESTIONS.length).fill(''))
    setPhase('interview')
  }

  async function handleNext() {
    if (step < QUESTIONS.length - 1) { setStep(s => s + 1); return }
    setLoading(true)
    setError(null)
    try {
      const interview_answers = {}
      QUESTIONS.forEach((_, i) => { interview_answers[`Q${i + 1}`] = answers[i] || '' })
      const data = await generateOffboarding({
        departing_rep_name: repName,
        territory,
        tenure_months: parseInt(tenureMonths) || 12,
        interview_answers,
      })
      setResult(data)
      setPhase('result')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleApprove() {
    try {
      await approveOffboarding({
        doc_id: result.doc_id,
        departing_rep_name: repName,
        approved_content: docToText(result, repName, territory),
        was_edited: false,
        manager_approved: managerApproved,
      })
      setApprovalStatus('approved')
    } catch (e) { setError(e.message) }
  }

  async function handleEdit(editedText) {
    try {
      await approveOffboarding({
        doc_id: result.doc_id,
        departing_rep_name: repName,
        approved_content: editedText,
        was_edited: true,
        manager_approved: managerApproved,
      })
      setApprovalStatus('edited')
    } catch (e) { setError(e.message) }
  }

  /* ── Setup ── */
  if (phase === 'setup') {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Offboarding KT</h1>
          <p className="text-gray-500">
            Capture departing SDR knowledge through a structured interview.
            GPT-4o synthesizes the answers into a handoff document stored in the KB.
          </p>
        </div>
        <div className="max-w-lg space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Departing SDR Name</label>
            <input type="text" value={repName} onChange={e => setRepName(e.target.value)}
              placeholder="e.g. Jordan Martinez"
              className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Territory</label>
            <input type="text" value={territory} onChange={e => setTerritory(e.target.value)}
              placeholder="e.g. AMER West"
              className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Tenure <span className="text-gray-400 font-normal">(months)</span>
            </label>
            <input type="number" value={tenureMonths} onChange={e => setTenureMonths(e.target.value)}
              placeholder="e.g. 18"
              className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500" />
          </div>
          <button onClick={handleStart} disabled={!repName.trim() || !territory.trim()}
            className="w-full bg-blue-500 text-white font-semibold py-3 rounded-md hover:bg-blue-600 hover:scale-105 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100">
            Start Interview
          </button>
        </div>
      </div>
    )
  }

  /* ── Interview ── */
  if (phase === 'interview') {
    const isLast = step === QUESTIONS.length - 1
    return (
      <div>
        <div className="mb-6">
          <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Offboarding KT</h1>
          <p className="text-gray-500">{repName} · {territory}</p>
        </div>

        {/* Progress bar */}
        <div className="flex items-center gap-2 mb-8">
          {QUESTIONS.map((_, i) => (
            <div key={i}
              className={`h-1.5 flex-1 rounded-full transition-colors duration-300 ${i <= step ? 'bg-blue-500' : 'bg-gray-200'}`} />
          ))}
          <span className="text-xs font-semibold text-gray-400 ml-2 shrink-0">{step + 1}/{QUESTIONS.length}</span>
        </div>

        <div className="max-w-2xl">
          <p className="text-xl font-bold text-gray-900 mb-6">{QUESTIONS[step]}</p>
          <textarea
            rows={6}
            value={answers[step]}
            onChange={e => setAnswer(e.target.value)}
            placeholder="Share as much detail as you can…"
            className="w-full bg-gray-100 rounded-md px-4 py-3 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500 resize-none"
          />
          <div className="flex items-center gap-3 mt-4">
            {step > 0 && (
              <button onClick={() => setStep(s => s - 1)}
                className="text-sm font-medium text-gray-500 hover:text-gray-700">
                ← Back
              </button>
            )}
            <button
              onClick={handleNext}
              disabled={!answers[step]?.trim() || loading}
              className="bg-blue-500 text-white font-semibold px-6 py-2.5 rounded-md hover:bg-blue-600 hover:scale-105 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {loading ? 'Generating…' : isLast ? 'Generate Handoff Doc →' : 'Next →'}
            </button>
          </div>
          {error && <p className="text-red-500 text-sm mt-4">{error}</p>}
        </div>
      </div>
    )
  }

  /* ── Result ── */
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Handoff Document</h1>
        <p className="text-gray-500">{repName} · {territory} · {result?.tenure_months} months tenure</p>
      </div>

      {/* Summary */}
      {result?.summary && (
        <div className="bg-blue-50 rounded-lg p-4 mb-6 border-l-4 border-blue-500">
          <p className="text-sm font-semibold text-blue-700 mb-1">Summary</p>
          <p className="text-sm text-blue-800">{result.summary}</p>
        </div>
      )}

      {/* Key accounts */}
      {result?.key_accounts?.length > 0 && (
        <div className="mb-6">
          <h2 className="font-bold text-gray-900 mb-3">Key Accounts</h2>
          <div className="space-y-4">
            {result.key_accounts.map((acct, i) => <AccountCard key={i} acct={acct} />)}
          </div>
        </div>
      )}

      {/* Two-column: insights + lessons */}
      {(result?.territory_insights?.length > 0 || result?.lessons_learned?.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {result.territory_insights?.length > 0 && (
            <div>
              <h2 className="font-bold text-gray-900 mb-3">Territory Insights</h2>
              <ul className="space-y-2">
                {result.territory_insights.map((insight, i) => (
                  <li key={i} className="flex gap-2 text-sm text-gray-700">
                    <span className="text-blue-500 shrink-0 font-bold">→</span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {result.lessons_learned?.length > 0 && (
            <div>
              <h2 className="font-bold text-gray-900 mb-3">Lessons Learned</h2>
              <ul className="space-y-2">
                {result.lessons_learned.map((lesson, i) => (
                  <li key={i} className="flex gap-2 text-sm text-gray-700">
                    <span className="text-amber-500 shrink-0 font-bold">•</span>
                    <span>{lesson}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      <ApprovalCard
        result={result}
        status={approvalStatus}
        onApprove={handleApprove}
        onEdit={handleEdit}
        onReject={() => setApprovalStatus('rejected')}
        editableContent={docToText(result, repName, territory)}
        extraContent={
          <div className="flex items-center gap-3 mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <input type="checkbox" id="manager-check" checked={managerApproved}
              onChange={e => setManagerApproved(e.target.checked)}
              className="w-4 h-4 accent-blue-500" />
            <label htmlFor="manager-check" className="text-sm font-medium text-gray-700 cursor-pointer">
              Manager has reviewed and approved this handoff document
            </label>
          </div>
        }
      />
    </div>
  )
}
