import { useEffect, useMemo, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import {
  Users,
  Loader2,
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Play,
  ChevronDown,
} from "lucide-react"
import { getHires, getRuns, startRun, getRun, approveStep } from "../lib/api"
import EvidencePanel from "../components/EvidencePanel"
import ApprovalCard from "../components/ApprovalCard"
import ArtifactCard from "../components/ArtifactCard"

const STEP_DEFS = [
  { id: "generate-onboarding-plan", title: "Pre-boarding Plan", type: "LLM Skill" },
  { id: "rank-trail-guides", title: "Mentor Matching", type: "Deterministic Automation" },
  { id: "welcome-new-hire", title: "Welcome Email", type: "Deterministic Automation" },
]

const STATUS_PILL = {
  none: { cls: "bg-gray-100 text-gray-500", label: "Not started" },
  running: { cls: "bg-blue-100 text-blue-700", label: "Running" },
  paused: { cls: "bg-amber-100 text-amber-700", label: "Needs review" },
  complete: { cls: "bg-emerald-100 text-emerald-700", label: "Complete" },
  rejected: { cls: "bg-gray-100 text-gray-500", label: "Rejected" },
  escalated: { cls: "bg-amber-100 text-amber-700", label: "Escalated" },
}

function StatusPill({ status }) {
  const p = STATUS_PILL[status] || STATUS_PILL.none
  return (
    <span className={`${p.cls} rounded-full text-[10px] font-semibold px-2 py-0.5 flex-shrink-0`}>
      {p.label}
    </span>
  )
}

function initials(name) {
  if (!name) return "?"
  const parts = name.trim().split(/\s+/)
  return ((parts[0]?.[0] || "") + (parts[parts.length - 1]?.[0] || "")).toUpperCase()
}

function HirePicker({ hires, latestByHire, hireId, hiresLoading, hiresError, onSelect }) {
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-4 mb-6">
      <label className="block text-xs uppercase tracking-wider text-gray-500 font-semibold mb-2">
        SDR
      </label>
      {hiresError ? (
        <div className="bg-red-50 rounded-md p-3 text-red-700 text-sm flex items-start gap-2">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold">Could not load hires</div>
            <div className="mt-1 text-xs">{hiresError}</div>
          </div>
        </div>
      ) : (
        <div className="relative">
          <select
            value={hireId || ""}
            onChange={(e) => {
              const value = e.target.value
              if (value) onSelect(value)
            }}
            disabled={hiresLoading}
            className="w-full appearance-none bg-gray-100 rounded-md px-4 py-2.5 pr-9 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500 disabled:opacity-60"
          >
            <option value="">
              {hiresLoading ? "Loading hires…" : "Select a hire…"}
            </option>
            {hires.map((h) => {
              const status = latestByHire[h.hire_id]?.status
              const statusSuffix = status ? `  •  ${STATUS_PILL[status]?.label || status}` : ""
              return (
                <option key={h.hire_id} value={h.hire_id}>
                  {h.name} ({h.hire_id}) — {h.territory} · {h.vertical} · {h.experience_level}
                  {statusSuffix}
                </option>
              )
            })}
          </select>
          <ChevronDown className="h-4 w-4 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      )}
    </div>
  )
}

function ConfidenceBar({ confidence }) {
  if (confidence === null || confidence === undefined) return null
  const pct = Math.max(0, Math.min(1, confidence)) * 100
  return (
    <div className="mt-4">
      <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Confidence</div>
      <div className="bg-gray-100 rounded-full h-1.5 overflow-hidden">
        <div className="bg-blue-500 rounded-full h-1.5" style={{ width: `${pct}%` }} />
      </div>
      <div className="mt-1 text-xs text-gray-500 text-right">{pct.toFixed(0)}%</div>
    </div>
  )
}

const HIDDEN_OUTPUT_KEYS = new Set(["retrieved_docs", "sources"])

function OutputsBlock({ outputs }) {
  if (!outputs) return null
  const entries = Object.entries(outputs).filter(([k]) => !HIDDEN_OUTPUT_KEYS.has(k))
  if (entries.length === 0) return null
  return (
    <div className="bg-gray-50 rounded-lg p-4 mt-3">
      <div className="text-xs uppercase tracking-wider text-gray-500 mb-2">Outputs</div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2">
        {entries.map(([k, v]) => (
          <div key={k} className="flex items-baseline gap-2">
            <span className="text-gray-500 text-xs">{k}</span>
            <span className="text-gray-900 text-sm font-medium truncate">
              {Array.isArray(v) ? v.join(", ") : String(v)}
            </span>
          </div>
        ))}
      </div>
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

function PendingCard({ def }) {
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-5 opacity-60">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-bold text-gray-400">{def.title}</div>
          <div className="text-xs text-gray-300">{def.type}</div>
        </div>
        <div className="text-xs text-gray-400">Waiting...</div>
      </div>
    </div>
  )
}

function CompletedCard({ def, step }) {
  const envelope = step.envelope || {}
  const reviewRequired = envelope.review_required === true
  const isError = envelope.status === "error"
  const borderCls = isError
    ? "border-red-400"
    : reviewRequired
      ? "border-amber-400"
      : "border-emerald-400"
  const badgeCls = isError
    ? "bg-red-100 text-red-700"
    : reviewRequired
      ? "bg-amber-100 text-amber-700"
      : "bg-emerald-100 text-emerald-700"
  const badgeLabel = isError ? "Error" : reviewRequired ? "Review Required" : "Complete"

  return (
    <div className={`bg-white border-2 ${borderCls} rounded-lg p-5`}>
      <div className="flex items-center gap-3 flex-wrap">
        <div className="font-bold text-gray-900">{def.title}</div>
        <span className={`${badgeCls} text-xs font-semibold rounded-full px-2 py-0.5`}>
          {badgeLabel}
        </span>
        <span className="bg-gray-100 text-gray-600 text-xs rounded-full px-2 py-0.5">
          {def.type}
        </span>
      </div>
      <ConfidenceBar confidence={envelope.confidence} />
      <OutputsBlock outputs={envelope.outputs} />
      <ArtifactCard content={step.artifact_content} />
      <EvidencePanel sources={buildEvidenceSources(envelope.outputs)} />
      {isError && envelope.error?.message && (
        <div className="bg-red-50 rounded-md p-4 mt-3 text-red-700 text-sm flex items-start gap-2">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <span>{envelope.error.message}</span>
        </div>
      )}
    </div>
  )
}

function pausedStepArtifact(run) {
  const steps = run?.completed_steps || []
  if (steps.length === 0) return ""
  return steps[steps.length - 1].artifact_content || ""
}

function ProfileField({ label, value }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">{label}</div>
      <div className="text-gray-900 font-medium text-sm">{value}</div>
    </div>
  )
}

function HireProfileEmptyRun({ hire, onStart, starting, startError }) {
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-12 h-12 bg-blue-100 text-blue-700 rounded-lg flex items-center justify-center text-base font-bold">
          {initials(hire.name)}
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">{hire.name}</h2>
          <div className="text-xs text-gray-500">{hire.hire_id}</div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <ProfileField label="Territory" value={hire.territory} />
        <ProfileField label="Vertical" value={hire.vertical} />
        <ProfileField label="Experience" value={hire.experience_level} />
        <ProfileField label="Prior role" value={hire.prior_role} />
      </div>
      {startError && (
        <div className="mt-6 bg-red-50 rounded-md p-4 text-red-700 text-sm flex items-start gap-2">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <span>{startError}</span>
        </div>
      )}
      <button
        onClick={onStart}
        disabled={starting}
        className="mt-6 w-full bg-blue-500 text-white rounded-md h-12 font-semibold hover:bg-blue-600 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {starting ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            Starting onboarding workflow...
          </>
        ) : (
          <>
            <Play className="h-4 w-4" />
            Start onboarding workflow
          </>
        )}
      </button>
    </div>
  )
}

