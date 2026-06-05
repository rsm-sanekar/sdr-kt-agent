import { useEffect, useRef, useState } from "react"
import {
  Loader2,
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  Send,
  PhoneOff,
  RefreshCw,
  Sparkles,
  Check,
  ArrowRight,
  MessageCircle,
} from "lucide-react"
import { getPersonas, simulateTurn, debriefSimulation } from "../lib/api"
import ScoreBadge from "../components/ScoreBadge"
import ScoreBreakdown from "../components/ScoreBreakdown"

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
      <div className="text-xs uppercase tracking-wider font-semibold mb-2 text-gray-700">{title}</div>
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

function ReviewReasons({ reasons }) {
  if (!reasons?.length) return null
  return (
    <div className="bg-amber-50 border-2 border-amber-500 rounded-lg p-4">
      <div className="flex items-center gap-2 text-amber-800 font-semibold text-sm mb-2">
        <AlertTriangle className="h-4 w-4" />
        Review suggested
      </div>
      <ul className="space-y-1 text-xs text-amber-900">
        {reasons.map((r, i) => <li key={i}>• {r}</li>)}
      </ul>
    </div>
  )
}

function PersonaCard({ persona, onPick }) {
  return (
    <button
      onClick={() => onPick(persona)}
      className="text-left bg-white border-2 border-gray-100 rounded-lg p-5 hover:border-blue-400 transition-colors"
    >
      <div className="flex items-center justify-between gap-2 flex-wrap mb-2">
        <h3 className="font-bold text-gray-900 text-base">{persona.name}</h3>
        <span className="bg-gray-100 text-gray-600 text-[10px] uppercase tracking-wider rounded-full px-2 py-0.5">
          {persona.vertical}
        </span>
      </div>
      <div className="text-xs text-gray-500 mb-3">
        {persona.role} · {persona.company}
      </div>
      <p className="text-sm text-gray-700 leading-relaxed mb-3 line-clamp-3">
        {persona.personality}
      </p>
      <div className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold mb-1">
        Typical objections
      </div>
      <ul className="text-xs text-gray-600 space-y-0.5">
        {(persona.top_objections || []).slice(0, 2).map((o, i) => (
          <li key={i} className="truncate">• {o}</li>
        ))}
      </ul>
    </button>
  )
}

function PersonaPicker({ personas, onPick, loading, error }) {
  if (loading) {
    return (
      <div className="flex items-center gap-2 text-gray-500 text-sm p-4">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading personas…
      </div>
    )
  }
  if (error) {
    return (
      <div className="bg-red-50 rounded-md p-4 text-red-700 text-sm flex items-start gap-2">
        <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
        <span>{error}</span>
      </div>
    )
  }
  return (
    <div>
      <div className="mb-4 text-sm text-gray-500">
        Pick a persona to practice against. Each one role-plays a different
        buyer style — Claude stays in character through the call.
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {personas.map((p) => (
          <PersonaCard key={p.id} persona={p} onPick={onPick} />
        ))}
      </div>
    </div>
  )
}

function ChatBubble({ message, personaName }) {
  const isTrainee = message.role === "trainee"
  if (isTrainee) {
    return (
      <div className="flex justify-end mb-2">
        <div className="bg-blue-500 text-white rounded-2xl rounded-tr-sm px-4 py-2 text-sm max-w-[80%] whitespace-pre-wrap">
          {message.text}
        </div>
      </div>
    )
  }
  return (
    <div className="flex flex-col items-start mb-2">
      <div className="text-[10px] uppercase tracking-wider text-gray-400 ml-1 mb-0.5">
        {personaName}
      </div>
      <div className="bg-gray-100 text-gray-900 rounded-2xl rounded-tl-sm px-4 py-2 text-sm max-w-[80%] whitespace-pre-wrap">
        {message.text}
      </div>
    </div>
  )
}

