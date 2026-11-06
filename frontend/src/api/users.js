// encoding: utf-8
import request from './request'

// 列表（返回 {items, total, page, size, pages}）
export const listUsers = (params = {}) => request.get('/users', { params })
export const listGroups = () => request.get('/users/groups')

export const createUser = (data) => request.post('/users', data)
export const updateUser = (id, data) => request.put(`/users/${id}`, data)
export const resetPassword = (id, new_password) =>
  request.post(`/users/${id}/reset-password`, { new_password })
export const deleteUser = (id) => request.delete(`/users/${id}`)

// ★ CSV 批量导入
export const importUsers = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return request.post('/users/import', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
