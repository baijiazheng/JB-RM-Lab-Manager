// encoding: utf-8
/**
 * ★ 统一 axios 封装
 * 所有请求都走这里，业务代码只用 request.get/post，不关心 token
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 20000,
})

// 请求拦截：自动带 token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截：★ 拆掉 { code, msg, data } 外壳，业务代码直接拿 data
request.interceptors.response.use(
  (resp) => {
    const body = resp.data
    if (body && body.code === 0) return body.data
    ElMessage.error(body?.msg || '请求失败')
    return Promise.reject(new Error(body?.msg || '请求失败'))
  },
  (error) => {
    const status = error.response?.status
    const msg = error.response?.data?.msg || error.message
    if (status === 401) {
      localStorage.removeItem('token')
      ElMessage.error('登录已过期，请重新登录')
      // 只在非登录页跳转
      if (!location.hash.includes('/login')) location.hash = '#/login'
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

export default request
