import { signInWithPopup } from 'firebase/auth'
import { auth, googleProvider } from '../config/firebase'
import api from './api'

export const authService = {
  /** Verify access code */
  async verifyCode(code) {
    const { data } = await api.post('/auth/verify-code', { code })
    return data
  },

  /** Google Sign-In → Firebase → Backend JWT */
  async loginWithGoogle() {
    const result = await signInWithPopup(auth, googleProvider)
    const idToken = await result.user.getIdToken()
    const { data } = await api.post('/auth/login', { id_token: idToken })
    localStorage.setItem('reetik_v3_token', data.access_token)
    localStorage.setItem('reetik_v3_user', JSON.stringify(data.user))
    return data
  },

  /** Get current user */
  async getMe() {
    const { data } = await api.get('/auth/me')
    return data
  },

  /** Logout */
  logout() {
    localStorage.removeItem('reetik_v3_token')
    localStorage.removeItem('reetik_v3_user')
    auth.signOut()
  },

  /** Check if logged in */
  isAuthenticated() {
    return !!localStorage.getItem('reetik_v3_token')
  },

  /** Get stored user */
  getStoredUser() {
    const raw = localStorage.getItem('reetik_v3_user')
    return raw ? JSON.parse(raw) : null
  },
}
