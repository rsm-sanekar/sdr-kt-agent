import { useEffect, useState } from "react"
import {
  CheckCircle,
  Edit,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Loader2,
  AlertCircle,
  Target,
  HelpCircle,
} from "lucide-react"
import { getDashboardMetrics } from "../lib/api"

const PCT = (x) => `${Math.round((x || 0) * 100)}%`
const DATE_FMT = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
})

function formatTimestamp(iso) {
  if (!iso) return ""
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return DATE_FMT.format(d)
}

const ACCENT_TEXT = {
  blue: "text-blue-500",
  emerald: "text-emerald-500",
  amber: "text-amber-500",
  gray: "text-gray-700",
}

function MetricCard({ label, value, sublabel, accent = "blue" }) {
  const cls = ACCENT_TEXT[accent] || ACCENT_TEXT.blue
  return (
    <div className="bg-white border-2 border-gray-100 rounded-2xl p-6">
      <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-3">
        {label}
      </div>
      <div className={`text-4xl font-extrabold ${cls}`}>{value}</div>
      {sublabel && <div className="mt-1 text-xs text-gray-500">{sublabel}</div>}
    </div>
  )
}

function RatesBreakdown({ summary }) {
  const total = summary.total_interactions || 0
  const counts = summary.counts || {}
  const rows = [
    { key: "approve", label: "Approved as-is", color: "bg-blue-500", Icon: CheckCircle },
    { key: "edit", label: "Edited & approved", color: "bg-amber-500", Icon: Edit },
    { key: "reject", label: "Rejected", color: "bg-red-500", Icon: XCircle },
    { key: "escalate", label: "Escalated", color: "bg-gray-500", Icon: AlertTriangle },
  ]
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-6">
      <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-4">
        Decision breakdown
      </div>
      {total === 0 ? (
        <div className="text-sm text-gray-500">
          No decisions logged yet. Approve, reject, or escalate something to populate this view.
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {rows.map((r) => {
            const n = counts[r.key] || 0
            const pct = total ? n / total : 0
            return (
              <div key={r.key}>
                <div className="flex items-center justify-between text-sm mb-1.5">
                  <span className="flex items-center gap-2 text-gray-700">
                    <r.Icon className="h-4 w-4 text-gray-500" />
                    {r.label}
                  </span>
                  <span className="font-mono text-gray-900 font-semibold">
                    {n} ({PCT(pct)})
                  </span>
                </div>
                <div className="bg-gray-100 rounded-full h-1.5 overflow-hidden">
                  <div className={`${r.color} h-1.5 rounded-full transition-all`} style={{ width: `${pct * 100}%` }} />
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function BaselineTargets({ targets }) {
  if (!targets || targets.length === 0) return null
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-1">
        <Target className="h-4 w-4 text-gray-500" />
        <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold">
          Baseline → target (process metrics)
        </div>
        <span className="ml-auto bg-gray-100 text-gray-500 text-[10px] uppercase tracking-wider rounded-full px-2 py-0.5">
          demo
        </span>
      </div>
      <p className="text-xs text-gray-500 mb-5">
        These four metrics aren't derived from this system's own data — they're
        the aspirational "after AI rollout" numbers from the M01 brief.
      </p>
      <div className="flex flex-col gap-5">
        {targets.map((t) => {
          const span = Math.max(0.001, t.baseline - t.target)
          const progress = Math.max(0, Math.min(1, (t.baseline - t.current) / span))
          const onTarget = t.current <= t.target
          return (
            <div key={t.key}>
              <div className="flex items-center justify-between text-sm mb-1.5">
                <span className="text-gray-800 font-semibold">{t.label}</span>
                <span className="font-mono text-gray-700">
                  baseline {t.baseline} → <span className={onTarget ? "text-emerald-600 font-semibold" : "text-amber-600 font-semibold"}>{t.current}</span> ({t.unit}) · target ≤ {t.target}
                </span>
              </div>
              <div className="bg-gray-100 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`${onTarget ? "bg-emerald-500" : "bg-amber-500"} h-1.5 rounded-full transition-all`}
                  style={{ width: `${progress * 100}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

const ACTION_BADGE = {
  approve: { cls: "bg-blue-100 text-blue-700", label: "Approved" },
  edit: { cls: "bg-amber-100 text-amber-700", label: "Edited" },
  reject: { cls: "bg-red-100 text-red-700", label: "Rejected" },
  escalate: { cls: "bg-gray-200 text-gray-800", label: "Escalated" },
}

function RecentDecisions({ decisions }) {
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-6">
      <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-4">
        Recent decisions
      </div>
      {!decisions || decisions.length === 0 ? (
        <div className="text-sm text-gray-500">No decisions yet.</div>
      ) : (
        <div className="flex flex-col gap-2">
          {decisions.map((d, i) => {
            const badge = ACTION_BADGE[d.action] || { cls: "bg-gray-100 text-gray-700", label: d.action }
            const ctx = d.context || {}
            return (
              <div key={`${d.timestamp}-${i}`} className="bg-gray-50 rounded-md p-3 flex items-start gap-3">
                <span className={`${badge.cls} rounded-full px-2 py-0.5 text-xs font-semibold flex-shrink-0`}>
                  {badge.label}
                </span>
                <span className="text-xs uppercase tracking-wider text-gray-500 flex-shrink-0 mt-0.5">
                  {d.feature}
                </span>
                <div className="flex-1 min-w-0 text-sm text-gray-700">
                  {ctx.question && <div className="truncate">Q: {ctx.question}</div>}
                  {ctx.run_id && (
                    <div className="truncate font-mono text-xs text-gray-500">
                      run {ctx.run_id} · at {ctx.at_step}
                    </div>
                  )}
                  {ctx.session_id && (
                    <div className="truncate font-mono text-xs text-gray-500">
                      session {ctx.session_id}
                    </div>
                  )}
                  {ctx.note && !ctx.question && (
                    <div className="text-xs text-gray-500 truncate">note: {ctx.note}</div>
                  )}
                  {ctx.reason && (
                    <div className="text-xs text-red-600 truncate">reason: {ctx.reason}</div>
                  )}
                </div>
                <span className="text-xs text-gray-500 flex-shrink-0">
                  {formatTimestamp(d.timestamp)}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

const GAP_BADGE = {
  low_confidence_query: { cls: "bg-amber-100 text-amber-700", label: "Low confidence" },
  rejected_answer: { cls: "bg-red-100 text-red-700", label: "Rejected" },
}

function OpenGaps({ gaps }) {
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <HelpCircle className="h-4 w-4 text-gray-500" />
        <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold">
          Open gaps ({gaps?.length || 0})
        </div>
      </div>
      {!gaps || gaps.length === 0 ? (
        <div className="text-sm text-gray-500">
          No gaps logged. Low-confidence tutor answers and rejected answers land here.
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {gaps.map((g, i) => {
            const badge = GAP_BADGE[g.type] || { cls: "bg-gray-100 text-gray-700", label: g.type || "gap" }
            return (
              <div key={`${g.timestamp}-${i}`} className="bg-amber-50 rounded-md p-3 flex items-start gap-3">
                <span className={`${badge.cls} rounded-full px-2 py-0.5 text-xs font-semibold flex-shrink-0`}>
                  {badge.label}
                </span>
                <div className="flex-1 min-w-0 text-sm text-gray-700">
                  <div className="font-medium truncate">{g.question || g.rejected_answer || "(no detail)"}</div>
                  {g.reason && <div className="text-xs text-red-600 truncate">reason: {g.reason}</div>}
                  {typeof g.confidence_score === "number" && (
                    <div className="text-xs text-gray-500">best match {g.confidence_score.toFixed(2)}</div>
                  )}
                </div>
                <span className="text-xs text-gray-500 flex-shrink-0">{formatTimestamp(g.timestamp)}</span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const m = await getDashboardMetrics()
      setMetrics(m)
    } catch (err) {
      setError(err.message || "Failed to load dashboard metrics")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="flex items-start justify-between gap-4 flex-wrap mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Dashboard</h1>
          <p className="text-sm text-gray-500">
            KB health, decision activity, and open gaps.
          </p>
        </div>
        <button
          onClick={load}
          className="bg-gray-100 text-gray-900 rounded-md px-4 py-2 hover:bg-gray-200 transition-all flex items-center gap-2 text-sm font-semibold"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {loading && !metrics && (
        <div className="flex items-center gap-3 text-gray-500">
          <Loader2 className="h-5 w-5 animate-spin" />
          Loading metrics…
        </div>
      )}

      {error && (
        <div className="bg-red-50 rounded-lg p-4 flex items-start gap-2 text-red-700 text-sm mb-6">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {metrics && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <MetricCard
              label="KB chunks"
              value={metrics.kb_chunk_count}
              sublabel="ChromaDB (sdr_tutor_kb)"
              accent="blue"
            />
            <MetricCard
              label="Approval rate"
              value={PCT((metrics.approval_rate || 0) + (metrics.edit_rate || 0))}
              sublabel={`includes ${PCT(metrics.edit_rate)} edited`}
              accent="emerald"
            />
            <MetricCard
              label="Edit rate"
              value={PCT(metrics.edit_rate)}
              sublabel="approve with edits"
              accent="amber"
            />
            <MetricCard
              label="Total interactions"
              value={metrics.total_interactions || 0}
              sublabel="tutor + chain + coaching + offboarding"
              accent="gray"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <RatesBreakdown summary={metrics} />
            <BaselineTargets targets={metrics.baseline_targets} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RecentDecisions decisions={metrics.recent_decisions} />
            <OpenGaps gaps={metrics.open_gaps} />
          </div>
        </>
      )}
    </div>
  )
}
