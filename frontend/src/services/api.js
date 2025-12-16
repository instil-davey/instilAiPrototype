import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login', { username, password }),
  getCurrentUser: () => api.get('/auth/me'),
}

// Constituents API
export const constituentsAPI = {
  list: (params) => api.get('/constituents', { params }),
  get: (id) => api.get(`/constituents/${id}`),
  create: (data) => api.post('/constituents', data),
  update: (id, data) => api.put(`/constituents/${id}`, data),
  delete: (id) => api.delete(`/constituents/${id}`),
  getSummary: (id) => api.get(`/constituents/${id}/summary`),
  getBriefing: (id, segments) =>
    api.get(`/constituents/${id}/briefing`, {
      params: segments ? { segments: segments.join(',') } : undefined,
    }),
  getSegmentSuggestion: (id) =>
    api.get(`/segments/constituents/${id}/suggestion`),
}

export const segmentsAPI = {
  getSuggestions: (params) => api.get('/segments/suggestions', { params }),
  getDefinitions: () => api.get('/segments/definitions'),
}

// Contributions API
export const contributionsAPI = {
  list: (params) => api.get('/contributions', { params }),
  get: (id) => api.get(`/contributions/${id}`),
  create: (data) => api.post('/contributions', data),
  update: (id, data) => api.put(`/contributions/${id}`, data),
  delete: (id) => api.delete(`/contributions/${id}`),
  getByConstituent: (constituentId) =>
    api.get('/contributions', { params: { constituent_id: constituentId } }),
  getByCampaign: () => api.get('/contributions/stats/by-campaign'),
}

// Interactions API
export const interactionsAPI = {
  list: (params) => api.get('/interactions', { params }),
  get: (id) => api.get(`/interactions/${id}`),
  create: (data) => api.post('/interactions', data),
  update: (id, data) => api.put(`/interactions/${id}`, data),
  delete: (id) => api.delete(`/interactions/${id}`),
}

// Opportunities API
export const opportunitiesAPI = {
  list: (params) => api.get('/opportunities', { params }),
  get: (id) => api.get(`/opportunities/${id}`),
  create: (data) => api.post('/opportunities', data),
  update: (id, data) => api.put(`/opportunities/${id}`, data),
  delete: (id) => api.delete(`/opportunities/${id}`),
  getPipelineStats: () => api.get('/opportunities/stats/pipeline'),
}

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getRecentActivity: () => api.get('/dashboard/recent-activity'),
}

export const tasksAPI = {
  create: (data) => api.post('/tasks', data),
  list: (params) => api.get('/tasks', { params }),
  complete: (id) => api.post(`/tasks/${id}/complete`),
}

export const voiceAPI = {
  speak: (data) => api.post('/voice/speak', data),
  agent: (data) => api.post('/voice/agent', data),
}

export default api
