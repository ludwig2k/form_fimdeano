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

router.beforeEach((to) => {
  const requiredRole = to.meta.requiresRole
  if (!requiredRole) return true

  const auth = useAuthStore()
  if (auth.role !== requiredRole || !auth.token) {
    return { name: requiredRole === 'admin' ? 'admin-login' : 'checkin-login' }
  }
  return true
})

export default router
