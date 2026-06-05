import { useEffect, useRef, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import {
  Loader2,
  AlertCircle,
  ArrowLeft,
  RefreshCcw,
  CheckCircle2,
  XCircle,
  Sparkles,
  FileText,
  ChevronRight,
  Printer,
} from "lucide-react"
import {
  getCertificationRoster,
  getCertificationSDR,
  analyzeCertification,
  decideCertification,
} from "../lib/api"
import { printRegion } from "../lib/printDoc"
import EvidencePanel from "../components/EvidencePanel"
import ArtifactCard from "../components/ArtifactCard"

const DIMENSION_ORDER = [
  "product_knowledge_accuracy",
  "objection_handling",
  "meddic_application",
  "salesforce_value_messaging",
  "discovery_and_questioning",
]

const VERDICT_STYLES = {
  PASS: { cls: "bg-emerald-100 text-emerald-700", label: "PASS" },
  BORDERLINE: { cls: "bg-amber-100 text-amber-700", label: "BORDERLINE" },
  FAIL: { cls: "bg-red-100 text-red-700", label: "FAIL" },
  not_analyzed: { cls: "bg-gray-100 text-gray-500", label: "Not analyzed" },
}

const DIM_VERDICT_STYLES = {
  pass: { cls: "bg-emerald-50 text-emerald-700 border-emerald-200", bar: "bg-emerald-500" },
  borderline: { cls: "bg-amber-50 text-amber-700 border-amber-200", bar: "bg-amber-500" },
  fail: { cls: "bg-red-50 text-red-700 border-red-200", bar: "bg-red-500" },
}

function VerdictBadge({ verdict }) {
  const style = VERDICT_STYLES[verdict] || VERDICT_STYLES.not_analyzed
  return (
    <span
      className={`${style.cls} rounded-full text-xs font-bold px-2.5 py-0.5 inline-flex items-center`}
    >
      {style.label}
    </span>
  )
}

const DIMENSION_LABELS = {
  product_knowledge_accuracy: "Product knowledge accuracy",
  objection_handling: "Objection handling (Defuse, Discover, Deliver)",
  meddic_application: "MEDDIC framework application",
  salesforce_value_messaging: "Salesforce value messaging",
  discovery_and_questioning: "Discovery and questioning",
}

function dimensionLabel(dimId, fallback) {
  return DIMENSION_LABELS[dimId] || fallback || dimId
}

function ScoreBar({ score, verdict }) {
  const pct = Math.max(0, Math.min(10, score)) * 10
  const bar = DIM_VERDICT_STYLES[verdict]?.bar || "bg-gray-400"
  return (
    <div className="mt-2">
      <div className="flex items-baseline justify-between mb-1">
        <span className="text-xs uppercase tracking-wider text-gray-500">Score</span>
        <span className="text-sm font-bold text-gray-900">{score}/10</span>
      </div>
      <div className="bg-gray-100 rounded-full h-2 overflow-hidden">
        <div className={`${bar} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function DimensionCard({ dimId, finding }) {
  const style = DIM_VERDICT_STYLES[finding.verdict] || DIM_VERDICT_STYLES.borderline
  return (
    <div className={`rounded-lg border-2 p-5 ${style.cls}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-base font-bold text-gray-900">
            {dimensionLabel(dimId, finding.label)}
          </div>
          <div className="text-xs text-gray-500 mt-0.5 uppercase tracking-wider">
            {finding.verdict}
          </div>
        </div>
      </div>
      <ScoreBar score={finding.score} verdict={finding.verdict} />
      <div className="mt-4 space-y-3 text-sm">
        <div>
          <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">Evidence</div>
          <blockquote className="border-l-2 border-gray-300 pl-3 text-gray-700 italic font-mono text-[13px] leading-relaxed">
            "{finding.evidence_quote}"
          </blockquote>
        </div>
        <div>
          <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">Rationale</div>
          <p className="text-gray-800">{finding.rationale}</p>
        </div>
        <div>
          <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">Gap to close</div>
          <p className="text-gray-800">{finding.gap_to_close}</p>
        </div>
        <div>
          <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">Coaching action</div>
          <p className="text-gray-800">{finding.coaching_action}</p>
        </div>
      </div>
    </div>
  )
}

function JourneyContext({ record, resolvedArtifacts }) {
  const events = record?.events || []
  const coachingNotes = events.filter((e) => e.phase === "coaching_note")
  const tutorActivity = events.find((e) => e.phase === "tutor_activity")
  if (coachingNotes.length === 0 && !tutorActivity) return null

  return (
    <div className="bg-blue-50/40 border-2 border-blue-200 rounded-lg p-5 mt-6">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="h-4 w-4 text-blue-600" />
        <div>
          <div className="text-sm font-bold text-blue-900">Supporting context — not scored</div>
          <div className="text-xs text-blue-700">
            Coaching notes and tutor activity inform the trainer's judgment but do not
            contribute to the dimension scores.
          </div>
        </div>
      </div>

      {coachingNotes.length > 0 && (
        <div className="mb-3">
          <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">
            Coaching notes
          </div>
          <div className="space-y-2">
            {coachingNotes.map((cn) => (
              <div
                key={cn.note_file || cn.date}
                className="bg-white border border-gray-200 rounded-md p-3"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-gray-900">
                    Call {cn.call} · {cn.date}
                  </span>
                  {cn.score !== undefined && (
                    <span className="text-xs font-mono text-gray-600">score {cn.score}/10</span>
                  )}
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {(resolvedArtifacts?.[cn.note_file] || "").trim() || "(note file missing)"}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {tutorActivity && (
        <div>
          <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">
            Tutor activity
          </div>
          <div className="bg-white border border-gray-200 rounded-md p-3 text-sm">
            <div className="mb-1">
              <span className="text-gray-500">Top topics: </span>
              <span className="text-gray-900">
                {(tutorActivity.top_topics || []).join(", ") || "(none)"}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Flagged gaps: </span>
              <span className="text-gray-900">
                {(tutorActivity.flagged_gaps || []).join(", ") || "(none)"}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function RawArtifacts({ record, resolvedArtifacts }) {
  const events = record?.events || []
  const refs = []
  for (const ev of events) {
    if (ev.transcript_file)
      refs.push({ label: `Simulation call ${ev.call} (${ev.date})`, file: ev.transcript_file })
    if (ev.qa_file) refs.push({ label: `Certification exam (${ev.date})`, file: ev.qa_file })
    if (ev.note_file)
      refs.push({ label: `Coaching note · call ${ev.call} (${ev.date})`, file: ev.note_file })
  }
  const [openFile, setOpenFile] = useState(null)
  if (refs.length === 0) return null

  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-5 mt-6">
      <div className="flex items-center gap-2 mb-3">
        <FileText className="h-4 w-4 text-gray-500" />
        <div className="text-sm font-bold text-gray-900">Raw artifacts</div>
      </div>
      <div className="flex flex-col gap-2">
        {refs.map((ref) => {
          const isOpen = openFile === ref.file
          return (
            <div key={ref.file} className="border border-gray-200 rounded-md">
              <button
                onClick={() => setOpenFile(isOpen ? null : ref.file)}
                className="w-full text-left flex items-center justify-between gap-2 px-3 py-2 hover:bg-gray-50"
              >
                <span className="text-sm font-medium text-gray-800">{ref.label}</span>
                <span className="text-xs font-mono text-gray-400">{ref.file}</span>
              </button>
              {isOpen && (
                <div className="border-t border-gray-200 px-2 py-2 bg-gray-50">
                  <ArtifactCard
                    content={resolvedArtifacts?.[ref.file] || "_(file missing)_"}
                    title=""
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function TrainerDecisionPanel({ sdrId, gapAnalysis, onDecided }) {
  const [decision, setDecision] = useState(null) // "pass" | "fail" | null
  const [comment, setComment] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [submitted, setSubmitted] = useState(null) // {decision, comment}

  const suggested = gapAnalysis?.outputs?.overall_recommendation
  const canSubmit = decision && comment.trim().length > 0 && !submitting

  const handleSubmit = async () => {
    if (!canSubmit) return
    setSubmitting(true)
    setError(null)
    try {
      await decideCertification({ sdr_id: sdrId, decision, comment: comment.trim() })
      setSubmitted({ decision, comment: comment.trim() })
      onDecided?.(decision)
    } catch (err) {
      setError(err.message || "Failed to record decision")
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    const ok = submitted.decision === "pass"
    const Icon = ok ? CheckCircle2 : XCircle
    return (
      <div
        className={`mt-6 rounded-lg border-2 p-5 ${
          ok ? "bg-emerald-50 border-emerald-200" : "bg-gray-50 border-gray-200"
        }`}
      >
        <div className="flex items-start gap-3">
          <Icon className={`h-6 w-6 flex-shrink-0 mt-0.5 ${ok ? "text-emerald-600" : "text-gray-500"}`} />
          <div>
            <div className="text-base font-bold text-gray-900">
              Trainer decision recorded — {submitted.decision.toUpperCase()}
            </div>
            <div className="text-sm text-gray-700 mt-1">{submitted.comment}</div>
            <div className="text-xs text-gray-500 mt-2">
              Logged to decision_log.json. Nothing was written to the knowledge base.
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border-2 border-gray-200 rounded-lg p-5 mt-6">
      <div className="mb-2">
        <div className="text-base font-bold text-gray-900">Trainer final decision</div>
        <div className="text-xs text-gray-500 mt-0.5">
          The AI recommendation is advisory. The trainer makes the final certification call.
          {suggested ? (
            <>
              {" "}Suggested: <strong>{suggested}</strong>.
            </>
          ) : null}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mt-3">
        <button
          onClick={() => setDecision("pass")}
          className={`flex items-center justify-center gap-2 rounded-md h-11 font-semibold text-sm transition-colors ${
            decision === "pass"
              ? "bg-emerald-600 text-white"
              : "bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
          }`}
        >
          <CheckCircle2 className="h-4 w-4" /> Pass
        </button>
        <button
          onClick={() => setDecision("fail")}
          className={`flex items-center justify-center gap-2 rounded-md h-11 font-semibold text-sm transition-colors ${
            decision === "fail"
              ? "bg-red-600 text-white"
              : "bg-red-50 text-red-700 hover:bg-red-100"
          }`}
        >
          <XCircle className="h-4 w-4" /> Fail
        </button>
      </div>

      <div className="mt-4">
        <label className="block text-xs uppercase tracking-wider text-gray-500 font-semibold mb-2">
          Trainer comment (required)
        </label>
        <textarea
          rows={3}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          disabled={submitting}
          placeholder="Explain the decision — context, trajectory, anything the AI gap analysis missed."
          className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500 resize-none"
        />
      </div>

      {error && (
        <div className="mt-3 flex items-start gap-2 text-red-600 text-sm">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={!canSubmit}
        className="mt-4 w-full bg-blue-500 text-white rounded-md h-11 font-semibold hover:bg-blue-600 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {submitting ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" /> Submitting...
          </>
        ) : (
          "Submit decision"
        )}
      </button>
    </div>
  )
}

function buildEvidenceSources(outputs) {
  if (!outputs) return []
  if (Array.isArray(outputs.sources) && outputs.sources.length > 0) return outputs.sources
  if (Array.isArray(outputs.retrieved_docs))
    return outputs.retrieved_docs.map((name) => ({ doc_name: name, passage: "", score: 0, weak: false }))
  return []
}

function DetailView({ sdrId }) {
  const navigate = useNavigate()
  const printRef = useRef(null)
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [analyzeError, setAnalyzeError] = useState(null)

  const fetchDetail = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getCertificationSDR(sdrId)
      setDetail(data)
    } catch (err) {
      setError(err.message || "Failed to load SDR")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDetail()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sdrId])

  const handleAnalyze = async () => {
    setAnalyzing(true)
    setAnalyzeError(null)
    try {
      await analyzeCertification(sdrId)
      await fetchDetail()
    } catch (err) {
      setAnalyzeError(err.message || "Failed to re-run gap analysis")
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading && !detail) {
    return (
      <div className="flex items-center gap-2 text-gray-500 text-sm p-4">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading SDR detail...
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

  const record = detail?.record || {}
  const gap = detail?.gap_analysis
  const outputs = gap?.outputs || null
  const findings = outputs?.dimension_findings || {}
  const overall = outputs?.overall_recommendation || "not_analyzed"

  return (
    <div ref={printRef}>
      <button
        onClick={() => navigate("/certification")}
        className="no-print flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
      >
        <ArrowLeft className="h-4 w-4" /> Back to roster
      </button>

      <div className="bg-white border-2 border-gray-100 rounded-lg p-6 mb-6">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <h1 className="text-2xl font-extrabold text-gray-900">
              {record.name} <span className="text-gray-400 font-mono text-base">{record.sdr_id}</span>
            </h1>
            <div className="text-sm text-gray-500 mt-1">
              {record.cohort} · {record.territory} · {record.experience_level}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <VerdictBadge verdict={overall} />
            <button
              onClick={() => printRegion(printRef.current, `Certification report — ${record.name || sdrId}`)}
              className="no-print flex items-center gap-2 text-xs font-semibold bg-gray-100 text-gray-700 px-3 py-1.5 rounded-md hover:bg-gray-200"
            >
              <Printer className="h-3.5 w-3.5" /> Print / Save PDF
            </button>
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="no-print flex items-center gap-2 text-xs font-semibold bg-white border border-gray-200 text-gray-700 px-3 py-1.5 rounded-md hover:border-blue-400 hover:text-blue-600 disabled:opacity-60"
            >
              {analyzing ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <RefreshCcw className="h-3.5 w-3.5" />
              )}
              Re-run gap analysis
            </button>
          </div>
        </div>
        {outputs?.overall_rationale && (
          <div className="mt-4 bg-gray-50 rounded-md p-4 text-sm text-gray-800 leading-relaxed">
            {outputs.overall_rationale}
          </div>
        )}
        {analyzeError && (
          <div className="mt-3 flex items-start gap-2 text-red-600 text-sm">
            <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <span>{analyzeError}</span>
          </div>
        )}
        {outputs?.confidence !== undefined && outputs.confidence !== null && (
          <div className="mt-3 text-xs text-gray-500">
            AI confidence: <span className="font-semibold">{(outputs.confidence * 100).toFixed(0)}%</span>
            {" · "}AI recommendation is advisory.
          </div>
        )}
      </div>

      {!outputs && (
        <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-5 text-sm text-amber-800">
          No gap analysis cached for this SDR yet. Click "Re-run gap analysis" above to generate one.
        </div>
      )}

      {outputs && (
        <>
          <div className="mb-4 text-base font-bold text-gray-900">Dimension scores</div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {DIMENSION_ORDER.map((dimId) =>
              findings[dimId] ? (
                <DimensionCard key={dimId} dimId={dimId} finding={findings[dimId]} />
              ) : null,
            )}
          </div>

          {outputs.review_reasons?.length > 0 && (
            <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-4 mt-4 text-sm text-amber-800">
              <div className="font-semibold mb-1">Why trainer review is required</div>
              <ul className="list-disc list-inside space-y-1">
                {outputs.review_reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}

          <EvidencePanel
            sources={buildEvidenceSources(outputs)}
            title="Retrieved rubric passages (RAG)"
          />
        </>
      )}

      <JourneyContext record={record} resolvedArtifacts={detail?.resolved_artifacts} />
      <div className="no-print">
        <RawArtifacts record={record} resolvedArtifacts={detail?.resolved_artifacts} />

        <TrainerDecisionPanel
          sdrId={sdrId}
          gapAnalysis={gap}
          onDecided={() => fetchDetail()}
        />
      </div>
    </div>
  )
}

function RosterView() {
  const navigate = useNavigate()
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    getCertificationRoster()
      .then((data) => {
        if (!cancelled) setRows(data || [])
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Failed to load roster")
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-gray-500 text-sm p-4">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading cohort roster...
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
      <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-12 text-center text-gray-500 text-sm">
        No SDR records found under <code className="font-mono">data/sdr_records/</code>.
        Run <code className="font-mono">uv run python skills/score-certification/scripts/seed_synthetic_cohort.py</code>{" "}
        to populate the demo cohort.
      </div>
    )
  }

  return (
    <>
      <div className="mb-3 text-xs text-gray-500">
        Click any row to see the per-dimension gap analysis, evidence quoted from the SDR's
        artifacts, and the trainer decision panel.
      </div>
      <div className="bg-white border-2 border-gray-100 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase tracking-wider text-gray-500">
            <tr>
              <th className="text-left px-5 py-3">SDR</th>
              <th className="text-left px-5 py-3">Cohort</th>
              <th className="text-left px-5 py-3">Territory</th>
              <th className="text-left px-5 py-3">Recommendation</th>
              <th className="text-left px-5 py-3">Weakest dimension</th>
              <th className="px-5 py-3 w-8"></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.sdr_id}
                onClick={() => navigate(`/certification/${r.sdr_id}`)}
                className="border-t border-gray-100 hover:bg-blue-50/60 cursor-pointer transition-colors group"
              >
                <td className="px-5 py-3">
                  <div className="font-semibold text-gray-900 group-hover:text-blue-600">
                    {r.name}
                  </div>
                  <div className="text-xs font-mono text-gray-400">{r.sdr_id}</div>
                </td>
                <td className="px-5 py-3 text-gray-700">{r.cohort}</td>
                <td className="px-5 py-3 text-gray-700">{r.territory}</td>
                <td className="px-5 py-3">
                  <VerdictBadge verdict={r.overall_recommendation} />
                </td>
                <td className="px-5 py-3 text-gray-700 capitalize">
                  {r.weakest_dimension ? r.weakest_dimension.replace(/_/g, " ") : "—"}
                </td>
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

export default function Certification() {
  const { sdrId } = useParams()
  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-gray-900">Certification</h1>
        <p className="text-sm text-gray-600 mt-1">
          SDR cohort gap analyses scored against the certification rubric. The AI flags gaps
          across the five rubric dimensions; the trainer makes the final pass/fail call.
        </p>
      </div>
      {sdrId ? <DetailView sdrId={sdrId} /> : <RosterView />}
    </div>
  )
}
