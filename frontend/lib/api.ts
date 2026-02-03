// API Client for Flask Backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

interface ApiRequestOptions {
  method?: string
  headers?: Record<string, string>
  body?: any
}

async function apiRequest<T>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const config: RequestInit = {
    method: options.method || 'GET',
    headers,
  }

  if (options.body) {
    config.body = JSON.stringify(options.body)
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }))
    throw new ApiError(response.status, error.error || 'Request failed')
  }

  return response.json()
}

// Authentication
export const auth = {
  login: (username: string, password: string) =>
    apiRequest<{ token: string; username: string; role: string }>('/api/auth/login', {
      method: 'POST',
      body: { username, password },
    }),

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  },

  getToken: () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token')
    }
    return null
  },

  setToken: (token: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token)
    }
  },

  getCurrentUser: () => {
    if (typeof window !== 'undefined') {
      const user = localStorage.getItem('user')
      return user ? JSON.parse(user) : null
    }
    return null
  },

  setCurrentUser: (user: any) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user))
    }
  },
}

// Students
export const students = {
  getAll: () => apiRequest<{ count: number; students: any[] }>('/api/students/students'),
  getById: (id: string) => apiRequest(`/api/students/students/${id}`),
  create: (data: any) => apiRequest('/api/students/students', { method: 'POST', body: data }),
  update: (id: string, data: any) =>
    apiRequest(`/api/students/students/${id}`, { method: 'PUT', body: data }),
  delete: (id: string) => apiRequest(`/api/students/students/${id}`, { method: 'DELETE' }),
}

// Courses
export const courses = {
  getAll: () => apiRequest<{ count: number; courses: any[] }>('/api/courses/courses'),
  getById: (id: string) => apiRequest(`/api/courses/courses/${id}`),
  create: (data: any) => apiRequest('/api/courses/courses', { method: 'POST', body: data }),
  update: (id: string, data: any) =>
    apiRequest(`/api/courses/courses/${id}`, { method: 'PUT', body: data }),
  delete: (id: string) => apiRequest(`/api/courses/courses/${id}`, { method: 'DELETE' }),
}

// Attendance
export const attendance = {
  getAll: () => apiRequest<{ count: number; records: any[] }>('/api/attendance/attendance'),
  getByStudent: (studentId: string) =>
    apiRequest(`/api/attendance/attendance/student/${studentId}`),
  getByCourse: (courseId: string) => apiRequest(`/api/attendance/attendance/course/${courseId}`),
  record: (data: any) =>
    apiRequest('/api/attendance/attendance', { method: 'POST', body: data }),
}

// Enrollments
export const enrollments = {
  getAll: () => apiRequest<any[]>('/api/enrollments'),
  enroll: (courseId: string, studentId: string) =>
    apiRequest(`/api/courses/${courseId}/enroll`, {
      method: 'POST',
      body: { student_id: studentId },
    }),
  unenroll: (courseId: string, studentId: string) =>
    apiRequest(`/api/courses/${courseId}/unenroll`, {
      method: 'POST',
      body: { student_id: studentId },
    }),
}

// Health Check
export const health = {
  check: () => apiRequest('/health'),
  services: () => apiRequest('/api/services'),
}

export { ApiError }
