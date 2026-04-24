const API_BASE = import.meta.env.VITE_API_URL || '/api/v3'

// WebSocket: même host/port que l'API, remplacer http(s) par ws(s)
const _apiOrigin = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace(/^http/, 'ws')
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v3`

export const API = {
  BASE: API_BASE,
  AUTH: {
    VERIFY_CODE: `${API_BASE}/auth/verify-code`,
    LOGIN: `${API_BASE}/auth/login`,
    ME: `${API_BASE}/auth/me`,
  },
  PROJECTS: `${API_BASE}/projects`,
  CHARACTERS: `${API_BASE}/characters`,
  SCENARIOS: `${API_BASE}/scenarios`,
  VIDEOS: `${API_BASE}/videos`,
  TIKTOK: `${API_BASE}/tiktok`,
  // Route backend: /api/v3/videos/{video_id}/ws
  WS_VIDEO: (videoId) => `${_apiOrigin}/videos/${videoId}/ws`,
}

export const VALID_DURATIONS = [8, 15, 22, 29, 36, 43, 50, 57]

export const VIDEO_STATUS = {
  PENDING: 'pending',
  GENERATING: 'generating',
  EXTENDING: 'extending',
  COMPLETED: 'completed',
  FAILED: 'failed',
}

export const PROJECT_STEPS = {
  CHARACTERS: 'characters',
  SCENARIO: 'scenario',
  VIDEOS: 'videos',
  TIKTOK: 'tiktok',
}
