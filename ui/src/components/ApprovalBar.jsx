import { useEffect, useState } from "react"
import {
  CheckCircle,
  Edit,
  XCircle,
  Save,
  X,
  Loader2,
} from "lucide-react"

const TERMINAL_STYLES = {
  approved: { cls: "bg-emerald-50 text-emerald-700 border-emerald-200", label: "Approved", Icon: CheckCircle },
  edited: { cls: "bg-amber-50 text-amber-800 border-amber-200", label: "Edited & approved", Icon: Edit },
  rejected: { cls: "bg-red-50 text-red-700 border-red-200", label: "Rejected", Icon: XCircle },
}

/**
 * Compact top-of-card approval surface. Three inline buttons (Approve / Edit /
 * Reject). Edit and Reject swap the bar into a textarea sub-mode. Terminal
 * statuses (approved / edited / rejected) collapse to a single pill.
 *
 * Parent contract matches `ApprovalCard`:
 *   onApprove(finalContent, { edited: boolean }) — required
 *   onReject(reason: string)                     — required
 */
export default function ApprovalBar({
  status = "idle",
  content,
  onApprove,
  onReject,
  busy = false,
}) {
  const [mode, setMode] = useState("display") // "display" | "edit" | "reject"
  const [editedContent, setEditedContent] = useState(content || "")
  const [reasonText, setReasonText] = useState("")

  // Re-sync editor content if the parent's `content` prop changes (e.g., new
  // session generated) and we're not in the middle of an edit.
  useEffect(() => {
    if (mode === "display") setEditedContent(content || "")
  }, [content, mode])

  if (status in TERMINAL_STYLES) {
    const t = TERMINAL_STYLES[status]
    const Icon = t.Icon
    return (
      <div className={`${t.cls} border-2 rounded-md px-3 py-1.5 inline-flex items-center gap-1.5 text-xs font-semibold mb-3`}>
        <Icon className="h-3.5 w-3.5" />
        {t.label}
      </div>
    )
  }

  if (mode === "edit") {
    const isEdited = editedContent !== (content || "")
    return (
      <div className="mb-3">
        <textarea
          value={editedContent}
          onChange={(e) => setEditedContent(e.target.value)}
          rows={Math.min(20, Math.max(6, (editedContent || "").split("\n").length + 1))}
          className="bg-white rounded-md w-full p-3 text-sm border-2 border-amber-300 focus:border-amber-500 outline-none font-mono"
        />
        <div className="flex gap-2 mt-2">
          <button
            onClick={async () => {
              await onApprove(editedContent, { edited: isEdited })
            }}
            disabled={busy}
            className="bg-amber-500 text-white rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-amber-600 disabled:opacity-60 flex items-center gap-1.5"
          >
            {busy ? <Loader2 className="h-3 w-3 animate-spin" /> : <Save className="h-3 w-3" />}
            Save &amp; approve
          </button>
          <button
            onClick={() => {
              setMode("display")
              setEditedContent(content || "")
            }}
            disabled={busy}
            className="bg-gray-100 text-gray-900 rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-gray-200 disabled:opacity-60 flex items-center gap-1.5"
          >
            <X className="h-3 w-3" />
            Cancel
          </button>
        </div>
      </div>
    )
  }

  if (mode === "reject") {
    return (
      <div className="mb-3">
        <textarea
          value={reasonText}
          onChange={(e) => setReasonText(e.target.value)}
          placeholder="Why reject? One sentence is fine."
          rows={2}
          className="bg-white rounded-md w-full p-3 text-sm border-2 border-red-200 focus:border-red-500 outline-none"
        />
        <div className="flex gap-2 mt-2">
          <button
            onClick={async () => {
              await onReject(reasonText)
              setMode("display")
              setReasonText("")
            }}
            disabled={busy}
            className="bg-red-500 text-white rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-red-600 disabled:opacity-60 flex items-center gap-1.5"
          >
            {busy && <Loader2 className="h-3 w-3 animate-spin" />}
            Confirm reject
          </button>
          <button
            onClick={() => {
              setMode("display")
              setReasonText("")
            }}
            disabled={busy}
            className="bg-gray-100 text-gray-900 rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-gray-200 disabled:opacity-60"
          >
            Cancel
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 mb-3 flex-wrap">
      <button
        onClick={async () => onApprove(content || "", { edited: false })}
        disabled={busy}
        className="bg-blue-500 text-white rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-blue-600 disabled:opacity-60 flex items-center gap-1.5"
      >
        {busy ? <Loader2 className="h-3 w-3 animate-spin" /> : <CheckCircle className="h-3 w-3" />}
        Approve
      </button>
      <button
        onClick={() => {
          setEditedContent(content || "")
          setMode("edit")
        }}
        disabled={busy}
        className="bg-gray-100 text-gray-900 rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-gray-200 disabled:opacity-60 flex items-center gap-1.5"
      >
        <Edit className="h-3 w-3" />
        Edit
      </button>
      <button
        onClick={() => setMode("reject")}
        disabled={busy}
        className="border-2 border-red-200 text-red-600 bg-white rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-red-50 disabled:opacity-60 flex items-center gap-1.5"
      >
        <XCircle className="h-3 w-3" />
        Reject
      </button>
    </div>
  )
}
