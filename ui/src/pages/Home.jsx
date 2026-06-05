import { Link } from "react-router-dom"
import {
  ArrowRight,
  Users,
  Sparkles,
  Target,
  Shield,
  TrendingUp,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Database,
  GitBranch,
  MessageCircle,
  Clock,
  Search,
  Zap,
  BookOpen,
  ExternalLink,
} from "lucide-react"
import { useRole } from "../lib/roleContext"

const PROCESS_ROWS = [
  {
    step: "Build personalized Trailhead plan",
    link: "/preboarding",
    skill: "generate-onboarding-plan (LLM skill)",
    current: "60–90 min",
    ai: "5–10 min review",
    why: "RAG retrieves policy + gold-standard template; LLM adapts; module-id allow-list catches hallucination.",
    confidence: "High",
  },
  {
    step: "Rank and assign mentor",
    link: "/preboarding",
    skill: "rank-trail-guides (deterministic)",
    current: "20–40 min",
    ai: "1–2 min approve",
    why: "Deterministic 5-component scoring across all AEs; reviewer sees per-component breakdown.",
    confidence: "High",
  },
  {
    step: "Personalized welcome email",
    link: "/preboarding",
    skill: "welcome-new-hire (deterministic)",
    current: "10–15 min",
    ai: "0 min (auto)",
    why: "Deterministic template + per-experience-level variant; no LLM, no review needed.",
    confidence: "High",
  },
  {
    step: "Score cold call against rubric",
    link: "/coaching",
    skill: "score-cold-call (LLM skill)",
    current: "15–25 min",
    ai: "5–10 min review",
    why: "LLM scores 4 dimensions; server recomputes weighted total to catch drift.",
    confidence: "Medium",
  },
  {
    step: "Answer SDR question (\"how do I…?\")",
    link: "/tutor",
    skill: "answer-sdr-question (AI Tutor)",
    current: "5–10 min (Slack ping)",
    ai: "1–2 min self-serve",
    why: "ChromaDB semantic retrieval over 16 KB docs + 7 scraped refs; citation chips; approval loop.",
    confidence: "Medium",
  },
  {
    step: "Role-play cold call + debrief",
    link: "/simulation",
    skill: "simulate-cold-call + debrief-cold-call",
    current: "30–45 min (manager role-play)",
    ai: "10–15 min (self-serve)",
    why: "Stateless persona LLM; same Rubric v3.1 used for both practice and manager scoring.",
    confidence: "Medium",
  },
  {
    step: "Certify SDR readiness against rubric",
    link: "/certification",
    skill: "score-certification (LLM skill)",
    current: "45–75 min",
    ai: "10–15 min review",
    why: "LLM scores 5 rubric dimensions with quoted evidence; server recomputes PASS/BORDERLINE/FAIL band from per-dimension scores to catch verdict drift.",
    confidence: "Medium",
  },
  {
    step: "Post-certification onboarding debrief",
    link: "/offboarding",
    skill: "generate-handoff-doc (LLM skill)",
    current: "60–90 min",
    ai: "10–15 min review",
    why: "Newly-certified SDR answers process questions; LLM synthesizes a debrief (what worked, barriers, improvements) for the manager; low confidence forces review.",
    confidence: "Medium",
  },
]

const SUMMARY_ROWS = [
  {
    Icon: Clock,
    metric: "Total manager time per hire",
    current: "200–305 min",
    ai: "32–54 min",
    change: "~80–85% reduction in manager hours",
  },
  {
    Icon: Users,
    metric: "Human review time per hire",
    current: "included above (no explicit review)",
    ai: "22–39 min (explicit, structured)",
    change: "May increase as % of total — review is now explicit and rubric-driven",
  },
  {
    Icon: GitBranch,
    metric: "Number of handoffs per hire",
    current: "5–7",
    ai: "2–3",
    change: "Fewer handoffs; auditable JSON envelope trail",
  },
  {
    Icon: AlertTriangle,
    metric: "Rework risk",
    current: "Medium",
    ai: "Low–medium",
    change: "Allow-list validation + deterministic ranking + server-side drift recompute",
  },
  {
    Icon: MessageCircle,
    metric: "New-hire wait time for answers",
    current: "1–4 hrs (Slack)",
    ai: "< 30 sec (Tutor self-serve)",
    change: "Same day → seconds",
  },
]

