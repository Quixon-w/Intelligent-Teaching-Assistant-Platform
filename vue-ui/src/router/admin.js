export default [
  {
    path: 'admin',
    name: 'admin',
    component: () => import('@/views/admin/AdminView.vue'),
    meta: { role: 'admin', title: '管理员中心' },
    children: [
      {
        path: '',
        redirect: '/dashboard/admin/users'
      },
      {
        path: 'home',
        name: 'admin-home',
        component: () => import('@/views/role/admin/AdminDashboardView.vue'),
        meta: { title: '系统概览', role: 'admin' }
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/views/admin/UserManagementView.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'courses',
        name: 'admin-courses',
        component: () => import('@/views/admin/CourseMonitorView.vue'),
        meta: { title: '课程监控' }
      }
    ]
  }
] 