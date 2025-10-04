import api from './client'

const journal = {
  createEntry: ({ content, tags = [], user_mood = null, is_private = true }) =>
    api.post('/journal/entries', { content, tags, user_mood, is_private }),

  listEntries: ({ q = null, limit = 50 } = {}) =>
    api.get(`/journal/entries${q ? `?q=${encodeURIComponent(q)}&limit=${limit}` : `?limit=${limit}`}`),

  getEntry: (id) => api.get(`/journal/entries/${id}`),

  deleteEntry: (id) => api.delete(`/journal/entries/${id}`),

  getSummary: (days = 7) => api.get(`/journal/summary?days=${days}`)
}

export default journal
