import { createRouter, createWebHistory } from 'vue-router'
import RouterReplaceComp from '@/utils/RouteReplaceSelf.js'

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
          path: 'findcourses',
          name: 'findcourses',
          component: () => import('../views/dashboard/FindCoursesView.vue'),
        },
        {
          path: 'user/central',
          name: 'user/central',
          component: () => import('../views/user/UserCentralView.vue'),
        },
        {
          path: 'aitalk/:sessionId',
          name: 'aitalk',
          component: () => import('../views/dashboard/AITalkView.vue'),
        },
        {
          path: 'admin',
          name: 'admin',
          component: RouterReplaceComp(() => import('../views/role/admin/AdminDashboardView.vue')),
          children: [
            {
              path: 'class',
              name: 'adminClass',
              component: () => import('../views/role/admin/AdminClassView.vue'),
            },
            {
              path: 'users',
              name: 'adminUsers',
              component: () => import('../views/role/admin/AdminUsersView.vue'),
            },
          ],
        },
        {
          path: 'teacher',
          name: 'teacher',
          component: RouterReplaceComp(()=> import('../views/role/teacher/TeacherDashboardView.vue')),
          children:[
            {
              path: 'class',
              name: 'teacherClass',
              component: () => import('../views/role/teacher/TeacherClassView.vue'),
            },
            {
              path: 'class/:id',
              name: 'teacherClass/id',
              component: () => import('../views/role/teacher/TeacherClassDetailView.vue'),
            },
            {
                path: '/lessonScore',
                name: 'lessonScore',
                component: () => import('../views/role/teacher/LessonScoreView.vue'),
            },
            {
                path: ':courseId/questions/:lessonId',
                name: 'teacherQuestions',
                component: () => import('../views/role/teacher/TeacherQuestionsView.vue'),
            },
            {
              path: ':courseId/viewquestions/:lessonId',
              name: 'teacherViewQuestions',
              component: () => import('../views/role/teacher/TeacherViewQuestionsView.vue'),
            },
            {
              path: 'questionodteacher',
              name: 'questionsOfTeacher',
              component: () => import('../views/role/teacher/QuestionsOfTeacherView.vue'),
            }
          ]
        },
        {
          path: 'student',
          name: 'student',
          component: RouterReplaceComp(() => import('../views/role/student/StudentDashboardView.vue')),
          children:[
            {
              path: 'class',
              name: 'studentClass',
              component: () => import('../views/role/student/StudentClassView.vue'),
            },
            {
              path: 'class/:id',
              name: 'studentClass/id',
              component: () => import('../views/role/student/StudentClassDetailView.vue'),
            },
            {
              path: 'mycourse',
              name: 'studentMyCourse',
              component: () => import('../views/role/student/CoursesOfStudentView.vue'),
            },
            {
              path: 'choosecourse',
              name: 'studentChooseCourse',
              component: () => import('../views/role/student/ChooseCourseView.vue'),
            },
            {
              path: '/studentStatics',
              name: 'studentStatics',
              component: () => import('../views/role/student/StudentStaticsView.vue'),
            },
            {
              path: ':courseId/questions/:lessonId',
              name: 'studentQuestions',
              component: () => import('../views/role/student/StudentQuestionsView.vue'),
            },
          ]
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
