import api from './api'
import { API } from '../config/api'

export const videoService = {
  async list(projectId) {
    const params = projectId ? { project_id: projectId } : {}
    const { data } = await api.get('/videos', { params })
    return data
  },

  async get(id) {
    const { data } = await api.get(`/videos/${id}`)
    return data
  },

  async generate(payload) {
    const { data } = await api.post('/videos/generate', payload)
    return data
  },

  async getStatus(id) {
    const { data } = await api.get(`/videos/${id}/status`)
    return data
  },

  async getStreamUrl(id) {
    const { data } = await api.get(`/videos/${id}/stream`)
    return data
  },

  async getDownloadUrl(id) {
    const { data } = await api.get(`/videos/${id}/download`)
    return data
  },

  async remove(id) {
    await api.delete(`/videos/${id}`)
  },

  async retry(id) {
    const { data } = await api.post(`/videos/${id}/retry`)
    return data
  },

  /** WebSocket for real-time video status */
  connectWs(videoId, onMessage) {
    if (!videoId || videoId === 'null') return { onclose: null, onerror: null, close: () => {} }
    const token = localStorage.getItem('reetik_v3_token')
    const wsUrl = `${API.WS_VIDEO(videoId)}?token=${token}`
    const ws = new WebSocket(wsUrl)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      onMessage(data)
    }

    ws.onerror = () => ws.close()

    return ws
  },
}
