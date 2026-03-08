import axios from 'axios'
import { API } from '../config/api'

const api = axios.create({
  baseURL: API.BASE,
  headers: { 'Content-Type': 'application/json' },
})

// Interceptor: attach JWT from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('reetik_v3_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor: redirect to login on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('reetik_v3_token')
      localStorage.removeItem('reetik_v3_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
