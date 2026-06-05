import { useEffect, useState } from "react"
import {
  Upload,
  Loader2,
  AlertCircle,
  AlertTriangle,
  Sparkles,
  Check,
  ArrowRight,
  MessageCircle,
} from "lucide-react"
import { getHires, scoreCoaching, approveCoaching } from "../lib/api"
import ApprovalBar from "../components/ApprovalBar"
import EvidencePanel from "../components/EvidencePanel"
import ScoreBadge from "../components/ScoreBadge"
import ScoreBreakdown from "../components/ScoreBreakdown"

const SAMPLE_TRANSCRIPT_PRIYA = `SDR: Hi Dr. Hassan, this is Priya from Salesforce. I'm reaching out because I saw your team at Meridian Health rolled out a new patient-portal initiative last quarter — congrats on that launch. The reason for my call is that healthcare orgs running portal rollouts often hit case-volume spikes in the first 90 days, and our Service Cloud Health workflow helps triage that surge. Do you have two minutes?

Prospect: Hmm. Yeah, we're definitely seeing more inbound, but honestly we already have a ticketing tool. And I'm not sure we have budget for another system right now.

SDR: Totally fair. Quick question — when you say more inbound, are most of those tickets routed to clinical staff or back-office? The reason I ask is that the budget conversation often shifts once teams see how much clinician time gets pulled into ticket triage. I'm not trying to sell you anything today — would it be useful to walk through how three other patient-portal launches handled that, just so you have a benchmark?

Prospect: Okay, yeah, that part is genuinely a problem. Send me a 20-minute slot next week — Tuesday or Thursday afternoon. Loop in my ops lead too.`

const SAMPLE_TRANSCRIPT_MARCUS = `SDR: Hi Director of Ops at NorthStar Capital, thanks for the few minutes. I'm calling because three other fintech ops leaders we work with were spending 18-22 hours a week on manual pipeline hygiene before they moved to Sales Cloud. Does that pattern sound familiar at your scale, or is your team in a different place?

Prospect: Honestly, my reps spend more time updating CRM than selling. It's a problem.

SDR: That's the exact pain we hear. Before I assume Sales Cloud is right, can you walk me through where the data actually lives today — is it in Salesforce, in spreadsheets, or somewhere in between?

Prospect: Mostly in Salesforce, but the reps don't trust the forecast numbers, so we rebuild them in Excel weekly.

SDR: Got it — so the friction isn't capture, it's confidence in what's in the system. A few of your peers have used Sales Cloud's revenue intelligence layer to close that trust gap; what would actually have to be true for your forecast to be the one number everyone runs the business on?

Prospect: Clean stage definitions, owner accountability, and something that flags stalled deals before my reviews on Friday.

SDR: All three are addressable inside Sales Cloud. The piece I'd want to dig into is who else weighs in when you're changing the forecast rhythm — is that you, or do you have a finance partner and a RevOps lead in that decision?

Prospect: Finance VP and my RevOps lead. We'd need both to sign off.

SDR: Helpful — I'd want to bring those two in before we propose anything specific. Would Thursday at 11 work for a 30-minute scoping call with you and the RevOps lead?

Prospect: Yes, Thursday at 11 works.`

// Selectable sample calls — each preloads the transcript, the SDR, context and outcome.
const SAMPLE_CALLS = [
  {
    id: "priya",
    label: "Priya → Dr. Hassan (Healthcare)",
    hire_id: "HIRE-001",
    context: "Cold call — Meridian Health patient-portal follow-up",
    outcome: "meeting_booked",
    text: SAMPLE_TRANSCRIPT_PRIYA,
  },
  {
    id: "marcus",
    label: "Marcus → Director of Ops (FinTech)",
    hire_id: "HIRE-002",
    context: "Cold call — NorthStar Capital pipeline hygiene & forecast trust",
    outcome: "meeting_booked",
    text: SAMPLE_TRANSCRIPT_MARCUS,
  },
]

