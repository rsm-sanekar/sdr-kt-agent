import { useEffect, useRef, useState } from "react"
import { BookOpen, FileText, AlertTriangle, X } from "lucide-react"
import { formatScore } from "../lib/format"

/**
 * Compact chip-cluster source panel. One numbered pill per source — click to
 * expand its full passage below.
 *
 * When the parent owns the expanded state (via ``expandedIndex`` +
 * ``onExpandedChange``), inline citations elsewhere on the page can drive
 * this panel. Otherwise it falls back to internal state.
 *
 * `sources` shape (consistent across the tutor and every chain skill):
 *   [{ doc_name: string, passage: string, score: number, weak: boolean }]
 */
export default function EvidencePanel({
  sources,
  title = "Sources",
  expandedIndex,
  onExpandedChange,
}) {
  const [internal, setInternal] = useState(null)
  const controlled = onExpandedChange != null
  const expanded = controlled ? (expandedIndex ?? null) : internal
  const setExpanded = controlled ? onExpandedChange : setInternal

  const cardRef = useRef(null)
  useEffect(() => {
    if (expanded != null && cardRef.current) {
      cardRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" })
    }
  }, [expanded])

  if (!sources || sources.length === 0) return null

  const open = expanded != null ? sources[expanded - 1] : null

  return (
    <div className="mt-4">
      <div className="flex items-center gap-2 mb-2">
        <BookOpen className="h-3.5 w-3.5 text-gray-400" />
        <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold">
          {title} ({sources.length})
        </div>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {sources.map((src, i) => {
          const n = i + 1
          const isOpen = expanded === n
          return (
            <button
              key={`${src.doc_name}-${i}`}
              id={`source-${n}`}
              onClick={() => setExpanded(isOpen ? null : n)}
              title={src.passage?.slice(0, 220) || src.doc_name}
              className={`text-xs rounded-md px-2 py-1 flex items-center gap-1.5 transition-colors border-2 ${
                isOpen
                  ? "bg-blue-100 border-blue-500"
                  : "bg-blue-50 border-transparent hover:border-blue-300"
              } ${src.weak ? "ring-1 ring-amber-300" : ""}`}
            >
              <span className="font-semibold text-blue-700">[{n}]</span>
              <FileText className="h-3 w-3 text-blue-600" />
              <span className="text-blue-900 max-w-[14rem] truncate">{src.doc_name}</span>
              {src.weak && <AlertTriangle className="h-3 w-3 text-amber-600" />}
            </button>
          )
        })}
      </div>

      {open && (
        <div
          ref={cardRef}
          className="mt-3 bg-white border-2 border-gray-100 rounded-lg p-4"
        >
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-900 min-w-0">
              <FileText className="h-4 w-4 text-gray-400 flex-shrink-0" />
              <span className="truncate">
                <span className="text-blue-700">[{expanded}]</span> {open.doc_name}
              </span>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <span className="text-xs text-gray-500">
                score {formatScore(open.score)}
              </span>
              <button
                onClick={() => setExpanded(null)}
                className="text-gray-400 hover:text-gray-700"
                aria-label="close"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
          <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
            {open.passage || "(no passage available)"}
          </div>
          {open.weak && (
            <div className="mt-2 flex items-center gap-1 text-xs text-amber-700 font-semibold">
              <AlertTriangle className="h-3 w-3" />
              Weak match — review carefully before relying on this source.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
