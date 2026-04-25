import { useState } from 'react'
import { generatePreboarding, approvePreboarding } from '../api.js'
import ApprovalCard from '../components/ApprovalCard.jsx'

const TERRITORIES = ['AMER West', 'AMER East', 'EMEA', 'APAC', 'Southeast', 'Midwest', 'Northeast', 'Southwest']
const VERTICALS = ['Technology', 'Healthcare', 'Manufacturing', 'Financial Services', 'Retail', 'Media', 'Education']
const EXPERIENCE_LEVELS = ['entry', 'mid', 'senior']

function WeekCard({ week }) {
  return (
    <div className="bg-white rounded-lg p-5 border-l-4 border-blue-500">
      <div className="flex items-start justify-between mb-3">
        <div>
          <span className="text-xs font-semibold text-blue-500 uppercase tracking-wider">Week {week.week}</span>
          <h3 className="font-bold text-gray-900 mt-0.5">{week.theme}</h3>
        </div>
      </div>

      {week.trailhead_badges?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {week.trailhead_badges.map((badge, i) => (
            <span key={i} className="bg-emerald-100 text-emerald-700 text-xs font-medium px-2.5 py-1 rounded-full">
              {badge}
            </span>
          ))}
        </div>
      )}

      <p className="text-sm text-gray-600 mb-2">{week.focus}</p>

      {week.daily_goal && (
        <div className="bg-gray-50 rounded px-3 py-2">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Daily goal · </span>
          <span className="text-xs text-gray-600">{week.daily_goal}</span>
        </div>
      )}
    </div>
  )
}

export default function Preboarding() {
  const [form, setForm] = useState({
    sdr_name: '', territory: '', vertical: '', experience_level: 'entry', notes: '',
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [approvalStatus, setApprovalStatus] = useState('idle')

  function set(field) {
    return e => setForm(f => ({ ...f, [field]: e.target.value }))
  }

  const canGenerate = form.sdr_name.trim() && form.territory && form.vertical && !loading

  async function handleGenerate() {
    if (!canGenerate) return
    setLoading(true)
    setError(null)
    setResult(null)
    setApprovalStatus('idle')
    try {
      const data = await generatePreboarding(form)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function planToText(r) {
    if (!r) return ''
    const lines = [`${r.plan_title || 'Learning Path'} (${r.estimated_weeks} weeks)\n`]
    if (r.sdr_profile_summary) lines.push(`Profile: ${r.sdr_profile_summary}\n`)
    ;(r.weeks || []).forEach(w => {
      lines.push(`\nWeek ${w.week}: ${w.theme}`)
      lines.push(`Badges: ${(w.trailhead_badges || []).join(', ')}`)
      lines.push(`Focus: ${w.focus}`)
      if (w.daily_goal) lines.push(`Daily goal: ${w.daily_goal}`)
    })
    if (r.manager_notes) lines.push(`\nManager notes: ${r.manager_notes}`)
    return lines.join('\n')
  }

  async function handleApprove() {
    try {
      await approvePreboarding({
        plan_id: result.plan_id,
        sdr_name: result.sdr_name || form.sdr_name,
        approved_plan: planToText(result),
        was_edited: false,
      })
      setApprovalStatus('approved')
    } catch (e) {
      setError(e.message)
    }
  }

  async function handleEdit(editedText) {
    try {
      await approvePreboarding({
        plan_id: result.plan_id,
        sdr_name: result.sdr_name || form.sdr_name,
        approved_plan: editedText,
        was_edited: true,
      })
      setApprovalStatus('edited')
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Pre-boarding Generator</h1>
        <p className="text-gray-500">Generate a personalized Salesforce Trailhead learning path for a new SDR based on their profile.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-6">
        {/* Left — Form */}
        <div className="lg:col-span-2 space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">SDR Name</label>
            <input
              type="text"
              value={form.sdr_name}
              onChange={set('sdr_name')}
              placeholder="e.g. Alex Johnson"
              className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Territory</label>
            <select
              value={form.territory}
              onChange={set('territory')}
              className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm text-gray-900 focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500"
            >
              <option value="">Select territory…</option>
              {TERRITORIES.map(t => <option key={t}>{t}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Vertical</label>
            <select
              value={form.vertical}
              onChange={set('vertical')}
              className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm text-gray-900 focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500"
            >
              <option value="">Select vertical…</option>
              {VERTICALS.map(v => <option key={v}>{v}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Experience Level</label>
            <div className="flex gap-2">
              {EXPERIENCE_LEVELS.map(level => (
                <button
                  key={level}
                  onClick={() => setForm(f => ({ ...f, experience_level: level }))}
                  className={`flex-1 py-2 rounded-md text-sm font-medium capitalize transition-all duration-200 hover:scale-105 ${
                    form.experience_level === level
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Manager Notes <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <textarea
              rows={3}
              value={form.notes}
              onChange={set('notes')}
              placeholder="Prior experience, certifications, specific goals…"
              className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500 resize-none"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={!canGenerate}
            className="w-full bg-blue-500 text-white font-semibold py-3 rounded-md hover:bg-blue-600 hover:scale-105 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {loading ? 'Generating…' : 'Generate Learning Path'}
          </button>

          {error && <p className="text-red-500 text-sm">{error}</p>}
        </div>

        {/* Right — Learning path */}
        <div className="lg:col-span-3">
          {result ? (
            <div>
              {/* Plan header */}
              <div className="mb-5">
                <h2 className="font-extrabold text-gray-900 text-xl">{result.plan_title}</h2>
                <p className="text-sm text-gray-400 mt-1">
                  {result.estimated_weeks} weeks · {form.vertical} · {form.territory} · {form.experience_level}
                </p>
                {result.sdr_profile_summary && (
                  <p className="text-sm text-gray-600 mt-2 bg-gray-50 rounded-lg p-3">
                    {result.sdr_profile_summary}
                  </p>
                )}
              </div>

              {/* Week cards */}
              <div className="space-y-4">
                {(result.weeks || []).map(week => (
                  <WeekCard key={week.week} week={week} />
                ))}
              </div>

              {/* Manager notes */}
              {result.manager_notes && (
                <div className="mt-4 bg-amber-50 border-l-4 border-amber-500 rounded-lg p-4">
                  <p className="text-xs font-semibold text-amber-600 uppercase tracking-wider mb-1">Manager Notes</p>
                  <p className="text-sm text-amber-800">{result.manager_notes}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-6 min-h-[300px] flex items-center justify-center text-gray-400 text-sm">
              {loading ? 'Generating personalized learning path…' : 'Fill in the form to generate a learning path'}
            </div>
          )}
        </div>
      </div>

      {result && (
        <ApprovalCard
          result={result}
          status={approvalStatus}
          onApprove={handleApprove}
          onEdit={handleEdit}
          onReject={() => setApprovalStatus('rejected')}
          editableContent={planToText(result)}
        />
      )}
    </div>
  )
}
