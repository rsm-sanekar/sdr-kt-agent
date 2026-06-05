import { useState } from "react"
import {
  CheckCircle,
  Edit,
  XCircle,
  AlertTriangle,
  Loader2,
  Save,
  X,
} from "lucide-react"

/**
 * Reusable human-in-the-loop approval card.
 *
 * Status state machine (driven by the parent):
 *   "idle"      → buttons visible, no terminal styling
 *   "approved"  → emerald background, no buttons
 *   "edited"    → amber background, "Edited & approved" badge
 *   "rejected"  → red background, no buttons
 *   "escalated" → amber background, "Escalated" badge (chain only)
 *
 * Action contract (handlers all return a Promise so the parent can manage busy state):
 *   onApprove(finalContent, { edited: boolean })  — required
 *   onReject(reason: string)                       — required
 *   onEscalate(reason: string)                     — optional (chain only)
 *
 * The card never owns the terminal state — the parent passes `status` based on
 * whatever the backend confirmed. Reject reason flows through `onReject`.
 */
export default function ApprovalCard({
  status = "idle",
  content,
  onApprove,
  onReject,
  onEscalate,
  allowEscalate = false,
  allowEdit = true,
  busy = false,
  footerNote,
}) {
  const [mode, setMode] = useState("display")
  const [editedContent, setEditedContent] = useState(content || "")
  const [reasonText, setReasonText] = useState("")

  const styles = STATE_STYLES[status] || STATE_STYLES.idle
  const StatusIcon = styles.label?.icon
  const isTerminal = TERMINAL_STATES.has(status)

  const handleApprove = async () => {
    const final = mode === "edit" ? editedContent : (content || "")
    const isEdited = mode === "edit" && final !== (content || "")
    await onApprove(final, { edited: isEdited })
    if (mode === "edit") setMode("display")
  }

  const handleConfirmReject = async () => {
    await onReject(reasonText)
    setMode("display")
    setReasonText("")
  }

  const handleConfirmEscalate = async () => {
    if (!onEscalate) return
    await onEscalate(reasonText)
    setMode("display")
    setReasonText("")
  }

  return (
    <div className={`${styles.bg} border-2 ${styles.border} rounded-lg p-6 mt-6`}>
      <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
        <div className="text-xl font-bold text-gray-900">Human review</div>
        {styles.label && (
          <span
            className={`flex items-center gap-1 text-xs font-semibold uppercase tracking-wider ${styles.label.cls}`}
          >
            <StatusIcon className="h-4 w-4" />
            {styles.label.text}
          </span>
        )}
      </div>

      {/* DISPLAY MODE — show prompt + buttons */}
      {!isTerminal && mode === "display" && (
        <>
          <p className="text-gray-600 text-sm">
            Review the output above. Approve to commit, edit to refine before
            approval, or reject to log a gap.
          </p>
          <div className="flex gap-3 mt-4 flex-wrap">
            <button
              onClick={handleApprove}
              disabled={busy}
              className="bg-blue-500 text-white rounded-md px-6 h-11 font-semibold hover:bg-blue-600 hover:scale-105 transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center gap-2"
            >
              {busy ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle className="h-4 w-4" />
              )}
              Approve
            </button>
            {allowEdit && (
              <button
                onClick={() => {
                  setEditedContent(content || "")
                  setMode("edit")
                }}
                disabled={busy}
                className="bg-gray-100 text-gray-900 rounded-md px-6 h-11 font-semibold hover:bg-gray-200 hover:scale-105 transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center gap-2"
              >
                <Edit className="h-4 w-4" />
                Edit
              </button>
            )}
            <button
              onClick={() => setMode("reject")}
              disabled={busy}
              className="border-4 border-red-500 text-red-500 bg-transparent rounded-md px-6 h-11 font-semibold hover:bg-red-500 hover:text-white transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <XCircle className="h-4 w-4" />
              Reject
            </button>
            {allowEscalate && (
              <button
                onClick={() => setMode("escalate")}
                disabled={busy}
                className="bg-amber-100 text-amber-700 rounded-md px-6 h-11 font-semibold hover:bg-amber-200 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <AlertTriangle className="h-4 w-4" />
                Escalate
              </button>
            )}
          </div>
        </>
      )}

      {/* EDIT MODE — textarea + save / cancel */}
      {!isTerminal && mode === "edit" && (
        <>
          <p className="text-gray-600 text-sm mb-2">
            Edit the output. Saving stores the edited version as the
            human-approved record.
          </p>
          <textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            rows={Math.min(20, Math.max(8, (editedContent || "").split("\n").length + 2))}
            className="bg-white rounded-md w-full p-4 text-sm border-2 border-amber-300 focus:border-amber-500 outline-none font-mono"
          />
          <div className="flex gap-3 mt-4 flex-wrap">
            <button
              onClick={handleApprove}
              disabled={busy}
              className="bg-amber-500 text-white rounded-md px-6 h-11 font-semibold hover:bg-amber-600 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {busy ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              Save & approve edited
            </button>
            <button
              onClick={() => {
                setMode("display")
                setEditedContent(content || "")
              }}
              disabled={busy}
              className="bg-gray-100 text-gray-900 rounded-md px-6 h-11 font-semibold hover:bg-gray-200 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <X className="h-4 w-4" />
              Cancel
            </button>
          </div>
        </>
      )}

      {/* REJECT / ESCALATE REASON */}
      {!isTerminal && (mode === "reject" || mode === "escalate") && (
        <>
          <p className="text-gray-600 text-sm mb-2">
            {mode === "reject"
              ? "Why are you rejecting? Logged to the gap tracker so a human can fill it."
              : "Why are you escalating? Logged for senior review."}
          </p>
          <textarea
            value={reasonText}
            onChange={(e) => setReasonText(e.target.value)}
            placeholder="One sentence is fine."
            rows={3}
            className="bg-white rounded-md w-full p-4 text-sm border-2 border-gray-300 focus:border-red-500 outline-none"
          />
          <div className="flex gap-3 mt-4 flex-wrap">
            <button
              onClick={mode === "reject" ? handleConfirmReject : handleConfirmEscalate}
              disabled={busy}
              className={`${
                mode === "reject"
                  ? "bg-red-500 hover:bg-red-600"
                  : "bg-amber-500 hover:bg-amber-600"
              } text-white rounded-md px-6 h-11 font-semibold transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2`}
            >
              {busy && <Loader2 className="h-4 w-4 animate-spin" />}
              Confirm {mode === "reject" ? "reject" : "escalate"}
            </button>
            <button
              onClick={() => {
                setMode("display")
                setReasonText("")
              }}
              disabled={busy}
              className="bg-gray-100 text-gray-900 rounded-md px-6 h-11 font-semibold hover:bg-gray-200 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </div>
        </>
      )}

      {footerNote && (
        <div className="mt-4 text-xs text-gray-500 border-t border-gray-200 pt-3">
          {footerNote}
        </div>
      )}
    </div>
  )
}

const STATE_STYLES = {
  idle: { bg: "bg-gray-50", border: "border-gray-200", label: null },
  approved: {
    bg: "bg-emerald-50",
    border: "border-emerald-500",
    label: { icon: CheckCircle, text: "Approved", cls: "text-emerald-700" },
  },
  edited: {
    bg: "bg-amber-50",
    border: "border-amber-500",
    label: { icon: Edit, text: "Edited & approved", cls: "text-amber-700" },
  },
  rejected: {
    bg: "bg-red-50",
    border: "border-red-400",
    label: { icon: XCircle, text: "Rejected", cls: "text-red-700" },
  },
  escalated: {
    bg: "bg-amber-50",
    border: "border-amber-500",
    label: { icon: AlertTriangle, text: "Escalated", cls: "text-amber-700" },
  },
}

const TERMINAL_STATES = new Set(["approved", "edited", "rejected", "escalated"])