const OUTCOMES = [
  { value: "meeting_booked", label: "Meeting booked" },
  { value: "follow_up_scheduled", label: "Follow-up scheduled" },
  { value: "no_meeting", label: "No meeting" },
  { value: "unknown", label: "Unknown" },
]

const LIST_STYLES = {
  emerald: { bg: "bg-emerald-50", border: "border-emerald-200", icon: Check, iconCls: "text-emerald-600" },
  amber: { bg: "bg-amber-50", border: "border-amber-200", icon: ArrowRight, iconCls: "text-amber-600" },
  blue: { bg: "bg-blue-50", border: "border-blue-200", icon: MessageCircle, iconCls: "text-blue-600" },
}

function ListBox({ title, items, color }) {
  const s = LIST_STYLES[color] || LIST_STYLES.blue
  const Icon = s.icon
  if (!items?.length) return null
  return (
    <div className={`${s.bg} border-2 ${s.border} rounded-lg p-4`}>
      <div className="text-xs uppercase tracking-wider font-semibold mb-2 text-gray-700">
        {title}
      </div>
      <ul className="space-y-2 text-sm text-gray-800">
        {items.map((it, i) => (
          <li key={i} className="flex items-start gap-2">
            <Icon className={`h-4 w-4 ${s.iconCls} flex-shrink-0 mt-0.5`} />
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

const RESULT_TABS = [
  { id: "score", label: "Score" },
  { id: "breakdown", label: "Breakdown" },
  { id: "feedback", label: "Worked / Improve" },
  { id: "language", label: "Language alts" },
  { id: "sources", label: "Sources" },
]

function ResultTabs({ active, onSelect, reviewRequired }) {
  return (
    <div className="flex items-center gap-1 mb-2 flex-wrap">
      {RESULT_TABS.map((tab) => {
        const isActive = active === tab.id
        return (
          <button
            key={tab.id}
            onClick={() => onSelect(tab.id)}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-colors flex items-center gap-1.5 ${
              isActive
                ? "text-blue-500 bg-blue-50"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            {tab.label}
            {tab.id === "score" && reviewRequired && (
              <span className="inline-block w-1.5 h-1.5 bg-amber-500 rounded-full" />
            )}
          </button>
        )
      })}
    </div>
  )
}

function ReviewReasons({ reasons }) {
  if (!reasons?.length) return null
  return (
    <div className="bg-amber-50 border-2 border-amber-500 rounded-lg p-4">
      <div className="flex items-center gap-2 text-amber-800 font-semibold text-sm mb-2">
        <AlertTriangle className="h-4 w-4" />
        Manager review required
      </div>
      <ul className="space-y-1 text-xs text-amber-900">
        {reasons.map((r, i) => (
          <li key={i}>• {r}</li>
        ))}
      </ul>
    </div>
  )
}

export default function CoachingNotes() {
  const [hires, setHires] = useState([])
  const [hiresLoading, setHiresLoading] = useState(true)
  const [hireId, setHireId] = useState("")
  const [transcriptText, setTranscriptText] = useState("")
  const [callContext, setCallContext] = useState("")
  const [outcome, setOutcome] = useState("meeting_booked")

  const [generating, setGenerating] = useState(false)
  const [session, setSession] = useState(null)
  const [error, setError] = useState(null)
  const [dragOver, setDragOver] = useState(false)

  const [decisionStatus, setDecisionStatus] = useState("idle")
  const [decisionBusy, setDecisionBusy] = useState(false)
  const [decisionDetail, setDecisionDetail] = useState(null)
  const [activeTab, setActiveTab] = useState("score")

  useEffect(() => {
    getHires()
      .then((data) => setHires(data || []))
      .catch(() => {})
      .finally(() => setHiresLoading(false))
  }, [])

  const handleFile = (file) => {
    if (!file) return
    const reader = new FileReader()
    reader.onload = (e) => setTranscriptText(String(e.target?.result || ""))
    reader.readAsText(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer?.files?.[0]
    handleFile(file)
  }

  const resetDecision = () => {
    setDecisionStatus("idle")
    setDecisionDetail(null)
  }

  const handleGenerate = async () => {
    if (!hireId || !transcriptText.trim() || generating) return
    setGenerating(true)
    setError(null)
    setSession(null)
    resetDecision()
    setActiveTab("score")
    try {
      const s = await scoreCoaching({
        hire_id: hireId,
        transcript_text: transcriptText,
        call_context: callContext,
        outcome,
      })
      setSession(s)
      if (s?.envelope?.status === "error") {
        setError(s.envelope.error?.message || "Scoring failed")
      }
    } catch (err) {
      setError(err.message || "Failed to score transcript")
    } finally {
      setGenerating(false)
    }
  }

  const handleApprove = async (finalContent, opts) => {
    if (!session) return
    setDecisionBusy(true)
    try {
      const updated = await approveCoaching({
        session_id: session.session_id,
        decision: "approve",
        note: opts.edited ? "Approved with edits" : "",
        edited_content: opts.edited ? finalContent : null,
      })
      setSession(updated)
      setDecisionStatus(opts.edited ? "edited" : "approved")
      setDecisionDetail(
        opts.edited
          ? "Edited coaching note saved and sent to the SDR."
          : "Coaching note approved and sent to the SDR.",
      )
    } catch (err) {
      setError(err.message || "Failed to approve")
    } finally {
      setDecisionBusy(false)
    }
  }

  const handleReject = async (reason) => {
    if (!session) return
    setDecisionBusy(true)
    try {
      const updated = await approveCoaching({
        session_id: session.session_id,
        decision: "reject",
        note: reason || "",
      })
      setSession(updated)
      setDecisionStatus("rejected")
      setDecisionDetail("Coaching note rejected. The SDR will not see this version.")
    } catch (err) {
      setError(err.message || "Failed to reject")
    } finally {
      setDecisionBusy(false)
    }
  }

  const envelope = session?.envelope
  const outputs = envelope?.outputs
  const reviewRequired = envelope?.review_required === true
  const isError = envelope?.status === "error"
  const showApproval = session && !isError

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Coaching Notes</h1>
        <p className="text-gray-500 text-sm">
          Upload a recorded sales call. The agent scores it against the Coaching
          Rubric v3.1 and asks for your review when the score is uncertain or
          below bar.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* LEFT — upload + inputs */}
        <div className="flex flex-col gap-4">
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-500 font-semibold mb-2">
              SDR
            </label>
            <select
              value={hireId}
              onChange={(e) => setHireId(e.target.value)}
              disabled={hiresLoading || generating}
              className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500 disabled:opacity-60"
            >
              <option value="">
                {hiresLoading ? "Loading hires…" : "Select a hire…"}
              </option>
              {hires.map((h) => (
                <option key={h.hire_id} value={h.hire_id}>
                  {h.name} ({h.hire_id}) — {h.territory} · {h.vertical} · {h.experience_level}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs uppercase tracking-wider text-gray-500 font-semibold mb-2">
                Call context
              </label>
              <input
                type="text"
                value={callContext}
                onChange={(e) => setCallContext(e.target.value)}
                disabled={generating}
                placeholder="e.g. Cold call to Meridian Health"
                className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs uppercase tracking-wider text-gray-500 font-semibold mb-2">
                Outcome
              </label>
              <select
                value={outcome}
                onChange={(e) => setOutcome(e.target.value)}
                disabled={generating}
                className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500"
              >
                {OUTCOMES.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-500 font-semibold mb-2">
              Transcript
            </label>
            <div
              onDragOver={(e) => {
                e.preventDefault()
                setDragOver(true)
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-3 transition-colors ${
                dragOver
                  ? "border-blue-400 bg-blue-50"
                  : "border-gray-200 bg-gray-50"
              }`}
            >
              <textarea
                rows={8}
                value={transcriptText}
                onChange={(e) => setTranscriptText(e.target.value)}
                disabled={generating}
                placeholder='Paste the transcript here, drag-drop a .txt or .json file, or use the sample. Lines like "SDR: …" and "Prospect: …" are parsed automatically.'
                className="w-full bg-white rounded-md px-3 py-2 text-sm font-mono leading-relaxed focus:outline-none resize-none"
              />
              <div className="flex items-center justify-between gap-2 mt-2 px-1 flex-wrap">
                <span className="text-xs text-gray-400 flex items-center gap-1">
                  <Upload className="h-3 w-3" />
                  Paste text, or drop a .txt / .json transcript
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">Sample call:</span>
                  {SAMPLE_CALLS.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => {
                        setTranscriptText(c.text)
                        setHireId(c.hire_id)
                        setCallContext(c.context)
                        setOutcome(c.outcome)
                      }}
                      disabled={generating}
                      className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors disabled:opacity-40"
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating || !hireId || !transcriptText.trim()}
            className="w-full bg-blue-500 text-white font-semibold py-3 rounded-md hover:bg-blue-600 hover:scale-[1.01] transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating coaching note…
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Generate coaching note
              </>
            )}
          </button>

          {error && (
            <div className="bg-red-50 rounded-md p-3 flex items-start gap-2 text-red-700 text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* RIGHT — output */}
        <div className="flex flex-col gap-4">
          {!session && !generating && (
            <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-6 min-h-[300px] flex items-center justify-center text-gray-400 text-sm text-center">
              Pick an SDR, paste a call transcript, and click Generate to see
              the coaching note here.
            </div>
          )}

          {generating && (
            <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-6 min-h-[300px] flex flex-col items-center justify-center text-gray-400 text-sm gap-3">
              <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
              Generating coaching note…
            </div>
          )}

          {isError && (
            <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 text-red-700 text-sm flex items-start gap-2">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-semibold">Scoring failed</div>
                <div className="mt-1 text-xs">{envelope?.error?.message}</div>
              </div>
            </div>
          )}

          {outputs && !isError && (
            <>
              <ApprovalBar
                status={decisionStatus}
                content={session.artifact_content || ""}
                onApprove={handleApprove}
                onReject={handleReject}
                busy={decisionBusy}
              />
              <ResultTabs
                active={activeTab}
                onSelect={setActiveTab}
                reviewRequired={reviewRequired}
              />
              {activeTab === "score" && (
                <>
                  <ScoreBadge weighted_total={outputs.weighted_total} />
                  {reviewRequired && <ReviewReasons reasons={outputs.review_reasons} />}
                </>
              )}
              {activeTab === "breakdown" && (
                <ScoreBreakdown dimension_scores={outputs.dimension_scores} />
              )}
              {activeTab === "feedback" && (
                <>
                  <ListBox title="What worked" items={outputs.what_worked} color="emerald" />
                  <ListBox title="What to improve" items={outputs.what_to_improve} color="amber" />
                </>
              )}
              {activeTab === "language" && (
                <ListBox
                  title="Language alternatives"
                  items={outputs.language_alternatives}
                  color="blue"
                />
              )}
              {activeTab === "sources" && (
                <EvidencePanel sources={outputs.sources} title="Rubric sources used" />
              )}
            </>
          )}
        </div>
      </div>

      {showApproval && decisionDetail && (
        <div
          className={`mt-3 rounded-md p-3 text-sm ${
            decisionStatus === "rejected"
              ? "bg-gray-100 text-gray-700"
              : decisionStatus === "edited"
                ? "bg-amber-50 text-amber-800"
                : "bg-emerald-50 text-emerald-700"
          }`}
        >
          {decisionDetail}
        </div>
      )}
    </div>
  )
}
