import api from './api'

export const projectService = {
  async list() {
    const { data } = await api.get('/projects')
    return data.projects ?? data
  },

  async get(id) {
    const { data } = await api.get(`/projects/${id}`)
    return data
  },

  async create(payload) {
    const { data } = await api.post('/projects', payload)
    return data
  },

  async update(id, payload) {
    const { data } = await api.patch(`/projects/${id}`, payload)
    return data
  },

  async remove(id) {
    await api.delete(`/projects/${id}`)
  },
}
