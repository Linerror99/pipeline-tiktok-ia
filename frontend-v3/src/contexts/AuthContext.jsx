import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authService } from '../services/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(authService.getStoredUser)
  const [loading, setLoading] = useState(true)
  const [codeVerified, setCodeVerified] = useState(
    () => sessionStorage.getItem('reetik_v3_code_ok') === '1'
  )

  useEffect(() => {
    if (authService.isAuthenticated()) {
      authService.getMe()
        .then((u) => setUser(u))
        .catch(() => authService.logout())
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const verifyCode = useCallback(async (code) => {
    await authService.verifyCode(code)
    sessionStorage.setItem('reetik_v3_code_ok', '1')
    setCodeVerified(true)
  }, [])

  const login = useCallback(async () => {
    const { user: u } = await authService.loginWithGoogle()
    setUser(u)
    return u
  }, [])

  const logout = useCallback(() => {
    authService.logout()
    setUser(null)
    sessionStorage.removeItem('reetik_v3_code_ok')
    setCodeVerified(false)
  }, [])

  return (
    <AuthContext.Provider
      value={{ user, loading, codeVerified, verifyCode, login, logout, isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
