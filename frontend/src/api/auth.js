// encoding: utf-8
import request from './request'

export const login = (emp_no, password) =>
  request.post('/auth/login', { emp_no, password })

export const getMe = () => request.get('/auth/me')
