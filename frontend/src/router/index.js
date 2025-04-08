import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// Views
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import BillingAgentView from '@/views/BillingAgentView.vue'
import InternationalAgentView from '@/views/InternationalAgentView.vue'
import SupervisorView from '@/views/SupervisorView.vue'
import CustomerProfile from '@/views/CustomerProfile.vue'
import NotFound from '@/views/NotFound.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/billing',
    name: 'BillingAgent',
    component: BillingAgentView,
    meta: { requiresAuth: true }
  },
  {
    path: '/international',
    name: 'InternationalAgent',
    component: InternationalAgentView,
    meta: { requiresAuth: true }
  },
  {
    path: '/supervisor',
    name: 'SupervisorAgent',
    component: SupervisorView,
    meta: { requiresAuth: true, requiresRole: 'supervisor' }
  },
  {
    path: '/customer/:id',
    name: 'CustomerProfile',
    component: CustomerProfile,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { public: true }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isPublic = to.matched.some(record => record.meta.public)
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresRole = to.meta.requiresRole
  const isAuthenticated = store.getters.isAuthenticated
  const userRole = store.getters.userRole

  // Check if the route requires authentication
  if (requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  // Check if the route requires a specific role
  if (requiresRole && userRole !== requiresRole) {
    return next('/dashboard')
  }

  // Redirect to dashboard if already logged in and trying to access login
  if (isAuthenticated && to.path === '/login') {
    return next('/dashboard')
  }

  next()
})

export default router