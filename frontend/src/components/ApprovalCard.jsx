import { useState } from 'react'

// status: 'idle' | 'approved' | 'edited' | 'rejected'
export default function ApprovalCard({
  result,
  status = 'idle',
  onApprove,
  onEdit,
  onReject,
  editableContent = '',
  extraContent = null,
}) {
  const [editMode, setEditMode] = useState(false)
  const [editedText, setEditedText] = useState('')

  function startEdit() {
    setEditedText(editableContent || result?.answer || '')
    setEditMode(true)
  }
  function saveEdit() {
    if (editedText.trim()) { onEdit(editedText.trim()); setEditMode(false) }
  }

  const cardBg =
    status === 'approved' ? 'bg-emerald-50 border-emerald-500' :
    status === 'edited'   ? 'bg-amber-50 border-amber-500' :
    status === 'rejected' ? 'bg-red-50 border-red-300 opacity-60' :
    'bg-gray-50 border-gray-200'

  return (
    <div className={`border-2 rounded-lg p-6 ${cardBg} transition-all duration-300`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {/* Shield icon */}
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" className="text-gray-500">
            <path d="M9 1L2 4v5c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V4L9 1z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" fill="none"/>
            <path d="M6 9l2 2 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span className="font-semibold text-gray-900 text-sm">Human Checkpoint Required</span>
          {status === 'approved' && <span className="text-emerald-600 text-sm font-semibold">✓ Approved</span>}
          {status === 'edited'   && <span className="text-amber-600 text-sm font-semibold">✓ Approved with edits</span>}
          {status === 'rejected' && <span className="text-red-500 text-sm font-semibold">✗ Rejected</span>}
        </div>

        {/* Metadata pills */}
        <div className="flex items-center gap-2">
          {result?.generation_time != null && (
            <span className="bg-gray-100 text-gray-500 text-xs font-medium px-2.5 py-1 rounded-full">
              {result.generation_time.toFixed(2)}s
            </span>
          )}
          {result?.model && (
            <span className="bg-gray-100 text-gray-500 text-xs font-medium px-2.5 py-1 rounded-full">
              {result.model}
            </span>
          )}
          {result?.token_count != null && (
            <span className="bg-gray-100 text-gray-500 text-xs font-medium px-2.5 py-1 rounded-full">
              {result.token_count} tokens
            </span>
          )}
        </div>
      </div>

      {/* Extra content slot (e.g. dual-approval for offboarding) */}
      {extraContent}

      {/* Edit mode */}
      {editMode && (
        <div className="mb-4">
          <textarea
            rows={6}
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            className="w-full bg-white border-2 border-gray-200 rounded-lg px-4 py-3 text-sm text-gray-800 focus:outline-none focus:border-blue-400 resize-y"
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={saveEdit}
              className="bg-emerald-500 text-white text-sm font-semibold px-4 py-2 rounded-md hover:bg-emerald-600 transition-scale hover:scale-105"
            >
              Save edit
            </button>
            <button
              onClick={() => setEditMode(false)}
              className="bg-gray-100 text-gray-700 text-sm font-medium px-4 py-2 rounded-md hover:bg-gray-200"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Action buttons */}
      {status === 'idle' && !editMode && (
        <div className="flex items-center gap-3">
          <button
            onClick={onApprove}
            className="bg-emerald-500 text-white text-sm font-semibold px-5 py-2 rounded-md hover:bg-emerald-600 transition-scale hover:scale-105"
          >
            Approve
          </button>
          <button
            onClick={startEdit}
            className="bg-gray-100 text-gray-900 text-sm font-medium px-5 py-2 rounded-md hover:bg-gray-200 transition-colors"
          >
            Edit
          </button>
          <button
            onClick={onReject}
            className="border-4 border-red-500 text-red-500 text-sm font-semibold px-5 py-2 rounded-md hover:bg-red-500 hover:text-white transition-scale hover:scale-105 ml-auto"
          >
            Reject
          </button>
        </div>
      )}

      {/* Rationale */}
      {status === 'idle' && !editMode && (
        <p className="text-xs text-gray-400 mt-3">
          Approved answers are embedded and written to ChromaDB, improving every future response.
          Edits are tracked separately for academic analysis.
        </p>
      )}
    </div>
  )
}
