import { useState } from "react"
import { AlertTriangle, AlertCircle } from "lucide-react"
import EvidencePanel from "../components/EvidencePanel"
import ApprovalBar from "../components/ApprovalBar"
import InlineCitations from "../components/InlineCitations"
import { askTutor, approveTutorAnswer, rejectTutorAnswer } from "../lib/api"

// KB-grounded chips. Each maps to a file in rag/knowledge_base/ so the Tutor
// has authoritative content to cite. After Phase D's scraper runs, additional
// questions answerable from scraped/ (MEDDIC, SPIN, BANT, etc.) also work.
const SUGGESTED_QUESTIONS = [
  "How do I handle the 'send me an email' objection?",
  "When does my quota ramp to 100%?",
  "What can I say about competitors on a call?",
  "What's the cold-call quality rubric we use?",
  "What tools do I get access to in my first week?",
  "What's the escalation path for a Day-1 IT issue?",
]

export default function Tutor() {
  const [question, setQuestion] = useState("")
  const [asking, setAsking] = useState(false)
  const [response, setResponse] = useState(null)
  const [error, setError] = useState(null)

  const [decisionStatus, setDecisionStatus] = useState("idle")
  const [decisionBusy, setDecisionBusy] = useState(false)
  const [decisionDetail, setDecisionDetail] = useState(null)
  const [expandedSource, setExpandedSource] = useState(null)

  const resetDecision = () => {
    setDecisionStatus("idle")
    setDecisionDetail(null)
    setExpandedSource(null)
  }

  const handleAsk = async () => {
    if (!question.trim() || asking) return
    setAsking(true)
    setError(null)
    setResponse(null)
    resetDecision()
    try {
      const r = await askTutor(question.trim())
      setResponse(r)
    } catch (err) {
      setError(err.message || "Failed to reach the tutor backend")
    } finally {
      setAsking(false)
    }
  }

  const handleChip = (chip) => {
    setQuestion(chip)
    setResponse(null)
    setError(null)
    resetDecision()
  }

  const handleApprove = async (finalContent, opts) => {
    if (!response?.outputs) return
    setDecisionBusy(true)
    try {
      const r = await approveTutorAnswer(
        response.outputs.question,
        response.outputs.answer,
        opts.edited ? finalContent : null,
      )
      setDecisionStatus(opts.edited ? "edited" : "approved")
      setDecisionDetail(
        `${opts.edited ? "Edited answer" : "Answer"} written as ${r.qa_id} (KB now ${r.kb_chunk_count} chunks)`,
      )
    } catch (err) {
      setError(err.message || "Failed to approve")
    } finally {
      setDecisionBusy(false)
    }
  }

  const handleReject = async (reason) => {
    if (!response?.outputs) return
    setDecisionBusy(true)
    try {
      const r = await rejectTutorAnswer(
        response.outputs.question,
        response.outputs.answer,
        reason || "Rejected from tutor UI",
      )
      setDecisionStatus("rejected")
      setDecisionDetail(
        `Logged to gap tracker (entry ${r.gap_index}). Nothing written to the KB.`,
      )
    } catch (err) {
      setError(err.message || "Failed to reject")
    } finally {
      setDecisionBusy(false)
    }
  }

  const outputs = response?.outputs
  const flagged = outputs?.flagged === true
  const confidencePct = Math.round((response?.confidence || 0) * 100)

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">AI Tutor</h1>
        <p className="text-gray-500 text-sm">
          Ask any question about Salesforce SDR processes — answers are cited from the knowledge base.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* LEFT — question + suggested chips */}
        <div>
          <textarea
            rows={5}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleAsk()
            }}
            placeholder="e.g. How do I handle the 'send me an email' objection?"
            className="w-full bg-gray-100 rounded-lg p-4 text-sm text-gray-900 placeholder-gray-400 focus:outline-none resize-none"
          />

          <div className="mt-3 mb-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Suggested
            </p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleChip(q)}
                  className="text-xs font-medium bg-white border border-gray-200 text-gray-600 px-3 py-1.5 rounded-full hover:border-blue-400 hover:text-blue-600 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleAsk}
              disabled={asking || !question.trim()}
              className="bg-blue-500 text-white font-semibold px-6 py-2.5 rounded-md hover:bg-blue-600 hover:scale-105 transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {asking ? "Thinking…" : "Ask"}
            </button>
            <span className="text-xs text-gray-400">⌘ + Enter</span>
          </div>

          {error && (
            <div className="mt-3 flex items-start gap-2 text-red-600 text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* RIGHT — answer */}
        <div>
          {outputs ? (
            <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
              <ApprovalBar
                status={decisionStatus}
                content={outputs.answer}
                onApprove={handleApprove}
                onReject={handleReject}
                busy={decisionBusy}
              />

              {flagged && (
                <div className="bg-amber-50 border-2 border-amber-500 rounded-lg p-3 mb-4 text-amber-800 text-xs font-medium flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                  Low confidence — this answer may not be fully grounded in the KB. Review carefully before approving.
                </div>
              )}

              <div className="text-[15px] text-gray-800 leading-[1.65] space-y-3.5 mb-5">
                {outputs.answer.split(/\n\n+/).map((para, i) => (
                  <p key={i} className="whitespace-pre-wrap">
                    <InlineCitations text={para} onCitationClick={setExpandedSource} />
                  </p>
                ))}
              </div>

              {outputs.next_step && (
                <div className="border-l-4 border-blue-500 bg-blue-50/50 rounded-r-md p-4 mb-5">
                  <div className="text-xs uppercase tracking-wider text-blue-700 font-bold mb-1.5">
                    Next step
                  </div>
                  <div className="text-gray-800 text-[14px] leading-relaxed">{outputs.next_step}</div>
                </div>
              )}

              <div className="mb-1">
                <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                  <span>Confidence</span>
                  <span className="font-semibold">{confidencePct}%</span>
                </div>
                <div className="bg-gray-100 rounded-full h-1.5">
                  <div
                    className="bg-blue-500 h-1.5 rounded-full transition-all duration-700"
                    style={{ width: `${confidencePct}%` }}
                  />
                </div>
              </div>

              <EvidencePanel
                sources={outputs.sources}
                title="Sources used"
                expandedIndex={expandedSource}
                onExpandedChange={setExpandedSource}
              />
            </div>
          ) : (
            <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-6 min-h-[220px] flex items-center justify-center text-gray-400 text-sm">
              {asking ? "Retrieving from knowledge base…" : "Your answer will appear here"}
            </div>
          )}
        </div>
      </div>

      {outputs && decisionDetail && (
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
