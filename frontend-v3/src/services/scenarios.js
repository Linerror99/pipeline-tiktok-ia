import api from './api'

export const scenarioService = {
  async list(projectId) {
    const { data } = await api.get('/scenarios', { params: { project_id: projectId } })
    return data
  },

  async get(id) {
    const { data } = await api.get(`/scenarios/${id}`)
    return data
  },

  async chat(payload) {
    const { data } = await api.post('/scenarios/chat', payload)
    return data
  },

  async upload(id, file) {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post(`/scenarios/${id}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  async validate(id, payload) {
    const { data } = await api.post(`/scenarios/${id}/validate`, payload)
    return data
  },

  async remove(id) {
    await api.delete(`/scenarios/${id}`)
  },
}