const KPI_ROWS = [
  {
    kpi: "Ramp time to full productivity",
    baseline: "3.1–3.2 mo industry; 6–8 wks top teams",
    anchor: "1",
    moves: "Compresses bottlenecks in plan-drafting, coaching, and Q&A.",
    mechanism: "Personalized plan + always-on Tutor + practice simulation",
  },
  {
    kpi: "SDR quota attainment %",
    baseline: "~60% of reps reach quota industry-wide",
    anchor: "3",
    moves: "Consistent rubric coaching reduces variance; same rubric for trainee practice and manager review.",
    mechanism: "Coaching Rubric v3.1 across score-cold-call + debrief-cold-call",
  },
  {
    kpi: "First-year onboarding cost per hire",
    baseline: "$8K–$15K typical",
    anchor: "2",
    moves: "Manager-time recapture of $120–$340 per hire offsets a meaningful slice.",
    mechanism: "All 7 automations",
  },
  {
    kpi: "SDR annual turnover",
    baseline: "30–39% median; 12% of cos. > 55%",
    anchor: "4",
    moves: "Faster ramp + better practice tooling → higher early confidence (indirect lever, not a guarantee).",
    mechanism: "Tutor + Simulation reduce isolation",
  },
  {
    kpi: "AI deflection rate on trainee Q&A",
    baseline: "Emerging KPI; AI tutors aim for 60–80% resolution without manager escalation",
    anchor: null,
    moves: "Trainee questions answered by AI Tutor with citations; only review_required cases route to manager.",
    mechanism: "answer-sdr-question + approval loop + KB feedback",
  },
  {
    kpi: "Coaching coverage compliance",
    baseline: "≥1 hr/wk + weekly call review per new rep; often missed",
    anchor: "5",
    moves: "Every call gets a rubric-drafted note so manager time goes to judgment, not transcription.",
    mechanism: "score-cold-call",
  },
]

const FAILURE_ROWS = [
  {
    mode: "LLM hallucinates a Trailhead module ID",
    detection: "Module IDs validated against trailhead_module_catalog.md allow-list; mismatch forces review_required=true.",
    status: "Detected",
  },
  {
    mode: "LLM math drift on weighted cold-call score",
    detection: "Server-side recomputes weighted total from per-dimension scores; drift > 1 point flags review.",
    status: "Detected",
  },
  {
    mode: "Tutor answers from weak/no evidence",
    detection: "ChromaDB cosine similarity < 0.40 forces flagged=true + review_required=true.",
    status: "Detected",
  },
  {
    mode: "Tutor self-reports low confidence",
    detection: "LLM confidence < 0.60 forces review_required=true.",
    status: "Detected",
  },
  {
    mode: "Low-confidence onboarding debrief auto-approved",
    detection: "Synthesis confidence < 0.65 forces review_required=true before it reaches the manager.",
    status: "Detected",
  },
  {
    mode: "Stale approved answer pollutes KB over time",
    detection: "Approved Q&A tagged source=\"approved_qa\"; rejected answers logged to gap_tracker.json. No detection of drift in the approved set itself.",
    status: "Partial",
  },
  {
    mode: "Cold-call simulation persona breaks character",
    detection: "No automated detection today; persona prompt constrains in-character + objection-from-list.",
    status: "Gap",
  },
  {
    mode: "Generated plan ignores per-hire summary",
    detection: "Skill emits summary_present=false flag and forces review_required=true when summary missing.",
    status: "Detected",
  },
]

const SOURCES = [
  {
    n: 1,
    title: "MarketBetter SDR Onboarding Guide 2026",
    url: "https://www.marketbetter.ai/blog/sdr-onboarding-guide-reduce-ramp-time-2026/",
    desc: "Industry SDR ramp benchmark — average 3.1–3.2 mo; top teams 6–8 wks",
  },
  {
    n: 2,
    title: "SalesHive — The True Cost of an SDR",
    url: "https://saleshive.com/blog/true-cost-sdr-sales-development-rep/",
    desc: "First-year SDR cost — $113K–$162K fully-loaded; $8K–$15K onboarding component",
  },
  {
    n: 3,
    title: "Orum — Guide to SDR Tenure",
    url: "https://www.orum.com/blog/sales-turnover",
    desc: "SDR quota attainment & tenure — 14–16 mo tenure, ~60% reach quota",
  },
  {
    n: 4,
    title: "SOMAmetrics — SDR Attrition Rate",
    url: "https://www.somametrics.com/sdr-attrition-rate/",
    desc: "30–39% annual median; 12% of cos. > 55%",
  },
  {
    n: 5,
    title: "WideAngle — Sales Coaching 101",
    url: "https://wideangle.com/sales-coaching-101-much-time-week-spent-per-rep/",
    desc: "Manager coaching cadence — ≥1 hr/wk + weekly call review during ramp",
  },
]

