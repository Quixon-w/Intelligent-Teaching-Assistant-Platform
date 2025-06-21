import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/login/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/register/RegisterView.vue'),
    },
    {
      path:'/dashboard',
      name:'dashboard',
      component: () => import('../views/dashboard/DashboardView.vue'),
      children:[
        {
          path: 'main',
          name: 'main',
          component: () => import('../views/dashboard/MainView.vue'),
        },
        {
          path: '',
          name: 'inToMain',
          redirect: 'dashboard/main',
        },
        {
          path: 'about',
          name: 'about',
          // route level code-splitting
          // this generates a separate chunk (About.[hash].js) for this route
          // which is lazy-loaded when the route is visited.
          component: () => import('../views/AboutView.vue'),
        },
        {
          path: 'user/central',
          name: 'user/central',
          component: () => import('../views/user/UserCentralView.vue'),
        },
        {
          path: 'teacher/class',
          name: 'teacher/class',
          component: () => import('../views/role/teacher/TeacherClassView.vue'),
        },
        {
          path: 'teacher/class/:id',
          name: 'teacher/class/id',
          component: () => import('../views/role/teacher/TeacherClassDetailView.vue'),
        },
        {
          path: 'student/class',
          name: 'student/class',
          component: () => import('../views/role/student/StudentClassView.vue'),
        },
        {
          path: 'student/class/:id',
          name: 'student/class/id',
          component: () => import('../views/role/student/StudentClassDetailView.vue'),
        },
      ]
    }
  ],
})
router.beforeEach((to, from, next) => {
  if (to.name !== 'login' && to.name!=='register' &&!sessionStorage.getItem('token')) next({ name: 'login' })
  else next()
})
export default router
