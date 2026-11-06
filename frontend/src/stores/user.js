// encoding: utf-8
import { defineStore } from 'pinia'
import { login as apiLogin, getMe } from '../api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null,   // { id, emp_no, name, group_name, role }
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
    isAdmin: (s) => s.user?.role === 'admin',
  },
  actions: {
    async login(empNo, password) {
      const data = await apiLogin(empNo, password)
      this.token = data.access_token
      localStorage.setItem('token', data.access_token)
      await this.fetchMe()
    },
    async fetchMe() {
      this.user = await getMe()
      return this.user
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    },
  },
})
