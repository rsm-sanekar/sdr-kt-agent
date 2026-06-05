import { createContext, useContext, useState } from "react"

const STORAGE_KEY = "kt-agent-role"
const VALID = new Set(["trainee", "manager"])

const RoleContext = createContext({ role: "manager", setRole: () => {} })

function readInitial() {
  if (typeof window === "undefined") return "manager"
  const stored = window.localStorage.getItem(STORAGE_KEY)
  return VALID.has(stored) ? stored : "manager"
}

export function RoleProvider({ children }) {
  const [role, setRoleState] = useState(readInitial)

  const setRole = (next) => {
    if (!VALID.has(next)) return
    setRoleState(next)
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, next)
    }
  }

  return (
    <RoleContext.Provider value={{ role, setRole }}>
      {children}
    </RoleContext.Provider>
  )
}

export function useRole() {
  return useContext(RoleContext)
}
