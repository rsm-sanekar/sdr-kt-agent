import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Navbar from "./components/Navbar"
import Home from "./pages/Home"
import Tutor from "./pages/Tutor"
import Dashboard from "./pages/Dashboard"
import Preboarding from "./pages/Preboarding"
import Offboarding from "./pages/Offboarding"
import OffboardingReviews from "./pages/OffboardingReviews"
import CoachingNotes from "./pages/CoachingNotes"
import Certification from "./pages/Certification"
import Simulation from "./pages/Simulation"
import { RoleProvider, useRole } from "./lib/roleContext"

function RoleHome() {
  const { role } = useRole()
  return <Navigate to={role === "trainee" ? "/tutor" : "/preboarding"} replace />
}

export default function App() {
  return (
    <RoleProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/app" element={<RoleHome />} />
          <Route path="/preboarding" element={<Preboarding />} />
          <Route path="/preboarding/:hireId" element={<Preboarding />} />
          <Route path="/tutor" element={<Tutor />} />
          <Route path="/offboarding" element={<Offboarding />} />
          <Route path="/offboarding-reviews" element={<OffboardingReviews />} />
          <Route path="/offboarding-reviews/:sessionId" element={<OffboardingReviews />} />
          <Route path="/coaching" element={<CoachingNotes />} />
          <Route path="/certification" element={<Certification />} />
          <Route path="/certification/:sdrId" element={<Certification />} />
          <Route path="/simulation" element={<Simulation />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </RoleProvider>
  )
}
