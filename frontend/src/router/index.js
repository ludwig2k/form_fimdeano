import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue') },
  { path: '/sucesso/:id', name: 'sucesso', component: () => import('../views/Sucesso.vue') },
  { path: '/reenvio/:token', name: 'reenvio', component: () => import('../views/Reenvio.vue') },
  { path: '/admin/login', name: 'admin-login', component: () => import('../views/AdminLogin.vue') },
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('../views/AdminDashboard.vue'),
    meta: { requiresRole: 'admin' },
  },
  { path: '/checkin/login', name: 'checkin-login', component: () => import('../views/CheckinLogin.vue') },
  {
    path: '/checkin',
    name: 'checkin-scanner',
    component: () => import('../views/CheckinScanner.vue'),
    meta: { requiresRole: 'checkin' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const LOGIN_POR_ROLE = { admin: 'admin-login', checkin: 'checkin-login' }

// Desloga e manda para o login certo, com aviso de sessão expirada.
export function encerrarSessaoExpirada() {
  const auth = useAuthStore()
  const role = router.currentRoute.value.meta.requiresRole || auth.role
  auth.logout()
  if (LOGIN_POR_ROLE[role]) {
    router.replace({ name: LOGIN_POR_ROLE[role], query: { expirada: '1' } })
  }
}

router.beforeEach((to) => {
  const requiredRole = to.meta.requiresRole
  if (!requiredRole) return true

  const auth = useAuthStore()
  if (!auth.sessaoValida(requiredRole)) {
    const expirou = !!auth.token
    auth.logout()
    return { name: LOGIN_POR_ROLE[requiredRole], query: expirou ? { expirada: '1' } : {} }
  }
  return true
})

// Logoff automático: agenda para o instante em que o token vence e também
// confere ao voltar para a aba (timers de abas em segundo plano atrasam).
let timerExpiracao = null
function agendarExpiracao() {
  clearTimeout(timerExpiracao)
  const role = router.currentRoute.value.meta.requiresRole
  if (!role) return
  const auth = useAuthStore()
  if (!auth.sessaoValida(role)) {
    encerrarSessaoExpirada()
    return
  }
  timerExpiracao = setTimeout(agendarExpiracao, Math.min(auth.expiraEm - Date.now() + 1000, 2 ** 31 - 1))
}

router.afterEach(agendarExpiracao)
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') agendarExpiracao()
})

export default router
