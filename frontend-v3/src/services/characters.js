import api from './api'

export const characterService = {
  async list(projectId) {
    const { data } = await api.get('/characters', { params: { project_id: projectId } })
    return data
  },

  async get(id) {
    const { data } = await api.get(`/characters/${id}`)
    return data
  },

  async chat(payload) {
    const { data } = await api.post('/characters/chat', payload)
    return data
  },

  async generate(id) {
    const { data } = await api.post(`/characters/${id}/generate`)
    return data
  },

  async regenerate(id) {
    const { data } = await api.post(`/characters/${id}/regenerate`)
    return data
  },

  async update(id, payload) {
    const { data } = await api.patch(`/characters/${id}`, payload)
    return data
  },
}
