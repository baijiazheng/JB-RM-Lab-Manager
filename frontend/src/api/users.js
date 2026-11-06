// encoding: utf-8
import request from './request'

export const listUsers = () => request.get('/users')
export const createUser = (data) => request.post('/users', data)
export const updateUser = (id, data) => request.put(`/users/${id}`, data)
export const resetPassword = (id, new_password) =>
  request.post(`/users/${id}/reset-password`, { new_password })
export const deleteUser = (id) => request.delete(`/users/${id}`)
