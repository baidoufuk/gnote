import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import { useAuth } from '@/composables/useAuth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const { checkAuth } = useAuth()
  const isAuthenticated = checkAuth()

  // 如果路由需要认证
  if (to.meta.requiresAuth && !isAuthenticated) {
    // 未登录，跳转到登录页
    next({ name: 'Login' })
  } else if (to.name === 'Login' && isAuthenticated) {
    // 已登录，访问登录页时跳转到首页
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