function ChatPhase({
  persona,
  messages,
  pendingText,
  setPendingText,
  onSend,
  onBack,
  onEnd,
  turnLoading,
  turnError,
  endLoading,
}) {
  const scrollRef = useRef(null)
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, turnLoading])

  return (
    <div className="flex flex-col gap-4">
      {/* Persona context bar */}
      <div className="bg-white border-2 border-gray-100 rounded-lg p-4 flex items-start justify-between gap-3 flex-wrap">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="font-bold text-gray-900">{persona.name}</h2>
            <span className="text-xs text-gray-500">{persona.role} · {persona.company}</span>
            <span className="bg-gray-100 text-gray-600 text-[10px] uppercase tracking-wider rounded-full px-2 py-0.5">
              {persona.vertical}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{persona.personality}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={onBack}
            className="bg-gray-100 text-gray-900 rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-gray-200 transition-colors flex items-center gap-1.5"
          >
            <ArrowLeft className="h-3 w-3" />
            Change persona
          </button>
          <button
            onClick={onEnd}
            disabled={messages.length === 0 || endLoading}
            className="bg-red-500 text-white rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-red-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            {endLoading ? <Loader2 className="h-3 w-3 animate-spin" /> : <PhoneOff className="h-3 w-3" />}
            End call &amp; debrief
          </button>
        </div>
      </div>

      {/* Chat */}
      <div
        ref={scrollRef}
        className="bg-gray-50 border-2 border-gray-100 rounded-lg p-4 min-h-[20rem] max-h-[28rem] overflow-y-auto"
      >
        {messages.length === 0 && (
          <div className="text-center text-gray-400 text-sm py-12">
            You're connected with {persona.name}. Open the call.
          </div>
        )}
        {messages.map((m, i) => (
          <ChatBubble key={i} message={m} personaName={persona.name} />
        ))}
        {turnLoading && (
          <div className="flex items-center gap-2 text-gray-500 text-xs italic mt-2">
            <Loader2 className="h-3 w-3 animate-spin" />
            {persona.name} is responding…
          </div>
        )}
      </div>

      {turnError && (
        <div className="bg-red-50 rounded-md p-3 text-red-700 text-sm flex items-start gap-2">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <span>{turnError}</span>
        </div>
      )}

      {/* Input */}
      <div>
        <textarea
          value={pendingText}
          onChange={(e) => setPendingText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) onSend()
          }}
          rows={3}
          placeholder={
            messages.length === 0
              ? "Open the call — your first line as the SDR."
              : "Your reply… (⌘+Enter to send)"
          }
          className="w-full bg-gray-100 rounded-md p-3 text-sm focus:outline-none focus:bg-white focus:border-2 focus:border-blue-500 resize-none"
        />
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-gray-400">⌘ + Enter to send</span>
          <button
            onClick={onSend}
            disabled={turnLoading || !pendingText.trim()}
            className="bg-blue-500 text-white rounded-md px-4 py-2 text-sm font-semibold hover:bg-blue-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            {turnLoading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Send className="h-3 w-3" />}
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

function DebriefPhase({ persona, debriefData, onStartOver, onBackToChat }) {
  const envelope = debriefData.envelope || {}
  const outputs = envelope.outputs || {}
  const reviewSuggested = envelope.review_required === true
  const isError = envelope.status === "error"

  if (isError) {
    return (
      <div className="flex flex-col gap-4">
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 text-red-700 text-sm flex items-start gap-2">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold">Debrief failed</div>
            <div className="mt-1 text-xs">{envelope.error?.message || "Unknown error"}</div>
          </div>
        </div>
        <button
          onClick={onBackToChat}
          className="self-start bg-gray-100 text-gray-900 rounded-md px-4 py-2 text-sm font-semibold hover:bg-gray-200 transition-colors flex items-center gap-1.5"
        >
          <ArrowLeft className="h-3 w-3" />
          Back to chat
        </button>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h2 className="text-2xl font-extrabold text-gray-900">Practice debrief</h2>
          <div className="text-xs text-gray-500 mt-1">
            vs. {persona.name} ({persona.role}, {persona.company} — {persona.vertical})
            {outputs.n_turns ? ` · ${outputs.n_turns} turns` : null}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onBackToChat}
            className="bg-gray-100 text-gray-900 rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-gray-200 transition-colors flex items-center gap-1.5"
          >
            <ArrowLeft className="h-3 w-3" />
            Back to chat
          </button>
          <button
            onClick={onStartOver}
            className="bg-blue-500 text-white rounded-md px-3 py-1.5 text-xs font-semibold hover:bg-blue-600 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className="h-3 w-3" />
            Practice again
          </button>
        </div>
      </div>

      <ScoreBadge weighted_total={outputs.weighted_total} />
      {reviewSuggested && <ReviewReasons reasons={outputs.review_reasons} />}
      <ScoreBreakdown dimension_scores={outputs.dimension_scores} />
      <ListBox title="What worked" items={outputs.what_worked} color="emerald" />
      <ListBox title="What to improve" items={outputs.what_to_improve} color="amber" />
      <ListBox title="Language alternatives" items={outputs.language_alternatives} color="blue" />
    </div>
  )
}

