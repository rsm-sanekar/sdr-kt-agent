import { Link } from 'react-router-dom'

/* ── Inline SVG icons ─────────────────────────────────────────────────────── */
const IconBrain = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/>
    <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/>
    <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/>
    <path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/>
    <path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/>
  </svg>
)
const IconRocket = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
    <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>
    <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>
    <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>
  </svg>
)
const IconBook = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
  </svg>
)
const IconMic = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" y1="19" x2="12" y2="22"/>
    <line x1="8" y1="22" x2="16" y2="22"/>
  </svg>
)

/* ── Hero illustration — flat geometric ──────────────────────────────────── */
function HeroIllustration() {
  return (
    <div className="relative h-[420px] w-full select-none">
      {/* Background circle */}
      <div className="absolute top-4 right-0 w-80 h-80 bg-blue-50 rounded-full" />

      {/* Main blue rectangle */}
      <div className="absolute top-0 left-4 w-56 h-44 bg-blue-500 rounded-3xl" />

      {/* Emerald overlapping rectangle */}
      <div className="absolute top-20 left-28 w-48 h-36 bg-emerald-500 rounded-2xl" />

      {/* Amber circle */}
      <div className="absolute top-8 right-12 w-28 h-28 bg-amber-400 rounded-full" />

      {/* Small blue circle */}
      <div className="absolute bottom-24 left-0 w-14 h-14 bg-blue-200 rounded-full" />

      {/* Tiny emerald circle */}
      <div className="absolute top-2 right-40 w-8 h-8 bg-emerald-200 rounded-full" />

      {/* Floating white metric card */}
      <div className="absolute bottom-8 right-4 bg-white border-2 border-gray-100 rounded-2xl p-4 w-44">
        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">KB Health</div>
        <div className="text-4xl font-extrabold text-blue-500">89%</div>
        <div className="text-xs text-gray-500 mt-0.5">approval rate</div>
        <div className="flex items-end gap-1 mt-2 h-8">
          {[5, 7, 6, 9, 7, 8, 9].map((v, i) => (
            <div key={i} className="flex-1 bg-blue-500 rounded-sm" style={{ height: `${v * 4}px` }} />
          ))}
        </div>
      </div>

      {/* Approval badge */}
      <div className="absolute bottom-12 left-12 bg-blue-600 text-white text-xs font-bold px-4 py-2 rounded-full">
        1,847 KB chunks stored
      </div>

      {/* Small gray rectangle filler */}
      <div className="absolute bottom-32 right-8 w-12 h-20 bg-gray-200 rounded-xl" />
    </div>
  )
}

/* ── Stat card for the problem section ────────────────────────────────────── */
function StatCard({ value, label, bg }) {
  return (
    <div className={`${bg} rounded-2xl p-8 text-white`}>
      <div className="text-5xl font-extrabold mb-2">{value}</div>
      <div className="text-base font-medium opacity-90">{label}</div>
    </div>
  )
}

/* ── Feature card ─────────────────────────────────────────────────────────── */
function FeatureCard({ icon, title, description, step, bg, iconColor }) {
  return (
    <div className="bg-white border-2 border-gray-100 rounded-2xl p-6">
      <div className={`w-12 h-12 ${bg} rounded-xl flex items-center justify-center mb-4 ${iconColor}`}>
        {icon}
      </div>
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-bold text-gray-900 text-lg">{title}</h3>
        <span className="text-xs font-semibold bg-gray-100 text-gray-500 px-2.5 py-1 rounded-full">{step}</span>
      </div>
      <p className="text-gray-500 text-sm leading-relaxed">{description}</p>
    </div>
  )
}

/* ── Loop step ────────────────────────────────────────────────────────────── */
function LoopStep({ icon, label, sub }) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-3 text-2xl">
        {icon}
      </div>
      <div className="font-bold text-white text-sm">{label}</div>
      <div className="text-blue-100 text-xs mt-1">{sub}</div>
    </div>
  )
}

