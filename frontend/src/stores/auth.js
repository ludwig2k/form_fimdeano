import { defineStore } from 'pinia'

// Lê o "exp" (em segundos) do payload do JWT; o backend é quem valida a
// assinatura, aqui só precisamos saber quando a sessão vence.
function expiracaoDoToken(token) {
  try {
    const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(payload)).exp * 1000
  } catch (e) {
    return 0
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('confra_token') || '',
    role: localStorage.getItem('confra_role') || '',
  }),
  getters: {
    expiraEm: (state) => (state.token ? expiracaoDoToken(state.token) : 0),
  },
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
    sessaoValida(role) {
      return !!this.token && this.role === role && Date.now() < this.expiraEm
    },
  },
})
