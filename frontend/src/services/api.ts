import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://172.168.1.95:13066/api';

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor to add auth token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('arsa_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('arsa_token');
      localStorage.removeItem('arsa_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ────────────────────────────────────────
export const authAPI = {
  register: (data: any) => api.post('/auth/register/', data),
  login: (data: { username: string; password: string }) => api.post('/auth/login/', data),
  getMe: () => api.get('/auth/me/'),
  updateMe: (data: any) => api.patch('/auth/me/', data),
};

// ── Projects ────────────────────────────────────
export const projectAPI = {
  list: (params?: any) => api.get('/projects/', { params }),
  create: (data: any) => api.post('/projects/', data),
  get: (id: string) => api.get(`/projects/${id}/`),
  update: (id: string, data: any) => api.patch(`/projects/${id}/`, data),
  delete: (id: string) => api.delete(`/projects/${id}/`),
  addCollaborator: (id: string, data: any) => api.post(`/projects/${id}/collaborators/`, data),
};

// ── Papers ──────────────────────────────────────
export const paperAPI = {
  list: (params?: any) => api.get('/papers/', { params }),
  upload: (formData: FormData) =>
    api.post('/papers/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  get: (id: string) => api.get(`/papers/${id}/`),
  delete: (id: string) => api.delete(`/papers/${id}/`),
  getChunks: (id: string) => api.get(`/papers/${id}/chunks/`),
  getSummary: (id: string) => api.post(`/papers/${id}/summary/`),
  getCitations: (id: string, style?: string) =>
    api.get(`/papers/${id}/citations/`, { params: { style } }),
};

// ── Conversations ───────────────────────────────
export const conversationAPI = {
  list: (params?: any) => api.get('/conversations/', { params }),
  create: (data: any) => api.post('/conversations/', data),
  get: (id: string) => api.get(`/conversations/${id}/`),
  update: (id: string, data: any) => api.patch(`/conversations/${id}/`, data),
  delete: (id: string) => api.delete(`/conversations/${id}/`),
};

// ── RAG Query ───────────────────────────────────
export const queryAPI = {
  ask: (data: {
    question: string;
    project_id: string;
    conversation_id?: string;
    run_evaluation?: boolean;
  }) => api.post('/query/', data),
  history: (params?: any) => api.get('/query/history/', { params }),
  evaluate: (queryId: string, evalTypes?: string[]) =>
    api.post(`/query/${queryId}/evaluate/`, { eval_types: evalTypes }),
};

// ── Synthesis Reports ───────────────────────────
export const reportAPI = {
  list: (params?: any) => api.get('/reports/', { params }),
  generate: (data: { project_id: string; report_type: string; title?: string }) =>
    api.post('/reports/generate/', data),
  get: (id: string) => api.get(`/reports/${id}/`),
  delete: (id: string) => api.delete(`/reports/${id}/`),
};

// ── Agents ──────────────────────────────────────
export const agentAPI = {
  list: () => api.get('/agents/'),
  logs: (params?: any) => api.get('/agents/logs/', { params }),
  interactions: (params?: any) => api.get('/agents/interactions/', { params }),
};

// ── API Keys ────────────────────────────────────
export const apiKeyAPI = {
  list: () => api.get('/settings/api-keys/'),
  create: (data: any) => api.post('/settings/api-keys/', data),
  delete: (id: string) => api.delete(`/settings/api-keys/${id}/`),
};

// ── Exports ─────────────────────────────────────
export const exportAPI = {
  list: () => api.get('/exports/'),
  create: (data: any) => api.post('/exports/', data),
  get: (id: string) => api.get(`/exports/${id}/`),
};

// ── Annotations & Bookmarks ────────────────────
export const annotationAPI = {
  list: (params?: any) => api.get('/annotations/', { params }),
  create: (data: any) => api.post('/annotations/', data),
  update: (id: string, data: any) => api.patch(`/annotations/${id}/`, data),
  delete: (id: string) => api.delete(`/annotations/${id}/`),
};

export const bookmarkAPI = {
  list: () => api.get('/bookmarks/'),
  create: (data: any) => api.post('/bookmarks/', data),
  delete: (id: string) => api.delete(`/bookmarks/${id}/`),
};

// ── Analytics ───────────────────────────────────
export const analyticsAPI = {
  dashboard: () => api.get('/analytics/dashboard/'),
  usage: () => api.get('/analytics/usage/'),
};

// ── Health ──────────────────────────────────────
export const healthAPI = {
  check: () => api.get('/health/'),
};

export default api;