/* ── Main ─────────────────────────────────────────────────────────────────── */
export default function Homepage() {
  return (
    <div className="font-sans bg-white">

      {/* ── Navbar ── */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 1L2 4.5v7L8 15l6-3.5v-7L8 1z" fill="white"/>
              </svg>
            </div>
            <span className="font-extrabold text-gray-900">KT Agent</span>
            <span className="text-gray-400 text-sm font-medium hidden sm:block">for Salesforce SDR</span>
          </div>

          <nav className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">Features</a>
            <a href="#how-it-works" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">How it Works</a>
            <a href="#why-it-works" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">Why It Works</a>
          </nav>

          <Link
            to="/tutor"
            className="bg-blue-500 text-white text-sm font-semibold px-6 py-2 rounded-md hover:bg-blue-600 hover:scale-105 transition-scale"
          >
            Launch App
          </Link>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="bg-white overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 py-24 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left */}
          <div>
            <div className="inline-block text-blue-500 text-sm font-semibold uppercase tracking-wider mb-4">
              MGT 449 · GenAI for Business
            </div>
            <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight leading-[1.1] mb-6">
              The onboarding agent that gets smarter every day
            </h1>
            <p className="text-xl text-gray-500 leading-relaxed mb-8">
              AI-powered knowledge transfer for Salesforce SDRs. Every approved
              interaction feeds back into a shared knowledge base.
            </p>
            <div className="flex items-center gap-4">
              <Link
                to="/tutor"
                className="bg-blue-500 text-white font-semibold px-7 py-3 rounded-md hover:bg-blue-600 hover:scale-105 transition-scale"
              >
                Launch App
              </Link>
              <a
                href="#how-it-works"
                className="border-4 border-blue-500 text-blue-500 font-semibold px-6 py-2.5 rounded-md hover:bg-blue-500 hover:text-white transition-colors"
              >
                See How It Works
              </a>
            </div>
          </div>

          {/* Right — geometric illustration */}
          <div className="hidden lg:block">
            <HeroIllustration />
          </div>
        </div>
      </section>

      {/* ── Problem stats ── */}
      <section id="why-it-works" className="bg-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <h2 className="text-3xl font-extrabold text-gray-900 text-center mb-3">
            The SDR onboarding problem
          </h2>
          <p className="text-gray-500 text-center mb-12 max-w-xl mx-auto">
            Despite massive training investments, SDR onboarding remains slow, manual, and lossy.
          </p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard value="42%" label="Quota attainment despite top-10% training investment" bg="bg-blue-500" />
            <StatCard value="72hrs" label="Average feedback latency after a call" bg="bg-emerald-500" />
            <StatCard value="3–5hrs" label="Manager time on manual call review weekly" bg="bg-amber-500" />
            <StatCard value="5–10d" label="Content update lag after product changes" bg="bg-gray-800" />
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section id="how-it-works" className="bg-white">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <h2 className="text-3xl font-extrabold text-gray-900 text-center mb-3">
            Four features. One self-improving system.
          </h2>
          <p className="text-gray-500 text-center mb-12 max-w-xl mx-auto">
            Every feature connects to the same shared ChromaDB knowledge base that grows with every approval.
          </p>
          <div id="features" className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <FeatureCard
              icon={<IconBrain />}
              title="AI Tutor"
              description="SDRs ask product questions in plain English. Claude answers with citations from the KB. Approved answers feed back in."
              step="Step 4"
              bg="bg-blue-50"
              iconColor="text-blue-600"
            />
            <FeatureCard
              icon={<IconRocket />}
              title="Pre-boarding Generator"
              description="Manager inputs SDR profile — territory, vertical, experience. Claude generates a personalized Trailhead learning path."
              step="Step 1"
              bg="bg-emerald-50"
              iconColor="text-emerald-600"
            />
            <FeatureCard
              icon={<IconBook />}
              title="Offboarding KT"
              description="Departing SDR answers structured interview questions. Claude synthesizes answers into a handoff doc stored in the KB."
              step="KB Loop"
              bg="bg-amber-50"
              iconColor="text-amber-600"
            />
            <FeatureCard
              icon={<IconMic />}
              title="Coaching Notes"
              description="Manager uploads a call recording. Whisper transcribes it. Claude generates a structured coaching note for the SDR."
              step="Step 10"
              bg="bg-purple-50"
              iconColor="text-purple-600"
            />
          </div>
        </div>
      </section>

      {/* ── KB Loop section ── */}
      <section className="bg-blue-500">
        <div className="max-w-7xl mx-auto px-6 py-20 text-center">
          <h2 className="text-3xl font-extrabold text-white mb-3">
            The KB on day 90 is smarter than day 1
          </h2>
          <p className="text-blue-100 mb-14 max-w-lg mx-auto">
            Every human-approved interaction feeds back into ChromaDB — nothing enters without sign-off.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <LoopStep icon="🙋" label="SDR asks" sub="Plain English question" />
            <div className="text-white text-2xl font-light hidden sm:block">→</div>
            <LoopStep icon="🤖" label="AI answers" sub="Cited from ChromaDB" />
            <div className="text-white text-2xl font-light hidden sm:block">→</div>
            <LoopStep icon="✅" label="Human approves" sub="Manager or SDR signs off" />
            <div className="text-white text-2xl font-light hidden sm:block">→</div>
            <LoopStep icon="🧠" label="Stored in KB" sub="Embedded → ChromaDB" />
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-6 py-10 flex items-center justify-between">
          <div>
            <div className="font-extrabold text-lg mb-1">KT Agent</div>
            <div className="text-gray-400 text-sm">The self-improving SDR onboarding system</div>
          </div>
          <div className="text-gray-400 text-sm text-right">
            <div>MGT 449 · Group 2</div>
            <div>April 2026 · UCSD</div>
          </div>
        </div>
      </footer>
    </div>
  )
}
