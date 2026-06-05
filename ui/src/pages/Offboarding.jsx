import { useEffect, useMemo, useState } from "react"
import {
  ArrowLeft,
  ArrowRight,
  Loader2,
  Play,
  AlertCircle,
  CheckCircle,
  Sparkles,
  RefreshCw,
} from "lucide-react"
import { OFFBOARDING_QUESTIONS } from "../lib/offboardingQuestions"
import { synthesizeOffboarding, getHires, listOffboardingSessions } from "../lib/api"
import { formatDate } from "../lib/format"

function ProgressBar({ current, total }) {
  return (
    <div className="flex items-center gap-1.5">
      {Array.from({ length: total }).map((_, i) => (
        <div
          key={i}
          className={`flex-1 h-1.5 rounded-full transition-colors ${
            i < current ? "bg-blue-500" : i === current ? "bg-blue-300" : "bg-gray-200"
          }`}
        />
      ))}
    </div>
  )
}

function emptyAnswers() {
  return OFFBOARDING_QUESTIONS.map(() => "")
}

export default function Offboarding() {
  const [phase, setPhase] = useState("setup") // setup | interview | synthesizing | submitted | error
  const [hires, setHires] = useState([])
  const [hiresLoading, setHiresLoading] = useState(true)
  const [hiresError, setHiresError] = useState(null)
  const [hireId, setHireId] = useState("")

  const [answers, setAnswers] = useState(emptyAnswers())
  const [questionIdx, setQuestionIdx] = useState(0)

  const [submitted, setSubmitted] = useState(null) // {session_id, rep_name}
  const [error, setError] = useState(null)
  const [existingSessions, setExistingSessions] = useState([])

  useEffect(() => {
    let cancelled = false
    setHiresLoading(true)
    getHires()
      .then((data) => {
        if (!cancelled) setHires(data || [])
      })
      .catch((err) => {
        if (!cancelled) setHiresError(err.message || "Failed to load SDRs")
      })
      .finally(() => {
        if (!cancelled) setHiresLoading(false)
      })
    // Load existing debriefs so we can warn an SDR who already submitted.
    listOffboardingSessions()
      .then((rows) => {
        if (!cancelled) setExistingSessions(Array.isArray(rows) ? rows : [])
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])

  const selectedHire = useMemo(
    () => hires.find((h) => h.hire_id === hireId) || null,
    [hires, hireId],
  )

  const existingForHire = useMemo(() => {
    if (!selectedHire) return null
    return (
      existingSessions.find(
        (r) => r.hire_id === selectedHire.hire_id || r.rep_name === selectedHire.name,
      ) || null
    )
  }, [existingSessions, selectedHire])

  const setupReady = !!selectedHire

  const startInterview = () => {
    if (!setupReady) return
    setAnswers(emptyAnswers())
    setQuestionIdx(0)
    setPhase("interview")
  }

  const updateAnswer = (idx, value) => {
    setAnswers((prev) => {
      const next = [...prev]
      next[idx] = value
      return next
    })
  }

  const goNext = async () => {
    if (questionIdx < OFFBOARDING_QUESTIONS.length - 1) {
      setQuestionIdx(questionIdx + 1)
      return
    }
    setPhase("synthesizing")
    setError(null)
    try {
      const qa_pairs = OFFBOARDING_QUESTIONS.map((q, i) => ({
        question_id: q.id,
        question: q.prompt,
        answer: answers[i] || "",
      }))
      const s = await synthesizeOffboarding({
        rep_info: {
          name: selectedHire.name,
          territory: selectedHire.territory,
          vertical: selectedHire.vertical,
          hire_id: selectedHire.hire_id,
        },
        qa_pairs,
      })
      if (s?.envelope?.status === "error") {
        setError(s.envelope.error?.message || "Synthesis failed")
        setPhase("error")
        return
      }
      setSubmitted({ session_id: s.session_id, rep_name: selectedHire.name })
      setPhase("submitted")
    } catch (err) {
      setError(err.message || "Failed to submit debrief")
      setPhase("error")
    }
  }

  const goBack = () => {
    if (questionIdx > 0) setQuestionIdx(questionIdx - 1)
  }

  const startOver = () => {
    setPhase("setup")
    setHireId("")
    setAnswers(emptyAnswers())
    setQuestionIdx(0)
    setSubmitted(null)
    setError(null)
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Onboarding debrief</h1>
        <p className="text-gray-500 text-sm">
          Just passed certification? Walk through a 7-question debrief on your ramp. The AI
          synthesizes your answers into a structured debrief — what worked, what was
          confusing, and what to improve — for your manager and the enablement team.
        </p>
      </div>

      {phase === "setup" && (
        <SetupPhase
          hires={hires}
          hireId={hireId}
          setHireId={setHireId}
          hiresLoading={hiresLoading}
          hiresError={hiresError}
          selectedHire={selectedHire}
          existingForHire={existingForHire}
          ready={setupReady}
          onStart={startInterview}
        />
      )}

      {phase === "interview" && (
        <InterviewPhase
          questionIdx={questionIdx}
          answers={answers}
          updateAnswer={updateAnswer}
          onBack={goBack}
          onNext={goNext}
          selectedHire={selectedHire}
        />
      )}

      {phase === "synthesizing" && <SynthesizingPhase />}

      {phase === "submitted" && submitted && (
        <SubmittedPhase submitted={submitted} onStartOver={startOver} />
      )}

      {phase === "error" && (
        <ErrorPhase error={error} onStartOver={startOver} />
      )}
    </div>
  )
}

function SetupPhase({
  hires,
  hireId,
  setHireId,
  hiresLoading,
  hiresError,
  selectedHire,
  existingForHire,
  ready,
  onStart,
}) {
  return (
    <div className="bg-white border-2 border-gray-100 rounded-lg p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-1">Your info</h2>
      <p className="text-sm text-gray-500 mb-6">
        Pick your name. Your territory and vertical are pulled from your profile — no
        need to retype them.
      </p>

      <div className="grid grid-cols-1 gap-4">
        <div>
          <label className="block text-xs uppercase tracking-wider text-gray-500 font-semibold mb-2">
            SDR (your name)
          </label>
          {hiresError ? (
            <div className="bg-red-50 rounded-md p-3 text-red-700 text-sm flex items-start gap-2">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-semibold">Could not load SDRs</div>
                <div className="mt-1 text-xs">{hiresError}</div>
              </div>
            </div>
          ) : (
            <select
              value={hireId}
              onChange={(e) => setHireId(e.target.value)}
              disabled={hiresLoading}
              className="w-full bg-gray-100 rounded-md px-4 py-2.5 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500 disabled:opacity-60"
            >
              <option value="">
                {hiresLoading ? "Loading SDRs…" : "Select your name…"}
              </option>
              {hires.map((h) => (
                <option key={h.hire_id} value={h.hire_id}>
                  {h.name} ({h.hire_id}) — {h.territory} · {h.vertical} · {h.experience_level}
                </option>
              ))}
            </select>
          )}
        </div>

        {selectedHire && (
          <div className="bg-blue-50/40 border border-blue-200 rounded-lg p-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
            <ReadOnlyField label="Territory" value={selectedHire.territory} />
            <ReadOnlyField label="Vertical" value={selectedHire.vertical} />
            <ReadOnlyField label="Experience" value={selectedHire.experience_level} />
          </div>
        )}

        {existingForHire && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">You already submitted a debrief</span> on{" "}
              {formatDate(existingForHire.created_at)}. Submitting again will{" "}
              <span className="font-semibold">replace</span> it as your current debrief — your
              manager will see the latest version.
            </div>
          </div>
        )}
      </div>

      <button
        onClick={onStart}
        disabled={!ready}
        className="mt-6 w-full bg-blue-500 text-white font-semibold py-3 rounded-md hover:bg-blue-600 hover:scale-[1.01] transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
      >
        <Play className="h-4 w-4" />
        {existingForHire ? "Start a replacement debrief" : "Start debrief"}
      </button>
    </div>
  )
}

function ReadOnlyField({ label, value }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">{label}</div>
      <div className="text-sm font-medium text-gray-900">{value || "—"}</div>
    </div>
  )
}

