function scoreColor(score) {
  if (score >= 7) return "text-emerald-600"
  if (score >= 4) return "text-amber-600"
  return "text-red-600"
}

/**
 * Large weighted-total score card used by Coaching Notes + Cold Call
 * Simulation debrief. Color-coded by score band (emerald ≥7, amber ≥4, red <4).
 */
export default function ScoreBadge({ weighted_total, label = "Weighted score", caption = "Coaching Rubric v3.1" }) {
  const t = Number(weighted_total || 0).toFixed(2)
  const cls = scoreColor(weighted_total || 0)
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-5">
      <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">{label}</div>
      <div className="flex items-baseline gap-2">
        <span className={`text-4xl font-extrabold ${cls}`}>{t}</span>
        <span className="text-gray-400 text-sm">/ 10</span>
      </div>
      <div className="text-xs text-gray-500 mt-1">{caption}</div>
    </div>
  )
}
