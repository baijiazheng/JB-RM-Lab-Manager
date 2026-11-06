// encoding: utf-8
import request from './request'

// 队员
export const myTasks = () => request.get('/tasks/mine')
export const taskDetail = (id) => request.get(`/tasks/${id}`)
export const submitTask = (id, content) =>
  request.post(`/tasks/${id}/submit`, { content })
export const taskSubmissions = (id) => request.get(`/tasks/${id}/submissions`)
export const uploadFile = (submissionId, file) => {
  const fd = new FormData()
  fd.append('file', file)
  return request.post(`/tasks/submissions/${submissionId}/files`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const downloadUrl = (fileId) => `/api/tasks/files/${fileId}/download`

// 管理员
export const allTasks = () => request.get('/tasks')
export const createTask = (data) => request.post('/tasks', data)
export const updateTaskStatus = (id, status, reject_reason = '') =>
  request.put(`/tasks/${id}/status`, { status, reject_reason })
export const deleteTask = (id) => request.delete(`/tasks/${id}`)
export const allSubmissions = () => request.get('/tasks/admin/submissions')