export default function Simulation() {
  const [phase, setPhase] = useState("picker") // picker | chat | debriefing | debrief
  const [personas, setPersonas] = useState([])
  const [personasLoading, setPersonasLoading] = useState(true)
  const [personasError, setPersonasError] = useState(null)

  const [persona, setPersona] = useState(null)
  const [messages, setMessages] = useState([])
  const [pendingText, setPendingText] = useState("")
  const [turnLoading, setTurnLoading] = useState(false)
  const [turnError, setTurnError] = useState(null)
  const [endLoading, setEndLoading] = useState(false)
  const [debriefData, setDebriefData] = useState(null)

  useEffect(() => {
    let cancelled = false
    getPersonas()
      .then((data) => {
        if (cancelled) return
        if (Array.isArray(data)) setPersonas(data)
        else setPersonasError("Server returned an unexpected shape")
      })
      .catch((err) => {
        if (!cancelled) setPersonasError(err.message || "Failed to load personas")
      })
      .finally(() => {
        if (!cancelled) setPersonasLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const handlePickPersona = (p) => {
    setPersona(p)
    setMessages([])
    setPendingText("")
    setTurnError(null)
    setDebriefData(null)
    setPhase("chat")
  }

  const handleSend = async () => {
    if (!persona || !pendingText.trim() || turnLoading) return
    const text = pendingText.trim()
    const nextMessages = [...messages, { role: "trainee", text }]
    setMessages(nextMessages)
    setPendingText("")
    setTurnLoading(true)
    setTurnError(null)
    try {
      const env = await simulateTurn({
        persona_id: persona.id,
        messages: nextMessages,
      })
      if (env?.status === "error") {
        setTurnError(env.error?.message || "Simulation turn failed")
      } else {
        const reply = env?.outputs?.prospect_response || ""
        setMessages([...nextMessages, { role: "prospect", text: reply }])
      }
    } catch (err) {
      setTurnError(err.message || "Failed to reach the simulation backend")
    } finally {
      setTurnLoading(false)
    }
  }

  const handleEnd = async () => {
    if (!persona || messages.length === 0 || endLoading) return
    setEndLoading(true)
    setPhase("debriefing")
    try {
      const result = await debriefSimulation({
        persona_id: persona.id,
        messages,
      })
      setDebriefData(result)
      setPhase("debrief")
    } catch (err) {
      setTurnError(err.message || "Failed to generate debrief")
      setPhase("chat")
    } finally {
      setEndLoading(false)
    }
  }

  const handleBackToChat = () => {
    setPhase("chat")
  }

  const handleStartOver = () => {
    setPersona(null)
    setMessages([])
    setPendingText("")
    setTurnError(null)
    setDebriefData(null)
    setPhase("picker")
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-1">Cold Call Simulation</h1>
        <p className="text-sm text-gray-500">
          Practice cold calls against an AI prospect. Pick a persona, hold a
          live chat, then get a debrief scored against Coaching Rubric v3.1.
        </p>
      </div>

      {phase === "picker" && (
        <PersonaPicker
          personas={personas}
          onPick={handlePickPersona}
          loading={personasLoading}
          error={personasError}
        />
      )}

      {phase === "chat" && persona && (
        <ChatPhase
          persona={persona}
          messages={messages}
          pendingText={pendingText}
          setPendingText={setPendingText}
          onSend={handleSend}
          onBack={handleStartOver}
          onEnd={handleEnd}
          turnLoading={turnLoading}
          turnError={turnError}
          endLoading={endLoading}
        />
      )}

      {phase === "debriefing" && (
        <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-12 flex flex-col items-center justify-center gap-3 min-h-[20rem]">
          <Sparkles className="h-6 w-6 text-blue-500" />
          <Loader2 className="h-6 w-6 text-blue-500 animate-spin" />
          <div className="text-sm font-semibold text-gray-600">Generating debrief…</div>
          <div className="text-xs text-gray-400 text-center max-w-md">
            Replaying the conversation and scoring against the four-dimension
            coaching rubric.
          </div>
        </div>
      )}

      {phase === "debrief" && persona && debriefData && (
        <DebriefPhase
          persona={persona}
          debriefData={debriefData}
          onStartOver={handleStartOver}
          onBackToChat={handleBackToChat}
        />
      )}
    </div>
  )
}
