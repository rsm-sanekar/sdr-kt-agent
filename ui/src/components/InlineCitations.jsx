/**
 * Renders text with `[n]` citation markers turned into clickable pills that
 * surface the matching source in the parent EvidencePanel. The parent owns
 * the expanded-source state and passes ``onCitationClick`` to receive the
 * clicked citation index (1-based).
 */
export default function InlineCitations({ text, onCitationClick }) {
  if (!text) return null
  const parts = text.split(/(\[\d+\])/g)
  return (
    <>
      {parts.map((part, i) => {
        const m = part.match(/^\[(\d+)\]$/)
        if (m) {
          const n = parseInt(m[1], 10)
          return (
            <button
              key={i}
              onClick={() => onCitationClick?.(n)}
              className="inline-flex items-center bg-blue-50 text-blue-700 text-[11px] font-semibold rounded px-1.5 mx-0.5 hover:bg-blue-100 transition-colors align-baseline"
              aria-label={`source ${n}`}
            >
              {n}
            </button>
          )
        }
        return <span key={i}>{part}</span>
      })}
    </>
  )
}
