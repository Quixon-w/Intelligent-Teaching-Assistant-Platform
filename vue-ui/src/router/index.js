import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 导入路由模块
import authRoutes from './auth'
import adminRoutes from './admin'
import teacherRoutes from './teacher'
import studentRoutes from './student'

const routes = [
  // 重定向根路径到登录页
    {
    path: '/',
    redirect: '/login'
  },
  
  // 认证路由
  ...authRoutes,
  
  // 主应用路由
    {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/dashboard/DashboardView.vue'),
    meta: { requiresAuth: true },
    children: [
      // 首页
        {
          path: '',
        redirect: '/dashboard/home'
        },
        {
        path: 'home',
        name: 'home',
        component: () => import('@/views/dashboard/HomeView.vue'),
        meta: { title: '首页'}
        },
        {
        path: 'main',
        name: 'main',
        component: () => import('@/views/dashboard/MainView.vue'),
        meta: { title: '项目介绍'}
        },
        {
        path: 'find-courses',
        name: 'find-courses',
        component: () => import('@/views/dashboard/FindCoursesView.vue'),
        meta: { title: '课程查找'}
        },
        {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/dashboard/ProfileView.vue'),
        meta: { title: '个人信息' }
      },
      
      // 管理员路由
      ...adminRoutes,
      
      // 教师路由
      ...teacherRoutes,
      
      // 学生路由
      ...studentRoutes,
      
      // 通用功能路由
            {
        path: 'ai-assistant',
        name: 'ai-assistant',
        component: () => import('@/components/ai/AIAssistant.vue'),
        meta: { title: '智能助手' }
            }
          ]
        },
  
  // 404页面
        {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/dashboard/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 智能教学辅助平台`
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // 检查角色权限
  if (to.meta.role !== undefined && authStore.userRole !== to.meta.role) {
    next('/dashboard/home')
    return
  }
  
  // 已登录用户访问登录页，重定向到首页
  if (to.name === 'login' && authStore.isAuthenticated) {
    next('/dashboard/home')
    return
  }
  
  next()
})

export default router
