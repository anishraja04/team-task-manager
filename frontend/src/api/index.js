import api from './client'

// all the api functions related to authentication
export const authApi = {
  login: (email, password) => api.post('/auth/login/', { email, password }),
  register: (payload) => api.post('/auth/register/', payload),
  me: () => api.get('/auth/me/'),
  searchUsers: (q) => api.get('/auth/users/', { params: { q } }),
}

// all the api functions for projects and team members
export const projectsApi = {
  list: () => api.get('/projects/'),
  get: (id) => api.get(`/projects/${id}/`),
  create: (data) => api.post('/projects/', data),
  update: (id, data) => api.patch(`/projects/${id}/`, data),
  remove: (id) => api.delete(`/projects/${id}/`),
  members: (id) => api.get(`/projects/${id}/members/`),
  addMember: (id, data) => api.post(`/projects/${id}/members/`, data),
  updateMember: (id, mpk, data) => api.patch(`/projects/${id}/members/${mpk}/`, data),
  removeMember: (id, mpk) => api.delete(`/projects/${id}/members/${mpk}/`),
}

// all the api functions for tasks, comments and the dashboard
export const tasksApi = {
  list: (params) => api.get('/tasks/', { params }),
  get: (id) => api.get(`/tasks/${id}/`),
  create: (data) => api.post('/tasks/', data),
  update: (id, data) => api.patch(`/tasks/${id}/`, data),
  remove: (id) => api.delete(`/tasks/${id}/`),
  comments: (id) => api.get(`/tasks/${id}/comments/`),
  addComment: (id, body) => api.post(`/tasks/${id}/comments/`, { body }),
  dashboard: () => api.get('/tasks/dashboard/'),
}
