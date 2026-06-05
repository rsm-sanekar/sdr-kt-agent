import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import {
  Loader2,
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  CheckCircle,
  ChevronRight,
  RefreshCw,
} from "lucide-react"
import {
  listOffboardingSessions,
  getOffboardingSession,
  approveOffboarding,
} from "../lib/api"
import ApprovalCard from "../components/ApprovalCard"
import EvidencePanel from "../components/EvidencePanel"

const STATUS_STYLE = {
  paused: { cls: "bg-amber-100 text-amber-700", label: "Needs review" },
  pending: { cls: "bg-amber-100 text-amber-700", label: "Pending review" },
  complete: { cls: "bg-emerald-100 text-emerald-700", label: "Approved" },
  rejected: { cls: "bg-gray-100 text-gray-500", label: "Rejected" },
  error: { cls: "bg-red-100 text-red-700", label: "Error" },
}

function StatusBadge({ status }) {
  const s = STATUS_STYLE[status] || STATUS_STYLE.pending
  return (
    <span className={`${s.cls} text-xs font-semibold rounded-full px-2.5 py-0.5`}>
      {s.label}
    </span>
  )
}

function ElementCard({ el }) {
  return (
    <div className="bg-white rounded-lg p-5 border-2 border-gray-100 border-l-4 border-l-blue-500">
      <h3 className="font-bold text-gray-900 mb-3">{el.element}</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        <div className="bg-emerald-50 rounded-md p-3">
          <div className="text-xs uppercase tracking-wider text-emerald-700 mb-1">
            What worked
          </div>
          <div className="text-gray-900">{el.what_worked}</div>
        </div>
        <div className="bg-amber-50 rounded-md p-3">
          <div className="text-xs uppercase tracking-wider text-amber-700 mb-1">
            What to improve
          </div>
          <div className="text-gray-900">{el.what_to_improve}</div>
        </div>
      </div>
    </div>
  )
}

