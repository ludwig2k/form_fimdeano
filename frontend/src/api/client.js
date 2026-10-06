import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { encerrarSessaoExpirada } from '../router'

const client = axios.create({ baseURL: '/api' })

client.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// Token expirado/inválido em rota protegida → logoff automático. As rotas de
// login ficam de fora: lá o 401 significa usuário/senha errados.
client.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const url = error.config?.url || ''
    if (error.response?.status === 401 && !url.endsWith('/login')) {
      encerrarSessaoExpirada()
    }
    return Promise.reject(error)
  }
)

export default client
