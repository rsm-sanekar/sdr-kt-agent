import { useState, useEffect } from 'react'
import { getDashboardMetrics } from '../api.js'

function MetricCard({ label, value, sub, accent }) {
  return (
    <div className="bg-white border-2 border-gray-100 rounded-2xl p-6">
      <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-4xl font-extrabold mb-1 ${accent || 'text-gray-900'}`}>{value}</div>
      {sub && <div className="text-xs text-gray-400">{sub}</div>}
    </div>
  )
}

function BarChart({ data, color = 'bg-blue-500' }) {
  const max = Math.max(...data.map(d => d.value), 1)
  return (
    <div className="flex items-end gap-3 h-28">
      {data.map((d, i) => (
        <div key={i} className="flex-1 flex flex-col items-center gap-1.5">
          <div className="w-full flex items-end justify-center" style={{ height: '88px' }}>
            <div
              className={`w-full ${color} rounded-t transition-all duration-700`}
              style={{ height: `${Math.max((d.value / max) * 88, 4)}px` }}
            />
          </div>
          <div className="text-xs text-gray-400 text-center truncate w-full leading-tight">{d.label}</div>
        </div>
      ))}
    </div>
  )
}

function ApprovalRow({ item }) {
  const statusStyle = {
    approved: 'bg-emerald-100 text-emerald-700',
    edited:   'bg-amber-100 text-amber-700',
    rejected: 'bg-red-100 text-red-600',
  }[item.status] || 'bg-emerald-100 text-emerald-700'

  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
      <div>
        <div className="text-sm font-medium text-gray-800">{item.type || item.feature}</div>
        {(item.description || item.summary) && (
          <div className="text-xs text-gray-400 mt-0.5">{item.description || item.summary}</div>
        )}
      </div>
      <span className={`text-xs font-semibold px-2.5 py-1 rounded-full shrink-0 ml-4 ${statusStyle}`}>
        {item.status || 'approved'}
      </span>
    </div>
  )
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getDashboardMetrics()
      .then(setMetrics)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-gray-400 text-sm">
        Loading metrics…
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-24 text-red-500 text-sm">
        {error}
      </div>
    )
  }

  if (!metrics) return null

  const kb = metrics.kb_health || {}
  const approvals = metrics.recent_approvals || []
  const weekly = metrics.weekly_interactions || []
  const breakdown = metrics.feature_breakdown || {}

  const totalChunks = kb.total_chunks ?? metrics.total_chunks ?? '—'
  const approvalRate = kb.approval_rate ?? metrics.approval_rate ?? '—'
  const editRate = kb.edit_rate ?? metrics.edit_rate ?? '—'
  const totalInteractions = metrics.total_interactions ?? '—'

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Dashboard</h1>
        <p className="text-gray-500">Knowledge base health and SDR interaction metrics.</p>
      </div>

      {/* Top metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          label="KB Chunks"
          value={totalChunks}
          sub="stored embeddings"
          accent="text-blue-500"
        />
        <MetricCard
          label="Approval Rate"
          value={approvalRate !== '—' ? `${approvalRate}%` : '—'}
          sub="human-approved"
          accent="text-emerald-500"
        />
        <MetricCard
          label="Edit Rate"
          value={editRate !== '—' ? `${editRate}%` : '—'}
          sub="approved with edits"
          accent="text-amber-500"
        />
        <MetricCard
          label="Total Interactions"
          value={totalInteractions}
          sub="across all features"
          accent="text-gray-900"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {weekly.length > 0 && (
          <div className="bg-white border-2 border-gray-100 rounded-2xl p-6">
            <h2 className="font-bold text-gray-900 mb-5">Weekly Interactions</h2>
            <BarChart
              data={weekly.map(w => ({ label: w.week || w.label || '', value: w.count ?? w.value ?? 0 }))}
              color="bg-blue-500"
            />
          </div>
        )}

        {Object.keys(breakdown).length > 0 && (
          <div className="bg-white border-2 border-gray-100 rounded-2xl p-6">
            <h2 className="font-bold text-gray-900 mb-5">By Feature</h2>
            <BarChart
              data={Object.entries(breakdown).map(([label, value]) => ({ label, value }))}
              color="bg-emerald-400"
            />
          </div>
        )}
      </div>

      {/* Baseline vs target */}
      {metrics.baseline_vs_target && (
        <div className="bg-white border-2 border-gray-100 rounded-2xl p-6 mb-6">
          <h2 className="font-bold text-gray-900 mb-4">Baseline vs Target</h2>
          <div className="space-y-4">
            {metrics.baseline_vs_target.map((row, i) => (
              <div key={i}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="font-medium text-gray-700">{row.metric}</span>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-gray-400">Baseline: {row.baseline}</span>
                    <span className="text-blue-600 font-semibold">Target: {row.target}</span>
                    {row.current && (
                      <span className="text-emerald-600 font-semibold">Now: {row.current}</span>
                    )}
                  </div>
                </div>
                <div className="bg-gray-100 rounded-full h-1.5">
                  <div
                    className="bg-blue-500 h-1.5 rounded-full transition-all duration-700"
                    style={{ width: `${Math.min(row.progress ?? 0, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent approvals */}
      {approvals.length > 0 && (
        <div className="bg-white border-2 border-gray-100 rounded-2xl p-6">
          <h2 className="font-bold text-gray-900 mb-2">Recent Approvals</h2>
          <div>
            {approvals.map((a, i) => <ApprovalRow key={i} item={a} />)}
          </div>
        </div>
      )}
    </div>
  )
}