function CompleteBanner({ onAnother }) {
  return (
    <div className="bg-emerald-50 border-2 border-emerald-500 rounded-lg p-6 mt-4">
      <div className="flex items-start gap-3">
        <CheckCircle className="h-6 w-6 text-emerald-500 flex-shrink-0 mt-0.5" />
        <div>
          <div className="text-lg font-bold text-emerald-700">Workflow Complete</div>
          <div className="mt-1 text-emerald-600 text-sm">All 3 steps finished successfully.</div>
        </div>
      </div>
      <button
        onClick={onAnother}
        className="mt-5 bg-blue-500 text-white rounded-md px-5 h-10 text-sm font-semibold hover:bg-blue-600 transition-all"
      >
        Run again
      </button>
    </div>
  )
}

function TerminalBanner({ status, onAnother }) {
  const isRejected = status === "rejected"
  const Icon = isRejected ? XCircle : AlertTriangle
  const iconCls = isRejected ? "text-gray-500" : "text-amber-500"
  const title = isRejected ? "Workflow Rejected" : "Workflow Escalated"
  const subtitle = isRejected
    ? "The run was stopped. The decision is logged in the review history."
    : "Flagged for senior review. The note is logged."
  return (
    <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 mt-4">
      <div className="flex items-start gap-3">
        <Icon className={`h-6 w-6 ${iconCls} flex-shrink-0 mt-0.5`} />
        <div>
          <div className="text-lg font-bold text-gray-900">{title}</div>
          <div className="mt-1 text-gray-600 text-sm">{subtitle}</div>
        </div>
      </div>
      <button
        onClick={onAnother}
        className="mt-5 bg-blue-500 text-white rounded-md px-5 h-10 text-sm font-semibold hover:bg-blue-600 transition-all"
      >
        Run again
      </button>
    </div>
  )
}

