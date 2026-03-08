import api from './api'

export const tiktokService = {
  async suggestProfile(payload) {
    const { data } = await api.post('/tiktok/suggest-profile', payload)
    return data
  },

  async suggestHashtags(payload) {
    const { data } = await api.post('/tiktok/suggest-hashtags', payload)
    return data
  },

  async suggestTitle(payload) {
    const { data } = await api.post('/tiktok/suggest-title', payload)
    return data
  },
}