function ListCard({ title, items, bullet = "•" }) {
  if (!items?.length) return null
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-5">
      <h3 className="text-sm font-bold text-gray-900 mb-3">{title}</h3>
      <ul className="space-y-2 text-sm text-gray-700">
        {items.map((it, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">{bullet}</span>
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function ReviewReasons({ reasons }) {
  if (!reasons?.length) return null
  return (
    <div className="bg-amber-50 border-2 border-amber-500 rounded-lg p-4">
      <div className="flex items-center gap-2 text-amber-800 font-semibold text-sm mb-2">
        <AlertTriangle className="h-4 w-4" />
        Why manager review is required
      </div>
      <ul className="space-y-1 text-xs text-amber-900">
        {reasons.map((r, i) => (
          <li key={i}>• {r}</li>
        ))}
      </ul>
    </div>
  )
}

function extractSummaryFromMarkdown(md) {
  if (!md) return ""
  const match = md.match(/## Summary\s*\n+([^#]+)/)
  return match ? match[1].trim() : ""
}

function ReviewQueueView() {
  const navigate = useNavigate()
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchRows = () => {
    setLoading(true)
    listOffboardingSessions()
      .then((data) => setRows(data || []))
      .catch((err) => setError(err.message || "Failed to load review queue"))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchRows()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-gray-500 text-sm p-4">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading debrief review queue...
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-md p-4 text-red-700 text-sm flex items-start gap-2">
        <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
        <span>{error}</span>
      </div>
    )
  }

  if (rows.length === 0) {
    return (
      <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-12 text-center">
        <div className="text-gray-500 text-sm">
          No debriefs yet. When a newly-certified SDR completes their onboarding debrief
          on the trainee side, it appears here for your review.
        </div>
        <button
          onClick={fetchRows}
          className="mt-4 bg-white border-2 border-gray-200 text-gray-700 rounded-md px-4 py-2 text-sm font-semibold hover:border-blue-400 hover:text-blue-600 flex items-center gap-2 mx-auto"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh
        </button>
      </div>
    )
  }

  return (
    <>
      <div className="flex items-center justify-between mb-3">
        <div className="text-xs text-gray-500">
          Click any row to review the AI-synthesized onboarding debrief and approve, edit, or
          reject it.
        </div>
        <button
          onClick={fetchRows}
          className="text-xs font-semibold bg-white border border-gray-200 text-gray-700 px-3 py-1.5 rounded-md hover:border-blue-400 hover:text-blue-600 flex items-center gap-1.5"
        >
          <RefreshCw className="h-3 w-3" /> Refresh
        </button>
      </div>
      <div className="bg-white border-2 border-gray-100 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase tracking-wider text-gray-500">
            <tr>
              <th className="text-left px-5 py-3">SDR</th>
              <th className="text-left px-5 py-3">Territory</th>
              <th className="text-left px-5 py-3">Vertical</th>
              <th className="text-left px-5 py-3">Status</th>
              <th className="text-left px-5 py-3">Elements</th>
              <th className="px-5 py-3 w-8"></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.session_id}
                onClick={() => navigate(`/offboarding-reviews/${r.session_id}`)}
                className="border-t border-gray-100 hover:bg-blue-50/60 cursor-pointer transition-colors group"
              >
                <td className="px-5 py-3">
                  <div className="font-semibold text-gray-900 group-hover:text-blue-600">
                    {r.rep_name || "—"}
                  </div>
                  <div className="text-xs font-mono text-gray-400">{r.session_id}</div>
                </td>
                <td className="px-5 py-3 text-gray-700">{r.territory || "—"}</td>
                <td className="px-5 py-3 text-gray-700">{r.vertical || "—"}</td>
                <td className="px-5 py-3">
                  <StatusBadge status={r.status} />
                </td>
                <td className="px-5 py-3 text-gray-700">{r.n_elements ?? "—"}</td>
                <td className="px-5 py-3 text-gray-300 group-hover:text-blue-500">
                  <ChevronRight className="h-4 w-4" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}

function ReviewDetailView({ sessionId }) {
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [decisionStatus, setDecisionStatus] = useState("idle")
  const [decisionBusy, setDecisionBusy] = useState(false)
  const [decisionDetail, setDecisionDetail] = useState(null)

  const fetchSession = () => {
    setLoading(true)
    getOffboardingSession(sessionId)
      .then((s) => setSession(s))
      .catch((err) => setError(err.message || "Failed to load debrief"))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchSession()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

  const handleApprove = async (finalContent, opts) => {
    if (!session) return
    setDecisionBusy(true)
    try {
      const updated = await approveOffboarding({
        session_id: session.session_id,
        decision: "approve",
        note: opts.edited ? "Approved with edits" : "",
        edited_content: opts.edited ? finalContent : null,
      })
      setSession(updated)
      setDecisionStatus(opts.edited ? "edited" : "approved")
      setDecisionDetail(
        opts.edited
          ? "Edited debrief saved and locked."
          : "Debrief approved and shared with the enablement team.",
      )
    } catch (err) {
      setError(err.message || "Failed to approve")
    } finally {
      setDecisionBusy(false)
    }
  }

  const handleReject = async (reason) => {
    if (!session) return
    setDecisionBusy(true)
    try {
      const updated = await approveOffboarding({
        session_id: session.session_id,
        decision: "reject",
        note: reason || "",
      })
      setSession(updated)
      setDecisionStatus("rejected")
      setDecisionDetail("Debrief rejected — it won't be shared.")
    } catch (err) {
      setError(err.message || "Failed to reject")
    } finally {
      setDecisionBusy(false)
    }
  }

  if (loading && !session) {
    return (
      <div className="flex items-center gap-2 text-gray-500 text-sm p-4">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading debrief...
      </div>
    )
  }

  if (error && !session) {
    return (
      <div className="bg-red-50 rounded-md p-4 text-red-700 text-sm flex items-start gap-2">
        <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
        <span>{error}</span>
      </div>
    )
  }

  if (!session) return null

  const envelope = session.envelope || {}
  const outputs = envelope.outputs || {}
  const reviewRequired = envelope.review_required === true
  const isError = envelope.status === "error"
  const repInfo = session.rep_info || {}
  const finalized = decisionStatus === "approved" || decisionStatus === "edited" || decisionStatus === "rejected"
    || session.status === "complete" || session.status === "rejected"

  return (
    <div>
      <button
        onClick={() => navigate("/offboarding-reviews")}
        className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
      >
        <ArrowLeft className="h-4 w-4" /> Back to queue
      </button>

      <div className="flex items-start justify-between gap-3 flex-wrap mb-4">
        <div>
          <h2 className="text-2xl font-extrabold text-gray-900">
            Debrief — {repInfo.name}
          </h2>
          <div className="text-xs text-gray-500 mt-1">
            {repInfo.territory} · {repInfo.vertical} · newly certified
          </div>
        </div>
        <StatusBadge status={session.status} />
      </div>

      {error && (
        <div className="bg-red-50 rounded-md p-3 text-red-700 text-sm flex items-start gap-2 mb-4">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {isError && (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 text-red-700 text-sm flex items-start gap-2 mb-4">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold">Synthesis failed</div>
            <div className="mt-1 text-xs">{envelope.error?.message || "Unknown error"}</div>
          </div>
        </div>
      )}

      {!isError && (
        <div className="flex flex-col gap-5">
          {reviewRequired && <ReviewReasons reasons={outputs.review_reasons} />}

          {(outputs.summary || envelope.confidence !== undefined) && (
            <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
              <div className="text-xs uppercase tracking-wider text-blue-700 font-semibold mb-2">
                Summary for the manager
              </div>
              <div className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
                {outputs.summary || extractSummaryFromMarkdown(session.artifact_content)}
              </div>
              <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                <CheckCircle className="h-3 w-3 text-blue-500" />
                Synthesis confidence: {Number(envelope.confidence || 0).toFixed(2)}
              </div>
            </div>
          )}

          {outputs.elements?.length > 0 && (
            <div>
              <h3 className="font-bold text-gray-900 mb-3">
                Experience by element ({outputs.elements.length})
              </h3>
              <div className="flex flex-col gap-3">
                {outputs.elements.map((el, i) => (
                  <ElementCard key={`${el.element}-${i}`} el={el} />
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ListCard title="Barriers to ramp" items={outputs.ramp_barriers} bullet="▸" />
            <ListCard title="What worked well" items={outputs.program_strengths} />
          </div>

          <ListCard title="Suggested improvements" items={outputs.suggested_improvements} bullet="→" />

          <EvidencePanel sources={outputs.sources} title="Playbook sources used (RAG)" />

          {!finalized && (
            <ApprovalCard
              status={decisionStatus}
              content={session.artifact_content || ""}
              onApprove={handleApprove}
              onReject={handleReject}
              allowEscalate={false}
              busy={decisionBusy}
              footerNote={
                reviewRequired
                  ? "The synthesizer flagged something — review carefully. Approve to share with enablement; edit to fix phrasing first; reject to discard."
                  : "Approve to share this debrief with the enablement team. Edit to fine-tune phrasing first. Reject to discard."
              }
            />
          )}

          {decisionDetail && (
            <div
              className={`rounded-md p-3 text-sm ${
                decisionStatus === "rejected"
                  ? "bg-gray-100 text-gray-700"
                  : decisionStatus === "edited"
                    ? "bg-amber-50 text-amber-800"
                    : "bg-emerald-50 text-emerald-700"
              }`}
            >
              {decisionDetail}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function OffboardingReviews() {
  const { sessionId } = useParams()
  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-gray-900">Debrief reviews</h1>
        <p className="text-sm text-gray-600 mt-1">
          Newly-certified SDRs submit an onboarding debrief from their tab; the AI synthesizes
          their answers into what worked, barriers, and suggested improvements. Review, edit if
          needed, and approve to share with the enablement team.
        </p>
      </div>
      {sessionId ? <ReviewDetailView sessionId={sessionId} /> : <ReviewQueueView />}
    </div>
  )
}
