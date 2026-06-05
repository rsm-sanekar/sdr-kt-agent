// Shared display formatters so confidence, scores, and dates render
// consistently across every screen.

/** 0.62 -> "62%". Handles null/undefined gracefully. */
export function formatConfidence(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—"
  return `${Math.round(Number(value) * 100)}%`
}

/** A retrieval/match score in [0,1] -> 2 decimals (e.g. 0.84). */
export function formatScore(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—"
  return Number(value).toFixed(2)
}

/** ISO timestamp -> "Jun 5, 2026, 2:14 PM". Falls back to the raw string. */
export function formatTimestamp(iso) {
  if (!iso) return "—"
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  })
}

/** ISO timestamp -> "Jun 5, 2026" (date only). */
export function formatDate(iso) {
  if (!iso) return "—"
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })
}
