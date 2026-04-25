import { Routes, Route } from 'react-router-dom'
import AppNavbar from './components/AppNavbar.jsx'
import Homepage from './pages/Homepage.jsx'
import Tutor from './pages/Tutor.jsx'
import Preboarding from './pages/Preboarding.jsx'
import Offboarding from './pages/Offboarding.jsx'
import CoachingNotes from './pages/CoachingNotes.jsx'
import Dashboard from './pages/Dashboard.jsx'

function AppLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <AppNavbar />
      <main className="max-w-7xl mx-auto px-8 py-10">{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <div className="font-sans">
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/tutor" element={<AppLayout><Tutor /></AppLayout>} />
        <Route path="/preboarding" element={<AppLayout><Preboarding /></AppLayout>} />
        <Route path="/offboarding" element={<AppLayout><Offboarding /></AppLayout>} />
        <Route path="/coaching" element={<AppLayout><CoachingNotes /></AppLayout>} />
        <Route path="/dashboard" element={<AppLayout><Dashboard /></AppLayout>} />
      </Routes>
    </div>
  )
}
