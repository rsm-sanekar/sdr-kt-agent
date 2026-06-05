const DIM_LABELS = {
  opening_and_framing: "Opening & framing",
  discovery_quality: "Discovery quality",
  objection_handling: "Objection handling",
  close_and_next_step: "Close & next step",
}

function scoreColor(score) {
  if (score >= 7) return "text-emerald-600"
  if (score >= 4) return "text-amber-600"
  return "text-red-600"
}

function scoreBarColor(score) {
  if (score >= 7) return "bg-emerald-500"
  if (score >= 4) return "bg-amber-500"
  return "bg-red-500"
}

function DimensionRow({ name, dim }) {
  const score = dim?.score ?? 0
  const pct = (score / 10) * 100
  return (
    <div className="mb-4 last:mb-0">
      <div className="flex items-center justify-between gap-2 mb-1">
        <div className="text-sm font-semibold text-gray-900">
          {DIM_LABELS[name] || name}
        </div>
        <div className="text-xs text-gray-500">weight {dim.weight.toFixed(2)}</div>
      </div>
      <div className="flex items-center gap-3 mb-1">
        <div className={`text-2xl font-bold ${scoreColor(score)} w-8`}>{score}</div>
        <div className="flex-1 bg-gray-100 rounded-full h-1.5 overflow-hidden">
          <div
            className={`${scoreBarColor(score)} h-1.5 rounded-full`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="text-xs text-gray-400 w-10 text-right">/ 10</div>
      </div>
      <div className="text-xs text-gray-600 leading-relaxed">{dim.rationale}</div>
    </div>
  )
}

/**
 * 4-dimension rubric breakdown — one row per dimension showing score, weight,
 * colored bar, and rationale. Used by Coaching Notes and Cold Call Simulation
 * debrief.
 */
export default function ScoreBreakdown({ dimension_scores }) {
  if (!dimension_scores) return null
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-5">
      <div className="text-xs uppercase tracking-wider text-gray-500 mb-3">
        Dimension breakdown
      </div>
      {Object.entries(dimension_scores).map(([name, dim]) => (
        <DimensionRow key={name} name={name} dim={dim} />
      ))}
    </div>
  )
}
