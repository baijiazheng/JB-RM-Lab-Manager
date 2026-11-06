// encoding: utf-8
import request from './request'

// ---- 队员 ----
export const myTasks = (params = {}) => request.get('/tasks/mine', { params })
export const taskDetail = (id) => request.get(`/tasks/${id}`)
export const submitTask = (id, content) =>
  request.post(`/tasks/${id}/submit`, { content })
export const taskSubmissions = (id) => request.get(`/tasks/${id}/submissions`)
export const updateMyStatus = (id, status) =>
  request.put(`/tasks/${id}/my-status`, { status })

export const uploadFile = (submissionId, file) => {
  const fd = new FormData()
  fd.append('file', file)
  return request.post(`/tasks/submissions/${submissionId}/files`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const downloadUrl = (fileId) => `/api/tasks/files/${fileId}/download`

// ---- 管理员 ----
export const allTasks = (params = {}) => request.get('/tasks', { params })
export const createTask = (data) => request.post('/tasks', data)
export const createTasksBatch = (data) => request.post('/tasks/batch', data)
export const updateTask = (id, data) => request.put(`/tasks/${id}`, data)
export const updateTaskStatus = (id, status, reject_reason = '') =>
  request.put(`/tasks/${id}/status`, { status, reject_reason })
export const deleteTask = (id) => request.delete(`/tasks/${id}`)
export const allSubmissions = (params = {}) =>
  request.get('/tasks/admin/submissions', { params })