function stepTabState(step) {
  if (!step) return { kind: "pending", label: "Waiting", cls: "bg-gray-100 text-gray-500" }
  const env = step.envelope || {}
  if (env.status === "error") return { kind: "error", label: "Error", cls: "bg-red-100 text-red-700" }
  if (env.review_required === true)
    return { kind: "review", label: "Needs review", cls: "bg-amber-100 text-amber-700" }
  return { kind: "complete", label: "Complete", cls: "bg-emerald-100 text-emerald-700" }
}

function pickInitialStepTab(stepByName) {
  // priority 1: a step that's paused for review (the thing demanding attention)
  for (const def of STEP_DEFS) {
    const env = stepByName[def.id]?.envelope
    if (env?.review_required === true) return def.id
  }
  // priority 2: latest completed step
  for (let i = STEP_DEFS.length - 1; i >= 0; i--) {
    if (stepByName[STEP_DEFS[i].id]) return STEP_DEFS[i].id
  }
  return STEP_DEFS[0].id
}

function StepTabs({ stepByName, active, onSelect }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-4">
      {STEP_DEFS.map((def, idx) => {
        const step = stepByName[def.id]
        const s = stepTabState(step)
        const isActive = active === def.id
        return (
          <button
            key={def.id}
            onClick={() => onSelect(def.id)}
            className={`text-left px-3 py-2 rounded-lg border-2 transition-colors ${
              isActive
                ? "bg-blue-50 border-blue-500"
                : "bg-white border-gray-100 hover:border-gray-300"
            }`}
          >
            <div className="text-[10px] uppercase tracking-wider text-gray-400 mb-0.5">
              Step {idx + 1}
            </div>
            <div className="font-semibold text-gray-900 text-sm leading-tight truncate">
              {def.title}
            </div>
            <div className="mt-1.5 flex items-center gap-1.5 flex-wrap">
              <span className={`${s.cls} rounded-full text-[10px] font-semibold px-2 py-0.5`}>
                {s.label}
              </span>
              <span className="text-[10px] text-gray-400">{def.type}</span>
            </div>
          </button>
        )
      })}
    </div>
  )
}

function RunView({ run, onApprove, onReject, onEscalate, reviewLoading, onAnother }) {
  const stepByName = (run?.completed_steps || []).reduce((acc, s) => {
    acc[s.step_name] = s
    return acc
  }, {})
  const [activeStepId, setActiveStepId] = useState(() => pickInitialStepTab(stepByName))

  // Re-pick the active tab when the run progresses so the manager always lands
  // on the step that needs attention (paused → latest completed → first).
  useEffect(() => {
    setActiveStepId(pickInitialStepTab(stepByName))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run.status, run.pending_step, run.completed_steps?.length])

  const activeDef = STEP_DEFS.find((d) => d.id === activeStepId) || STEP_DEFS[0]
  const activeStep = stepByName[activeDef.id]

  return (
    <div>
      <div className="flex items-center gap-3 flex-wrap mb-4">
        <span className="font-mono text-xs text-gray-500">{run.workflow_run_id}</span>
        <StatusPill status={run.status} />
      </div>

      <StepTabs stepByName={stepByName} active={activeStepId} onSelect={setActiveStepId} />

      <div>
        {activeStep
          ? <CompletedCard def={activeDef} step={activeStep} />
          : <PendingCard def={activeDef} />}
      </div>

      {run.status === "paused" && (
        <ApprovalCard
          status="idle"
          content={pausedStepArtifact(run)}
          onApprove={onApprove}
          onReject={onReject}
          onEscalate={onEscalate}
          allowEscalate={true}
          busy={reviewLoading}
          footerNote="Approve resumes the workflow. Edit overwrites the paused step's artifact first. Reject ends the run. Escalate flags it for senior review."
        />
      )}
      {run.status === "complete" && <CompleteBanner onAnother={onAnother} />}
      {(run.status === "rejected" || run.status === "escalated") && (
        <TerminalBanner status={run.status} onAnother={onAnother} />
      )}
    </div>
  )
}

