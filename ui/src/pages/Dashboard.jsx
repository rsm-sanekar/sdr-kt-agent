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
  GraduationCap,
  MessageCircleQuestion,
} from "lucide-react"
import { getDashboardMetrics } from "../lib/api"
import { formatScore } from "../lib/format"

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

function CertFunnel({ summary }) {
  if (!summary) return null
  const cells = [
    { label: "Pass", value: summary.pass, cls: "text-emerald-600", bg: "bg-emerald-50" },
    { label: "Borderline", value: summary.borderline, cls: "text-amber-600", bg: "bg-amber-50" },
    { label: "Fail", value: summary.fail, cls: "text-red-600", bg: "bg-red-50" },
  ]
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <GraduationCap className="h-4 w-4 text-gray-500" />
        <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold">
          Certification cohort
        </div>
        <span className="ml-auto text-xs text-gray-400">{summary.total} SDRs</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {cells.map((c) => (
          <div key={c.label} className={`${c.bg} rounded-xl p-4 text-center`}>
            <div className={`text-3xl font-extrabold ${c.cls}`}>{c.value}</div>
            <div className="text-xs uppercase tracking-wider text-gray-500 mt-1">{c.label}</div>
          </div>
        ))}
      </div>
      {summary.top_weak_dimension && (
        <div className="mt-4 text-sm text-gray-600">
          Most common weak dimension:{" "}
          <span className="font-semibold text-gray-900">{summary.top_weak_dimension}</span>
        </div>
      )}
      {summary.not_analyzed > 0 && (
        <div className="mt-1 text-xs text-gray-400">{summary.not_analyzed} not yet analyzed</div>
      )}
    </div>
  )
}

function TraineeQuestions({ questions }) {
  const needs = (questions || []).filter((q) => q.status === "needs_review")
  const answered = (questions || []).filter((q) => q.status === "answered")
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-1">
        <MessageCircleQuestion className="h-4 w-4 text-gray-500" />
        <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold">
          Trainee questions — be ready to answer
        </div>
      </div>
      <p className="text-xs text-gray-500 mb-4">
        Questions trainees asked the AI Tutor. The flagged ones below are where the AI was unsure
        or a reviewer rejected the answer — worth prepping a human answer or adding to the KB.
      </p>
      {!questions || questions.length === 0 ? (
        <div className="text-sm text-gray-500">No tutor questions yet.</div>
      ) : (
        <div className="flex flex-col gap-4">
          {needs.length > 0 && (
            <div className="flex flex-col gap-2">
              {needs.map((q, i) => (
                <div key={i} className="bg-amber-50 border border-amber-200 rounded-md p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                        q.kind === "rejected"
                          ? "bg-red-100 text-red-700"
                          : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      {q.kind === "rejected" ? "Rejected" : "Low confidence"}
                    </span>
                    {typeof q.confidence_score === "number" && (
                      <span className="text-xs text-gray-500">match {formatScore(q.confidence_score)}</span>
                    )}
                    <span className="ml-auto text-xs text-gray-400">{formatTimestamp(q.timestamp)}</span>
                  </div>
                  <div className="text-sm font-semibold text-gray-900">{q.question}</div>
                  {q.answer && (
                    <div className="mt-1 text-xs text-gray-600">
                      <span className="font-semibold">AI said:</span> {q.answer}
                    </div>
                  )}
                  <div className="mt-1 text-xs text-amber-700">{q.detail}</div>
                </div>
              ))}
            </div>
          )}
          {answered.length > 0 && (
            <div>
              <div className="text-xs uppercase tracking-wider text-gray-400 font-semibold mb-2">
                Recently answered
              </div>
              <div className="flex flex-col gap-1.5">
                {answered.map((q, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                    <CheckCircle className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                    <span className="flex-1 truncate">{q.question}</span>
                    <span className="text-xs text-gray-400">{q.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function SectionHeading({ children }) {
  return (
    <h2 className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-3 mt-8">
      {children}
    </h2>
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
            KB health, certification outcomes, tutor questions, and decision activity.
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
          {/* KPI strip — every headline number, nothing dropped. */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
            <MetricCard
              label="Open gaps"
              value={metrics.open_gap_count || 0}
              sublabel="low-confidence + rejected tutor answers"
              accent="amber"
            />
            <MetricCard
              label="Est. time saved"
              value={`${Math.round(((metrics.estimated_time_saved_min || 0) / 60) * 10) / 10} hrs`}
              sublabel="estimated from logged approvals — see estimates.md"
              accent="emerald"
            />
          </div>

          <SectionHeading>Certification &amp; decisions</SectionHeading>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CertFunnel summary={metrics.certification_summary} />
            <RatesBreakdown summary={metrics} />
          </div>

          <SectionHeading>AI Tutor — trainee questions</SectionHeading>
          <TraineeQuestions questions={metrics.tutor_questions} />

          <SectionHeading>Activity</SectionHeading>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RecentDecisions decisions={metrics.recent_decisions} />
            <BaselineTargets targets={metrics.baseline_targets} />
          </div>
        </>
      )}
    </div>
  )
}
