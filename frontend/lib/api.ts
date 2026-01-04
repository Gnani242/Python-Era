import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth APIs
export const authAPI = {
  register: async (username: string, email: string, password: string) => {
    const response = await api.post('/api/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  },

  login: async (username: string, password: string) => {
    const response = await api.post('/api/auth/login', {
      username,
      password,
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/user/me');
    return response.data;
  },
};

// Lesson APIs
export const lessonAPI = {
  getTodayLesson: async () => {
    const response = await api.get('/api/lessons/today');
    return response.data;
  },
};

// Code Execution API
export const executeAPI = {
  executeCode: async (code: string) => {
    const response = await api.post('/api/execute', { code });
    return response.data;
  },
};

// Progress APIs
export const progressAPI = {
  completeTask: async () => {
    const response = await api.post('/api/progress/complete');
    return response.data;
  },

  updateTime: async (studyTime: number, practiceTime: number) => {
    const response = await api.post('/api/progress/time', {
      study_time: studyTime,
      practice_time: practiceTime,
    });
    return response.data;
  },

  getDashboard: async () => {
    const response = await api.get('/api/dashboard');
    return response.data;
  },
};

// Admin APIs
export const adminAPI = {
  getLessons: async () => {
    const response = await api.get('/api/admin/lessons');
    return response.data;
  },

  createLesson: async (lesson: {
    day_number: number;
    topic: string;
    content: string;
    question: string;
    solution: string;
  }) => {
    const response = await api.post('/api/admin/lessons', lesson);
    return response.data;
  },

  updateLesson: async (lessonId: number, lesson: {
    day_number: number;
    topic: string;
    content: string;
    question: string;
    solution: string;
  }) => {
    const response = await api.put(`/api/admin/lessons/${lessonId}`, lesson);
    return response.data;
  },

  deleteLesson: async (lessonId: number) => {
    const response = await api.delete(`/api/admin/lessons/${lessonId}`);
    return response.data;
  },
};

export default api;

