export default [
  {
    path: 'student',
    name: 'student',
    component: () => import('@/views/student/StudentView.vue'),
    meta: { role: 'student', title: '学生中心' },
    children: [
      {
        path: '',
        redirect: '/dashboard/student/courses'
      },
      {
        path: 'home',
        name: 'student-home',
        redirect: '/dashboard/student/my-courses'
      },
      {
        path: 'courses',
        name: 'student-courses',
        component: () => import('@/views/student/CourseSelectionView.vue'),
        meta: { title: '课程选择' }
      },
      {
        path: 'my-courses',
        name: 'student-my-courses',
        component: () => import('@/views/student/MyCoursesView.vue'),
        meta: { title: '我的课程' }
      },
      {
        path: 'courses/:id',
        name: 'student-course-detail',
        component: () => import('@/views/student/CourseDetailView.vue'),
        meta: { title: '课程详情', role: 'student' }
      },
      {
        path: 'tests/:testId',
        name: 'student-tests',
        component: () => import('@/views/student/TestTakingView.vue'),
        meta: { title: '在线测试' }
      },
      {
        path: ':courseId/questions/:lessonId',
        name: 'student-questions',
        component: () => import('@/views/student/TestTakingView.vue'),
        meta: { title: '在线测试' }
      }
    ]
  }
] 