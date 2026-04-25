import { NavLink, Link } from 'react-router-dom'

const NAV = [
  { to: '/tutor', label: 'AI Tutor' },
  { to: '/preboarding', label: 'Pre-boarding' },
  { to: '/offboarding', label: 'Offboarding KT' },
  { to: '/coaching', label: 'Coaching Notes' },
]

export default function AppNavbar() {
  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-8 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <div className="w-7 h-7 bg-blue-500 rounded-lg flex items-center justify-center">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1L2 4v6l5 3 5-3V4L7 1z" fill="white" />
            </svg>
          </div>
          <span className="font-bold text-gray-900 text-sm">KT Agent</span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {NAV.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                [
                  'px-4 py-1.5 text-sm font-medium rounded transition-colors',
                  isActive
                    ? 'text-blue-500 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100',
                ].join(' ')
              }
            >
              {label}
            </NavLink>
          ))}
        </div>

        {/* Dashboard */}
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            [
              'px-4 py-1.5 text-sm font-medium rounded transition-colors',
              isActive
                ? 'text-blue-500 bg-blue-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100',
            ].join(' ')
          }
        >
          Dashboard
        </NavLink>
      </div>
    </nav>
  )
}
