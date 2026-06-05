import { NavLink, Link, useNavigate, useLocation } from "react-router-dom"
import { useRole } from "../lib/roleContext"

const NAV_BY_ROLE = {
  manager: [
    { to: "/preboarding", label: "Pre-boarding" },
    { to: "/coaching", label: "Coaching Notes" },
    { to: "/certification", label: "Certification" },
    { to: "/offboarding-reviews", label: "Debrief Reviews" },
    { to: "/dashboard", label: "Dashboard" },
  ],
  trainee: [
    { to: "/tutor", label: "AI Tutor" },
    { to: "/simulation", label: "Cold Call Simulation" },
    { to: "/offboarding", label: "Onboarding Debrief" },
  ],
}

const SAFE_ALWAYS = new Set(["/", "/app"])
const DEFAULT_BY_ROLE = { manager: "/preboarding", trainee: "/tutor" }

const pillClass = ({ isActive }) =>
  `px-4 py-1.5 text-sm font-medium rounded transition-colors ${
    isActive
      ? "text-blue-500 bg-blue-50"
      : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
  }`

function RoleToggle({ role, setRole }) {
  const navigate = useNavigate()
  const location = useLocation()

  const switchTo = (target) => {
    if (target === role) return
    setRole(target)
    if (SAFE_ALWAYS.has(location.pathname)) return
    const allowed = new Set(NAV_BY_ROLE[target].map((it) => it.to))
    const matchesAllowedPrefix = [...allowed].some(
      (p) => location.pathname === p || location.pathname.startsWith(`${p}/`)
    )
    if (!matchesAllowedPrefix) {
      navigate(DEFAULT_BY_ROLE[target], { replace: true })
    }
  }

  const seg = (target, label) => (
    <button
      key={target}
      onClick={() => switchTo(target)}
      className={`px-3 py-1 text-xs font-semibold rounded-full transition-colors ${
        role === target
          ? "bg-blue-500 text-white"
          : "text-gray-600 hover:text-gray-900"
      }`}
    >
      {label}
    </button>
  )
  return (
    <div className="flex items-center gap-1 bg-gray-100 rounded-full p-0.5">
      {seg("trainee", "Trainee")}
      {seg("manager", "Manager")}
    </div>
  )
}

export default function Navbar() {
  const { role, setRole } = useRole()
  const items = NAV_BY_ROLE[role] || []
  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-7 h-7 bg-blue-500 rounded-lg flex items-center justify-center">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1L2 4v6l5 3 5-3V4L7 1z" fill="white" />
            </svg>
          </div>
          <span className="font-bold text-gray-900 text-sm">SDR KT Agent</span>
          <span className="bg-blue-500 text-white text-[10px] rounded-full px-2 py-0.5">
            MGT 449
          </span>
        </Link>

        <div className="flex items-center gap-1">
          {items.map((it) => (
            <NavLink key={it.to} to={it.to} className={pillClass}>
              {it.label}
            </NavLink>
          ))}
        </div>

        <RoleToggle role={role} setRole={setRole} />
      </div>
    </nav>
  )
}