export default function Preboarding() {
  const { hireId } = useParams()
  const navigate = useNavigate()

  const [hires, setHires] = useState([])
  const [runs, setRuns] = useState([])
  const [hiresLoading, setHiresLoading] = useState(true)
  const [hiresError, setHiresError] = useState(null)

  const [run, setRun] = useState(null)
  const [runLoading, setRunLoading] = useState(false)
  const [runError, setRunError] = useState(null)
  const [starting, setStarting] = useState(false)
  const [startError, setStartError] = useState(null)
  const [reviewLoading, setReviewLoading] = useState(false)

  useEffect(() => {
    let cancelled = false
    setHiresLoading(true)
    setHiresError(null)
    Promise.all([getHires(), getRuns()])
      .then(([hireList, runList]) => {
        if (cancelled) return
        setHires(hireList || [])
        setRuns(runList || [])
      })
      .catch((err) => {
        if (!cancelled) setHiresError(err.message || "Failed to load")
      })
      .finally(() => {
        if (!cancelled) setHiresLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const latestByHire = useMemo(() => {
    const m = {}
    for (const r of runs) {
      if (!m[r.hire_id]) m[r.hire_id] = r
    }
    return m
  }, [runs])

  const selectedHire = useMemo(
    () => hires.find((h) => h.hire_id === hireId) || null,
    [hires, hireId],
  )

  useEffect(() => {
    let cancelled = false
    setRun(null)
    setRunError(null)
    setStartError(null)
    if (!hireId) return
    const latest = latestByHire[hireId]
    if (!latest) return
    setRunLoading(true)
    getRun(latest.workflow_run_id)
      .then((data) => {
        if (!cancelled) setRun(data)
      })
      .catch((err) => {
        if (!cancelled) setRunError(err.message || "Failed to load run")
      })
      .finally(() => {
        if (!cancelled) setRunLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [hireId, latestByHire])

  useEffect(() => {
    if (run?.status !== "running") return
    const id = setInterval(async () => {
      try {
        const data = await getRun(run.workflow_run_id)
        setRun(data)
      } catch {
        // ignore transient polling errors
      }
    }, 2000)
    return () => clearInterval(id)
  }, [run?.status, run?.workflow_run_id])

  const refreshSidebar = () => {
    getRuns()
      .then((rs) => setRuns(rs || []))
      .catch(() => {})
  }

  const handleStart = async () => {
    if (!selectedHire) return
    setStarting(true)
    setStartError(null)
    try {
      const newRun = await startRun(selectedHire.hire_id)
      if (!newRun?.workflow_run_id) throw new Error("Server did not return a workflow_run_id")
      setRun(newRun)
      refreshSidebar()
    } catch (err) {
      setStartError(err.message || "Failed to start workflow")
    } finally {
      setStarting(false)
    }
  }

  const submitDecision = async (decision, reason = "", editedContent = null) => {
    if (!run) return
    setReviewLoading(true)
    setRunError(null)
    try {
      const updated = await approveStep(run.workflow_run_id, decision, reason, editedContent)
      setRun(updated)
      refreshSidebar()
    } catch (err) {
      setRunError(err.message || "Failed to submit decision")
    } finally {
      setReviewLoading(false)
    }
  }

  const handleApprove = (finalContent, opts) =>
    submitDecision("approve", opts.edited ? "Approved with edits" : "", opts.edited ? finalContent : null)
  const handleReject = (reason) => submitDecision("reject", reason || "")
  const handleEscalate = (reason) => submitDecision("escalate", reason || "")

  const handleAnother = () => {
    // Drop into the start screen for this hire without changing URL.
    // The next click on "Start" creates a fresh workflow_run_id.
    setRun(null)
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-gray-900">Pre-boarding</h1>
        <p className="text-sm text-gray-600 mt-1">
          Pick a hire to start their onboarding workflow or view a run in progress.
        </p>
      </div>

      <HirePicker
        hires={hires}
        latestByHire={latestByHire}
        hireId={hireId}
        hiresLoading={hiresLoading}
        hiresError={hiresError}
        onSelect={(id) => navigate(`/preboarding/${id}`)}
      />

      <div>
        <main>
          {!selectedHire && (
            <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-12 flex flex-col items-center justify-center text-center min-h-[24rem]">
              <Users className="h-12 w-12 text-gray-300 mb-3" />
              <div className="text-gray-500 text-sm">
                Select a hire from the dropdown to view their onboarding.
              </div>
            </div>
          )}

          {selectedHire && (
            <>
              {runLoading && !run && (
                <div className="flex items-center gap-2 text-gray-500 text-sm p-4">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading run...
                </div>
              )}

              {!runLoading && !run && (
                <HireProfileEmptyRun
                  hire={selectedHire}
                  onStart={handleStart}
                  starting={starting}
                  startError={startError}
                />
              )}

              {run && (
                <>
                  {runError && (
                    <div className="bg-red-50 rounded-md p-4 text-red-700 text-sm flex items-start gap-2 mb-4">
                      <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                      <span>{runError}</span>
                    </div>
                  )}
                  <RunView
                    run={run}
                    onApprove={handleApprove}
                    onReject={handleReject}
                    onEscalate={handleEscalate}
                    reviewLoading={reviewLoading}
                    onAnother={handleAnother}
                  />
                </>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  )
}