function InterviewPhase({ questionIdx, answers, updateAnswer, onBack, onNext, selectedHire }) {
  const total = OFFBOARDING_QUESTIONS.length
  const q = OFFBOARDING_QUESTIONS[questionIdx]
  const isLast = questionIdx === total - 1

  return (
    <div className="flex flex-col gap-5">
      <div>
        <div className="flex items-center justify-between mb-2 text-xs text-gray-500">
          <span className="font-semibold">
            Question {questionIdx + 1} of {total}
          </span>
          <span>
            {selectedHire?.name} · {selectedHire?.territory} · {selectedHire?.vertical}
          </span>
        </div>
        <ProgressBar current={questionIdx} total={total} />
      </div>

      <div className="bg-white border-2 border-gray-100 rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">{q.title}</h2>
        <p className="text-sm text-gray-600 mb-4">{q.prompt}</p>
        <textarea
          rows={6}
          value={answers[questionIdx] || ""}
          onChange={(e) => updateAnswer(questionIdx, e.target.value)}
          placeholder={q.placeholder}
          className="w-full bg-gray-100 rounded-md px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500 resize-none"
        />
      </div>

      <div className="flex items-center justify-between gap-3">
        <button
          onClick={onBack}
          disabled={questionIdx === 0}
          className="bg-gray-100 text-gray-900 font-semibold px-5 py-2.5 rounded-md hover:bg-gray-200 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>

        <button
          onClick={onNext}
          className="bg-blue-500 text-white font-semibold px-6 py-2.5 rounded-md hover:bg-blue-600 hover:scale-[1.01] transition-all flex items-center gap-2"
        >
          {isLast ? (
            <>
              <Sparkles className="h-4 w-4" />
              Submit to manager
            </>
          ) : (
            <>
              Next
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </div>
    </div>
  )
}

function SynthesizingPhase() {
  return (
    <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-12 flex flex-col items-center justify-center gap-3 min-h-[24rem]">
      <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
      <div className="text-sm font-semibold text-gray-600">
        Synthesizing your onboarding debrief…
      </div>
      <div className="text-xs text-gray-400 text-center max-w-md">
        Pulling territory and vertical playbook context and structuring your answers into
        what worked, barriers, and suggested improvements. This usually takes 10-30 seconds.
      </div>
    </div>
  )
}

function SubmittedPhase({ submitted, onStartOver }) {
  return (
    <div className="bg-emerald-50 border-2 border-emerald-200 rounded-lg p-8 flex flex-col items-center text-center">
      <CheckCircle className="h-12 w-12 text-emerald-500 mb-3" />
      <h2 className="text-2xl font-extrabold text-gray-900 mb-2">
        Debrief submitted
      </h2>
      <p className="text-sm text-gray-700 max-w-md">
        Thanks, {submitted.rep_name}. Your onboarding debrief has been sent to your manager
        and the enablement team — they'll review it to improve the program for the next
        cohort.
      </p>
      <div className="mt-4 text-xs text-gray-500 font-mono">
        Reference: {submitted.session_id}
      </div>
      <button
        onClick={onStartOver}
        className="mt-6 bg-white border-2 border-emerald-300 text-emerald-700 rounded-md px-5 py-2.5 text-sm font-semibold hover:bg-emerald-50 transition-all flex items-center gap-2"
      >
        Submit another
      </button>
    </div>
  )
}

function ErrorPhase({ error, onStartOver }) {
  return (
    <div className="flex flex-col gap-4">
      <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 text-red-700 text-sm flex items-start gap-2">
        <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
        <div>
          <div className="font-semibold">Submission failed</div>
          <div className="mt-1 text-xs">{error || "Unknown error"}</div>
        </div>
      </div>
      <button
        onClick={onStartOver}
        className="self-start bg-blue-500 text-white rounded-md px-5 py-2.5 font-semibold hover:bg-blue-600 transition-all flex items-center gap-2"
      >
        <RefreshCw className="h-4 w-4" />
        Start over
      </button>
    </div>
  )
}
