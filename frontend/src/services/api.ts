import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token && token !== 'undefined' && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (data: any) => api.post('/auth/login', data),
  register: (data: any) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};

export const journeyApi = {
  create: (data: any) => api.post('/journeys', data),
  list: () => api.get('/journeys'),
  get: (id: string) => api.get(`/journeys/${id}`),
  update: (id: string, data: any) => api.put(`/journeys/${id}`, data),
  delete: (id: string) => api.delete(`/journeys/${id}`),
};

export const nodeApi = {
  create: (journeyId: string, data: any) => api.post(`/journeys/${journeyId}/nodes`, data),
  update: (journeyId: string, nodeId: string, data: any) => api.put(`/journeys/${journeyId}/nodes/${nodeId}`, data),
  delete: (journeyId: string, nodeId: string) => api.delete(`/journeys/${journeyId}/nodes/${nodeId}`),
};

export const dependencyApi = {
  create: (journeyId: string, data: any) => api.post(`/journeys/${journeyId}/dependencies`, data),
  delete: (journeyId: string, depId: string) => api.delete(`/journeys/${journeyId}/dependencies/${depId}`),
};

export const digitalTwinApi = {
  get: (journeyId: string) => api.get(`/journeys/${journeyId}/digital-twin`),
};

export const resilienceApi = {
  get: (journeyId: string) => api.get(`/journeys/${journeyId}/resilience-score`),
};

export const disruptionApi = {
  create: (data: any) => api.post('/disruptions', data),
  list: () => api.get('/disruptions'),
  get: (id: string) => api.get(`/disruptions/${id}`),
};

export const recoveryApi = {
  getOptions: (journeyId: string) => api.post(`/recovery/journeys/${journeyId}/recovery-options`),
  getDetail: (id: string) => api.get(`/recovery/${id}`),
  approve: (id: string) => api.post(`/recovery/${id}/approve`),
  execute: (id: string) => api.post(`/recovery/${id}/execute`),
  reject: (id: string) => api.post(`/recovery/${id}/reject`),
};

export const simulatorApi = {
  simulate: (journeyId: string, data: any) => api.post(`/simulator/journeys/${journeyId}/simulate`, data),
  apply: (id: string) => api.post(`/simulator/simulations/${id}/apply`),
  discard: (id: string) => api.post(`/simulator/simulations/${id}/discard`),
};

export const guardianApi = {
  chat: (data: any) => api.post('/guardian/chat', data),
};

export const notificationApi = {
  list: () => api.get('/notifications'),
  markRead: (id: string) => api.put(`/notifications/${id}/read`),
};

export const analyticsApi = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getRecovery: () => api.get('/analytics/recovery'),
};

export const preferencesApi = {
  get: () => api.get('/preferences'),
  update: (data: any) => api.put('/preferences', data),
};

export const adminApi = {
  getUsers: () => api.get('/admin/users'),
  updateRole: (id: string, role: string) => api.put(`/admin/users/${id}/role`, { role }),
  getAuditLogs: () => api.get('/admin/audit-logs'),
  getSystemHealth: () => api.get('/admin/system-health'),
};

export const demoApi = {
  loadDemoJourney: () => api.post('/demo/load'),
  simulateDelay: () => api.post('/demo/simulate-delay'),
  simulateCancellation: () => api.post('/demo/simulate-cancellation'),
};

export default api;
