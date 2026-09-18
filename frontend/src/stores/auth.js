import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('confra_token') || '',
    role: localStorage.getItem('confra_role') || '',
  }),
  actions: {
    setSession(token, role) {
      this.token = token
      this.role = role
      localStorage.setItem('confra_token', token)
      localStorage.setItem('confra_role', role)
    },
    logout() {
      this.token = ''
      this.role = ''
      localStorage.removeItem('confra_token')
      localStorage.removeItem('confra_role')
    },
  },
})