const PAIN_CARDS = [
  {
    Icon: Clock,
    accent: "rose",
    title: "Manager-side",
    headline: "3–5 hrs / hire",
    body: "Hand-drafts the Trailhead plan, eyeballs mentor pairings, scores cold calls from memory, fields Slack pings, and reconstructs departed reps' accounts. Repeated for every hire, every cohort.",
  },
  {
    Icon: Search,
    accent: "amber",
    title: "SDR-side",
    headline: "Days lost",
    body: "Googles for answers, shadows calls when an AE has time, works through a generic Trailhead checklist that ignores prior experience. Friction the new hire should never have to absorb.",
  },
  {
    Icon: AlertTriangle,
    accent: "violet",
    title: "Process-side",
    headline: "Inconsistent",
    body: "Rubric applied from memory; no audit trail; institutional knowledge walks out the door when an SDR leaves. Onboarding quality varies hire-by-hire, manager-by-manager.",
  },
]

const HERO_STATS = [
  { value: "~80%", label: "Time saved per hire" },
  { value: "120×", label: "ROI on AI spend" },
  { value: "8", label: "End-to-end automations" },
  { value: "<30s", label: "Answer latency" },
]

const PAIN_ACCENT = {
  rose: {
    border: "border-rose-200/70",
    bg: "bg-rose-50/30",
    iconBg: "bg-rose-100 text-rose-600",
    headline: "text-rose-700",
  },
  amber: {
    border: "border-amber-200/70",
    bg: "bg-amber-50/30",
    iconBg: "bg-amber-100 text-amber-600",
    headline: "text-amber-700",
  },
  violet: {
    border: "border-violet-200/70",
    bg: "bg-violet-50/30",
    iconBg: "bg-violet-100 text-violet-600",
    headline: "text-violet-700",
  },
}

function Eyebrow({ number, label }) {
  return (
    <div className="inline-flex items-center gap-2 text-xs uppercase tracking-wider font-semibold text-blue-600 mb-3">
      <span className="font-mono text-blue-400">{number}</span>
      <span className="h-px w-6 bg-blue-200" />
      {label}
    </div>
  )
}

function SectionDivider() {
  return (
    <div className="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent" />
  )
}

function StatusBadge({ status }) {
  const map = {
    Detected: { cls: "bg-emerald-100 text-emerald-700", Icon: CheckCircle },
    Partial: { cls: "bg-amber-100 text-amber-700", Icon: AlertTriangle },
    Gap: { cls: "bg-red-100 text-red-700", Icon: XCircle },
  }
  const { cls, Icon } = map[status] || map.Gap
  return (
    <span className={`inline-flex items-center gap-1 ${cls} rounded-full text-[10px] font-semibold px-2 py-0.5`}>
      <Icon className="w-3 h-3" />
      {status}
    </span>
  )
}

function ConfBadge({ level }) {
  const cls =
    level === "High"
      ? "bg-emerald-100 text-emerald-700"
      : level === "Medium"
      ? "bg-amber-100 text-amber-700"
      : "bg-gray-100 text-gray-600"
  return (
    <span className={`${cls} rounded-full text-[10px] font-semibold px-2 py-0.5`}>
      {level}
    </span>
  )
}

