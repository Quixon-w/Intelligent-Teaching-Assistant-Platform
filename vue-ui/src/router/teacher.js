export default [
  {
    path: 'teacher',
    name: 'teacher',
    component: () => import('@/views/teacher/TeacherView.vue'),
    meta: { role: 'teacher', title: '教师中心' },
    children: [
      {
        path: '',
        redirect: '/dashboard/teacher/courses'
      },
      {
        path: 'home',
        name: 'teacher-home',
        component: () => import('@/views/teacher/AllCoursesGalleryView.vue'),
        meta: { title: '所有课程', role: 'teacher' }
      },
      {
        path: 'courses',
        name: 'teacher-courses',
        component: () => import('@/views/teacher/CourseManagementView.vue'),
        meta: { title: '课程管理', role: 'teacher' }
      },
      {
        path: 'courses/:id',
        name: 'teacher-course-detail',
        component: () => import('@/views/teacher/CourseDetailView.vue'),
        meta: { title: '课程详情', role: 'teacher' }
      },
      {
        path: 'lessons/:courseId',
        name: 'teacher-lessons',
        component: () => import('@/views/teacher/LessonManagementView.vue'),
        meta: { title: '课时管理', role: 'teacher' }
      },
      {
        path: 'tests/:lessonId',
        name: 'teacher-tests',
        component: () => import('@/views/teacher/TestManagementView.vue'),
        meta: { title: '测试管理', role: 'teacher' }
      },
      {
        path: 'questions',
        name: 'teacher-questions',
        component: () => import('@/views/teacher/QuestionBankView.vue'),
        meta: { title: '题库管理', role: 'teacher' }
      }
    ]
  }
] 