export default function Home() {
  const { setRole } = useRole()
  const pickManager = () => setRole("manager")
  const pickTrainee = () => setRole("trainee")

  return (
    <div className="bg-white">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-blue-50/40 border-b border-gray-100">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(59,130,246,0.10),transparent_50%),radial-gradient(circle_at_85%_60%,rgba(168,85,247,0.08),transparent_55%)] pointer-events-none" />
        <div className="relative max-w-6xl mx-auto px-6 py-20">
          <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 leading-[1.05] max-w-4xl tracking-tight">
            Cut SDR onboarding from{" "}
            <span className="bg-gradient-to-r from-blue-500 to-violet-500 bg-clip-text text-transparent">
              3 months
            </span>{" "}
            to{" "}
            <span className="bg-gradient-to-r from-blue-500 to-emerald-500 bg-clip-text text-transparent">
              6 weeks
            </span>
            <span className="text-gray-400"> —</span> your manager still controls every step.
          </h1>
          <p className="mt-6 text-lg text-gray-600 max-w-3xl leading-relaxed">
            An AI coworker that automates the seven most time-consuming tasks in Salesforce SDR onboarding —
            personalized plan, mentor matching, welcome email, call coaching, tutor Q&amp;A, cold-call practice,
            and exit-knowledge capture — with a confidence-flagged human-in-the-loop on every LLM artifact.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-3">
            <Link
              to="/app"
              className="inline-flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-semibold rounded-lg px-5 py-2.5 transition-all hover:shadow-lg hover:-translate-y-0.5"
            >
              Launch app
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/preboarding"
              onClick={pickManager}
              className="inline-flex items-center gap-2 bg-white border-2 border-gray-200 hover:border-blue-500 text-gray-900 text-sm font-semibold rounded-lg px-5 py-2.5 transition-all hover:-translate-y-0.5"
            >
              <Users className="w-4 h-4" />
              Manager workspace
            </Link>
            <Link
              to="/tutor"
              onClick={pickTrainee}
              className="inline-flex items-center gap-2 bg-white border-2 border-gray-200 hover:border-blue-500 text-gray-900 text-sm font-semibold rounded-lg px-5 py-2.5 transition-all hover:-translate-y-0.5"
            >
              <Sparkles className="w-4 h-4" />
              Trainee workspace
            </Link>
          </div>

          {/* Hero stat strip */}
          <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-3 max-w-4xl">
            {HERO_STATS.map((s) => (
              <div
                key={s.label}
                className="bg-white/70 backdrop-blur border border-gray-200/80 rounded-xl px-4 py-3 transition-all hover:-translate-y-0.5 hover:shadow-md"
              >
                <div className="text-2xl md:text-3xl font-extrabold bg-gradient-to-br from-blue-500 to-blue-700 bg-clip-text text-transparent">
                  {s.value}
                </div>
                <div className="text-[11px] text-gray-500 mt-1 leading-tight">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-6 py-20 space-y-20">
        {/* The manual world today — pain cards */}
        <section>
          <Eyebrow number="00" label="The problem" />
          <h2 className="text-3xl font-bold text-gray-900 mb-3">The manual world today</h2>
          <p className="text-gray-600 leading-relaxed max-w-3xl mb-8">
            Salesforce SDR onboarding is mostly invisible labor — done by managers, between meetings, with no audit
            trail. Three groups pay the cost.
          </p>
          <div className="grid md:grid-cols-3 gap-5">
            {PAIN_CARDS.map((c) => {
              const acc = PAIN_ACCENT[c.accent]
              return (
                <div
                  key={c.title}
                  className={`bg-white border-2 ${acc.border} ${acc.bg} rounded-xl p-6 transition-all hover:-translate-y-0.5 hover:shadow-md`}
                >
                  <div className={`w-11 h-11 ${acc.iconBg} rounded-xl flex items-center justify-center mb-4`}>
                    <c.Icon className="w-5 h-5" />
                  </div>
                  <div className="text-[11px] uppercase tracking-wider text-gray-500 font-semibold mb-1">
                    {c.title}
                  </div>
                  <div className={`text-2xl font-extrabold ${acc.headline} mb-3`}>{c.headline}</div>
                  <div className="text-sm text-gray-700 leading-relaxed">{c.body}</div>
                </div>
              )
            })}
          </div>
        </section>

        <SectionDivider />

        {/* Process Redesign — total-time callout + table */}
        <section>
          <Eyebrow number="01" label="Process redesign" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Before / after — the 7 tasks we automate
          </h2>
          <p className="text-gray-600 mb-8 max-w-3xl">
            Total manager time per hire collapses by 80–85%. Per-step breakdown below; click any automation to
            jump to its page.
          </p>

          {/* Total time callout */}
          <div className="bg-white border-2 border-gray-100 rounded-2xl p-6 md:p-7 mb-8 shadow-sm">
            <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-4">
              Total time per hire across the chain
            </div>
            <div className="grid md:grid-cols-2 gap-5">
              <div>
                <div className="flex items-baseline gap-2 mb-2">
                  <div className="text-[10px] uppercase tracking-wider text-rose-600 font-bold">Manual</div>
                </div>
                <div className="text-4xl font-extrabold text-gray-900 mb-2">200–305 min</div>
                <div className="h-3 bg-rose-100 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-rose-400 to-rose-500 rounded-full" style={{ width: "100%" }} />
                </div>
                <div className="text-xs text-gray-500 mt-2">~3.3–5 hrs of manager time per hire</div>
              </div>
              <div>
                <div className="flex items-baseline gap-2 mb-2">
                  <div className="text-[10px] uppercase tracking-wider text-emerald-600 font-bold">With AI</div>
                </div>
                <div className="text-4xl font-extrabold text-gray-900 mb-2">32–54 min</div>
                <div className="h-3 bg-emerald-100 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full" style={{ width: "18%" }} />
                </div>
                <div className="text-xs text-gray-500 mt-2">~30–60 min, mostly explicit review</div>
              </div>
            </div>
          </div>

          <div className="text-[11px] uppercase tracking-wider text-gray-500 font-semibold mb-3 flex items-center gap-2">
            Per-step breakdown
            <span className="text-gray-300">↓</span>
          </div>
          <div className="bg-white border border-gray-200/70 rounded-xl overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700">Process step</th>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700 whitespace-nowrap">
                      Current time / case
                    </th>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700 whitespace-nowrap">
                      AI-supported time / case
                    </th>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700">Why might time change?</th>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700 whitespace-nowrap">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {PROCESS_ROWS.map((r, i) => (
                    <tr
                      key={i}
                      className="border-b border-gray-100 last:border-b-0 hover:bg-blue-50/30 transition-colors"
                    >
                      <td className="px-5 py-4 align-top">
                        <div className="font-semibold text-gray-900">{r.step}</div>
                        <Link
                          to={r.link}
                          className="text-xs text-blue-500 hover:text-blue-700 font-medium inline-flex items-center gap-1 mt-0.5"
                        >
                          {r.skill}
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </td>
                      <td className="px-5 py-4 align-top text-gray-700 whitespace-nowrap font-mono text-xs">
                        {r.current}
                      </td>
                      <td className="px-5 py-4 align-top whitespace-nowrap">
                        <span className="text-emerald-700 font-mono text-xs font-semibold">{r.ai}</span>
                      </td>
                      <td className="px-5 py-4 align-top text-gray-600 leading-relaxed">{r.why}</td>
                      <td className="px-5 py-4 align-top">
                        <ConfBadge level={r.confidence} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <SectionDivider />

        {/* Process Summary Table */}
        <section>
          <Eyebrow number="02" label="Process summary" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Summary across the full chain</h2>
          <p className="text-gray-600 mb-8 max-w-3xl">
            The five rolled-up metrics that capture how the work shape-shifts when AI handles the drafting.
          </p>
          <div className="bg-white border border-gray-200/70 rounded-xl overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700">Metric</th>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700">Current process estimate</th>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700">AI-supported process estimate</th>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700">Expected change</th>
                  </tr>
                </thead>
                <tbody>
                  {SUMMARY_ROWS.map((r, i) => (
                    <tr
                      key={i}
                      className="border-b border-gray-100 last:border-b-0 hover:bg-blue-50/30 transition-colors"
                    >
                      <td className="px-5 py-4 align-top">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 bg-blue-50 text-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                            <r.Icon className="w-3.5 h-3.5" />
                          </div>
                          <span className="font-semibold text-gray-900">{r.metric}</span>
                        </div>
                      </td>
                      <td className="px-5 py-4 align-top text-gray-700">{r.current}</td>
                      <td className="px-5 py-4 align-top text-gray-700">{r.ai}</td>
                      <td className="px-5 py-4 align-top text-gray-600">{r.change}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <SectionDivider />

        {/* Cost Estimate */}
        <section>
          <Eyebrow number="03" label="Cost estimate" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">What it actually costs</h2>
          <p className="text-gray-600 mb-8 max-w-3xl">
            Standard formula{" "}
            <code className="bg-gray-100 px-1.5 py-0.5 rounded text-[12px] text-gray-700 font-mono">
              minutes / 60 × hourly_rate
            </code>
            . Hourly rates labeled as assumption — no claim of exact company costs.
          </p>
          <div className="grid md:grid-cols-2 gap-5">
            <div className="bg-gradient-to-br from-rose-50/60 to-white border-2 border-rose-200/70 rounded-2xl p-6 transition-all hover:-translate-y-0.5 hover:shadow-md">
              <div className="flex items-center gap-2 mb-3">
                <Clock className="w-4 h-4 text-rose-600" />
                <div className="text-xs uppercase tracking-wider text-rose-700 font-bold">
                  Manual onboarding (1 hire)
                </div>
              </div>
              <div className="text-4xl font-extrabold text-gray-900">$167 – $254</div>
              <div className="text-xs text-gray-500 mt-1.5">in manager labor</div>
              <div className="text-sm text-gray-700 mt-5 leading-relaxed border-t border-rose-100 pt-4">
                <code className="bg-white border border-gray-200 px-1.5 py-0.5 rounded text-[11px] font-mono">
                  200–305 min / 60 × $50/hr
                </code>
                <div className="mt-2 text-gray-600">
                  At $75/hr sensitivity:{" "}
                  <span className="font-semibold text-gray-900">$250–$381</span>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-emerald-50/60 to-white border-2 border-emerald-200/70 rounded-2xl p-6 transition-all hover:-translate-y-0.5 hover:shadow-md">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                <div className="text-xs uppercase tracking-wider text-emerald-700 font-bold">
                  With the AI agent (1 hire)
                </div>
              </div>
              <div className="text-4xl font-extrabold text-gray-900">$27 – $45</div>
              <div className="text-xs text-gray-500 mt-1.5">in manager labor + $0.50–$1.50 AI cost</div>
              <div className="text-sm text-gray-700 mt-5 leading-relaxed border-t border-emerald-100 pt-4">
                <code className="bg-white border border-gray-200 px-1.5 py-0.5 rounded text-[11px] font-mono">
                  32–54 min / 60 × $50/hr
                </code>
                <div className="mt-2 text-gray-600">
                  AI inference: ~$0.03/call × ~20 calls ≈ ~$1/hire
                </div>
              </div>
            </div>
          </div>
          <div className="mt-5 grid md:grid-cols-3 gap-4">
            {[
              { label: "Estimated savings", value: "$120 – $225", note: "per hire (mid case)", Icon: TrendingUp },
              { label: "ROI", value: "~120×", note: "every $1 spent on AI returns ~$120", Icon: Zap },
              { label: "Payback period", value: "~0", note: "AI is pay-per-use; savings from hire 1", Icon: CheckCircle },
            ].map((s) => (
              <div
                key={s.label}
                className="bg-gradient-to-br from-blue-50 to-white border-2 border-blue-200/70 rounded-xl p-5 transition-all hover:-translate-y-0.5 hover:shadow-md"
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <s.Icon className="w-3.5 h-3.5 text-blue-600" />
                  <div className="text-xs uppercase tracking-wider text-blue-700 font-bold">{s.label}</div>
                </div>
                <div className="text-3xl font-extrabold text-gray-900">{s.value}</div>
                <div className="text-xs text-gray-600 mt-1">{s.note}</div>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-5 italic leading-relaxed">
            $50/hr is the mid anchor of the $30/$50/$75 band suggested for labor cost assumptions. AI cost based
            on Claude Sonnet 4.6 list pricing ($3/MTok input + $15/MTok output) at ~5K in + 1K out per call.
          </p>
        </section>

        <SectionDivider />

        {/* Market-Standard KPIs — card grid (was table) */}
        <section>
          <Eyebrow number="04" label="Market-standard SDR KPIs" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">The industry KPIs we move</h2>
          <p className="text-gray-600 mb-8 max-w-3xl">
            Globally-recognized SDR/sales metrics with their industry baselines, mapped to the prototype feature
            that moves each one.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {KPI_ROWS.map((r, i) => (
              <div
                key={i}
                className="bg-white border border-gray-200/70 rounded-xl p-5 transition-all hover:-translate-y-0.5 hover:shadow-md hover:border-blue-300/60"
              >
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="font-bold text-gray-900 text-base leading-snug">{r.kpi}</div>
                  {r.anchor ? (
                    <a
                      href={`#source-${r.anchor}`}
                      className="bg-blue-50 text-blue-700 text-[10px] font-semibold rounded px-1.5 py-0.5 hover:bg-blue-100 flex-shrink-0"
                    >
                      [{r.anchor}]
                    </a>
                  ) : (
                    <span className="text-gray-400 text-[10px] flex-shrink-0">est.</span>
                  )}
                </div>
                <div className="bg-gray-50 border border-gray-200/60 rounded-lg px-3 py-2 mb-3">
                  <div className="text-[10px] uppercase tracking-wider text-gray-500 font-semibold mb-0.5">
                    Industry baseline
                  </div>
                  <div className="text-sm text-gray-800 font-medium">{r.baseline}</div>
                </div>
                <div className="text-sm text-gray-700 leading-relaxed mb-3">{r.moves}</div>
                <div className="inline-flex items-center gap-1.5 bg-blue-50 text-blue-700 text-[11px] font-semibold rounded-full px-2.5 py-1">
                  <Zap className="w-3 h-3" />
                  {r.mechanism}
                </div>
              </div>
            ))}
          </div>
        </section>

        <SectionDivider />

        {/* Quality Measures */}
        <section>
          <Eyebrow number="05" label="Quality measures" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Beyond time saved — how quality improves</h2>
          <p className="text-gray-600 mb-8 max-w-3xl">
            Four measurable quality dimensions mapped to the prototype features that drive them.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              {
                Icon: Target,
                title: "More consistent recommendations",
                body:
                  "Every coaching note and debrief scored against the same Coaching Rubric v3.1; LLM drift > 1 point auto-flags review_required. The trainee's Cold Call Simulation uses the same rubric the manager will see — no surprises.",
              },
              {
                Icon: Database,
                title: "Better use of internal documents",
                body:
                  "Every LLM answer is grounded in 14 internal docs + 7 curated Salesforce references. The AI Tutor shows clickable [n] citation chips so the SDR can verify every claim against the source passage.",
              },
              {
                Icon: GitBranch,
                title: "Fewer missed steps",
                body:
                  "JSON envelope next_action chains the orchestrator deterministically (plan → rank → email). Every step has an explicit review_required flag and approve/edit/reject UI — no quiet sign-offs.",
              },
              {
                Icon: CheckCircle,
                title: "More complete reports",
                body:
                  "generate-handoff-doc structures the post-certification debrief into per-element feedback, ramp barriers, and suggested improvements. Low-confidence syntheses force manager review before they reach the enablement team.",
              },
            ].map((c) => (
              <div
                key={c.title}
                className="bg-white border border-gray-200/70 rounded-xl p-6 transition-all hover:-translate-y-0.5 hover:shadow-md hover:border-blue-300/60"
              >
                <div className="flex items-start gap-4">
                  <div className="w-11 h-11 bg-gradient-to-br from-blue-50 to-blue-100 text-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
                    <c.Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-bold text-gray-900 mb-1.5">{c.title}</div>
                    <div className="text-sm text-gray-700 leading-relaxed">{c.body}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <SectionDivider />

        {/* Face Validity */}
        <section>
          <Eyebrow number="06" label="Face validity check" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Would these results make sense to someone in the role?
          </h2>
          <p className="text-gray-600 mb-8 max-w-3xl">
            Four standard face-validity questions, plus the public anchors that ground the numbers.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              {
                q: "Does the direction make sense?",
                a:
                  "Yes — AI compresses information-retrieval and rubric-application work (which it's good at) while preserving manager review where judgment is still needed (artifact approval, mentor sign-off, onboarding-debrief review).",
              },
              {
                q: "Is the size of effect plausible?",
                a:
                  "Yes — 80–85% manager-time reduction per hire is below the 90%+ claims of some AI-SDR vendors but above naive automation, consistent with our scope (we automate drafting + scoring + retrieval, not the relational work).",
              },
              {
                q: "Does output match the evidence shown?",
                a:
                  "Yes — every Tutor answer ships with cited passages; every coaching score ships with the dimension breakdown the rubric prescribes; every mentor ranking ships with per-component scores so the manager can audit \"why this AE.\"",
              },
              {
                q: "Does it respect practical constraints?",
                a:
                  "Yes — review is explicit, not skipped; approve/edit/reject is mandatory on every LLM artifact; module IDs validated against an allow-list (compliance); high-risk accounts forced into dual-approval (governance).",
              },
            ].map((row, i) => (
              <div
                key={i}
                className="bg-white border border-gray-200/70 rounded-xl p-5 transition-all hover:-translate-y-0.5 hover:shadow-md hover:border-blue-300/60"
              >
                <div className="flex items-start gap-3 mb-2">
                  <div className="w-8 h-8 bg-emerald-50 text-emerald-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <div className="font-bold text-gray-900 text-[15px] leading-snug pt-1">
                    <span className="text-blue-500 font-mono mr-1.5">({i + 1})</span>
                    {row.q}
                  </div>
                </div>
                <div className="text-sm text-gray-700 leading-relaxed pl-11">{row.a}</div>
              </div>
            ))}
          </div>

          {/* Sources — card grid */}
          <div className="mt-8">
            <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-4 flex items-center gap-2">
              <BookOpen className="w-3.5 h-3.5" />
              Public anchors
            </div>
            <div className="grid md:grid-cols-2 gap-3">
              {SOURCES.map((s) => (
                <a
                  key={s.n}
                  id={`source-${s.n}`}
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group bg-white border border-gray-200/70 rounded-xl p-4 transition-all hover:-translate-y-0.5 hover:shadow-md hover:border-blue-300/60 flex items-start gap-3"
                >
                  <div className="w-8 h-8 bg-blue-50 text-blue-700 rounded-lg flex items-center justify-center font-bold text-xs flex-shrink-0">
                    {s.n}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start gap-1.5">
                      <span className="font-semibold text-gray-900 text-sm group-hover:text-blue-600 transition-colors">
                        {s.title}
                      </span>
                      <ExternalLink className="w-3 h-3 text-gray-400 mt-0.5 flex-shrink-0" />
                    </div>
                    <div className="text-xs text-gray-600 mt-1 leading-relaxed">{s.desc}</div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>

        <SectionDivider />

        {/* Testing AI Performance */}
        <section>
          <Eyebrow number="07" label="Testing AI performance" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Likely failure modes — and which we detect today
          </h2>
          <p className="text-gray-600 mb-8 max-w-3xl">
            What can go wrong with an AI coworker, what our prototype already guards against, and the gaps we
            acknowledge.
          </p>
          <div className="bg-white border border-gray-200/70 rounded-xl overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700">Likely failure mode</th>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700">Detection in our prototype</th>
                    <th className="text-left px-5 py-3.5 font-semibold text-gray-700 whitespace-nowrap">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {FAILURE_ROWS.map((r, i) => (
                    <tr
                      key={i}
                      className="border-b border-gray-100 last:border-b-0 hover:bg-blue-50/30 transition-colors"
                    >
                      <td className="px-5 py-4 align-top font-semibold text-gray-900">{r.mode}</td>
                      <td className="px-5 py-4 align-top text-gray-600 leading-relaxed">{r.detection}</td>
                      <td className="px-5 py-4 align-top">
                        <StatusBadge status={r.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <SectionDivider />

        {/* Under the hood */}
        <section>
          <Eyebrow number="08" label="Under the hood" />
          <h2 className="text-3xl font-bold text-gray-900 mb-8">What we built</h2>
          <div className="grid md:grid-cols-3 gap-3">
            {[
              { Icon: Database, title: "Knowledge base", body: "16 proprietary KB docs + 7 web-scraped Salesforce references" },
              { Icon: TrendingUp, title: "Hybrid retrieval", body: "BM25 (chain skills) + ChromaDB semantic (AI Tutor)" },
              { Icon: GitBranch, title: "Orchestrator chain", body: "JSON envelope handoff between skills; next_action routing" },
              { Icon: MessageCircle, title: "2 MCP servers", body: "Read-only data resources + callable tools" },
              { Icon: Shield, title: "Human-in-the-loop", body: "Confidence + review flag on every LLM artifact; approve/edit/reject UI" },
              { Icon: Sparkles, title: "Role-aware UI", body: "Trainee vs Manager views; rubric continuity across both" },
            ].map((c) => (
              <div
                key={c.title}
                className="bg-white border border-gray-200/70 rounded-xl p-4 transition-all hover:-translate-y-0.5 hover:shadow-md hover:border-blue-300/60"
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <c.Icon className="w-4 h-4 text-blue-500" />
                  <div className="font-semibold text-gray-900 text-sm">{c.title}</div>
                </div>
                <div className="text-xs text-gray-600 leading-relaxed">{c.body}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Footer CTA */}
        <section className="relative overflow-hidden bg-gradient-to-br from-blue-500 via-blue-600 to-violet-600 rounded-2xl p-10 text-center">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_30%,rgba(255,255,255,0.15),transparent_50%),radial-gradient(circle_at_80%_70%,rgba(255,255,255,0.10),transparent_55%)] pointer-events-none" />
          <div className="relative">
            <h2 className="text-3xl font-bold text-white mb-3">Ready to see it in action?</h2>
            <p className="text-blue-50 text-sm mb-7 max-w-2xl mx-auto leading-relaxed">
              Launch the workspace as a manager (full chain, approvals, dashboards) or as a trainee (AI tutor and
              cold-call simulation).
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link
                to="/app"
                className="inline-flex items-center gap-2 bg-white text-blue-600 hover:bg-blue-50 text-sm font-semibold rounded-lg px-5 py-2.5 transition-all hover:-translate-y-0.5 hover:shadow-lg"
              >
                Launch app
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/preboarding"
                onClick={pickManager}
                className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white text-sm font-semibold rounded-lg px-5 py-2.5 transition-all hover:-translate-y-0.5 border border-white/30 backdrop-blur"
              >
                <Users className="w-4 h-4" />
                Manager workspace
              </Link>
              <Link
                to="/tutor"
                onClick={pickTrainee}
                className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white text-sm font-semibold rounded-lg px-5 py-2.5 transition-all hover:-translate-y-0.5 border border-white/30 backdrop-blur"
              >
                <Sparkles className="w-4 h-4" />
                Trainee workspace
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
