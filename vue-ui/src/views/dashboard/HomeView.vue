<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <template #header>
            <div class="card-header">
              <h2>欢迎使用智能教学辅助平台</h2>
            </div>
          </template>
          <div class="welcome-content">
            <p>您好，{{ username }}！欢迎回到{{ roleText }}</p>
            <p>今天是 {{ currentDate }}，祝您使用愉快！</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 学生端统计数据 -->
    <div v-if="userRole === 'student'" class="student-stats">
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 学习数据统计 -->
        <el-col :span="8">
          <el-card class="stat-card primary">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="40"><Reading /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.courses }}</h3>
                <p>已选课程</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="stat-card success">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="40"><EditPen /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.tests }}</h3>
                <p>完成测试</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="stat-card info">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="40"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.overallProgress }}%</h3>
                <p>学习进度</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 非学生端的原有布局 -->
    <el-row v-else :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40"><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.courses }}</h3>
              <p>{{ statsLabels.courses }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40"><User /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.users }}</h3>
              <p>{{ statsLabels.users }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="40"><EditPen /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.tests }}</h3>
              <p>{{ statsLabels.tests }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>快速操作</h3>
            </div>
          </template>
          <div class="quick-actions">
            <el-button 
              v-for="action in quickActions" 
              :key="action.name"
              :type="action.type"
              :icon="action.icon"
              @click="handleQuickAction(action.route)"
              size="large"
              style="margin: 8px;"
            >
              {{ action.name }}
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>系统公告</h3>
            </div>
          </template>
          <div class="announcements">
            <div v-for="announcement in announcements" :key="announcement.id" class="announcement-item">
              <h4>{{ announcement.title }}</h4>
              <p>{{ announcement.content }}</p>
              <span class="announcement-date">{{ announcement.date }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  Reading, 
  User, 
  EditPen, 
  TrendCharts
} from '@element-plus/icons-vue'
import { getRoleCenterName } from '@/utils/roleMapper'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const stats = ref({
  courses: 0,
  users: 0,
  tests: 0,
  // 学生端统计数据
  overallProgress: 0
})

const announcements = ref([
  {
    id: 1,
    title: '系统更新通知',
    content: '系统已更新到最新版本，新增多项功能优化用户体验。',
    date: '2024-01-15'
  },
  {
    id: 2,
    title: 'AI助手功能上线',
    content: '智能AI助手功能正式上线，支持文件问答和智能对话。',
    date: '2024-01-10'
  }
])

// 计算属性
const username = computed(() => authStore.user?.username || '用户')
const userRole = computed(() => authStore.userRole)

const roleText = computed(() => {
  return getRoleCenterName(userRole.value)
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

const statsLabels = computed(() => {
  if (userRole.value === 'teacher') {
    return {
      courses: '我的课程数量',
      users: '选课总人数',
      tests: '我发布的测试数量'
    }
  } else if (userRole.value === 'admin') {
    return {
      courses: '课程数量',
      users: '教师数量',
      tests: '学生数量'
    }
  }
  
  return {
    courses: '课程数量',
    users: '用户数量',
    tests: '测试数量'
  }
})

const quickActions = computed(() => {
  const baseActions = [
    {
      name: 'AI助手',
      type: 'primary',
      icon: 'ChatDotRound',
      route: '/dashboard/ai-assistant'
    }
  ]
  
  if (userRole.value === 'admin') {
    return [
      ...baseActions,
      {
        name: '用户管理',
        type: 'success',
        icon: 'User',
        route: '/dashboard/admin/users'
      },
      {
        name: '课程监控',
        type: 'warning',
        icon: 'Reading',
        route: '/dashboard/admin/courses'
      }
    ]
  } else if (userRole.value === 'teacher') {
    return [
      ...baseActions,
      {
        name: '我的课程',
        type: 'success',
        icon: 'Reading',
        route: '/dashboard/teacher/courses'
      },
      {
        name: '题库管理',
        type: 'warning',
        icon: 'EditPen',
        route: '/dashboard/teacher/questions'
      }
    ]
  } else if (userRole.value === 'student') {
    return [
      ...baseActions,
      {
        name: '课程选择',
        type: 'success',
        icon: 'Reading',
        route: '/dashboard/student/courses'
      },
      {
        name: '我的课程',
        type: 'warning',
        icon: 'User',
        route: '/dashboard/student/my-courses'
      }
    ]
  }
  
  return baseActions
})

// 方法
const handleQuickAction = (route) => {
  router.push(route)
}

const loadStats = async () => {
  try {
    if (userRole.value === 'teacher') {
      await loadTeacherStats()
    } else if (userRole.value === 'admin') {
      await loadAdminStats()
    } else if (userRole.value === 'student') {
      await loadStudentStats()
    } else {
      stats.value = {
        courses: 0,
        users: 0,
        tests: 0,
        overallProgress: 0
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    stats.value = {
      courses: 0,
      users: 0,
      tests: 0,
      overallProgress: 0
    }
  }
}

const loadTeacherStats = async () => {
  try {
    // 1. 获取我的课程数量
    const coursesResult = await request.get('/api/course/listById', {
      params: {
        teacherId: authStore.user?.id
      }
    })
    
    let coursesCount = 0
    if (coursesResult.code === 0 && coursesResult.data) {
      coursesCount = coursesResult.data.length
    }
    
    // 2. 获取选课总人数
    const studentsResult = await request.get('/api/enroll/studentNumSum', {
      params: {
        teacherId: authStore.user?.id
      }
    })
    
    let totalStudents = 0
    if (studentsResult.code === 0) {
      totalStudents = studentsResult.data || 0
    }
    
    // 3. 获取我发布的测试数量
    const testsResult = await request.get('/api/lesson/getQuestionedLessonNum', {
      params: {
        teacherId: authStore.user?.id
      }
    })
    
    let totalTests = 0
    if (testsResult.code === 0) {
      totalTests = testsResult.data || 0
    }
    
    stats.value = {
      courses: coursesCount,
      users: totalStudents,
      tests: totalTests,
      overallProgress: 0
    }
  } catch (error) {
    console.error('获取教师统计数据失败:', error)
    stats.value = {
      courses: 0,
      users: 0,
      tests: 0,
      overallProgress: 0
    }
  }
}

const loadAdminStats = async () => {
  try {
    console.log('开始加载管理员统计数据...')
    
    // 并行请求所有统计数据
    const [courseResult, teacherResult, studentResult] = await Promise.all([
      // 1. 获取课程数量（从分页接口提取总数）
      request.get('/api/course/listPage', {
        params: {
          pageNum: 1,
          pageSize: 1,
          courseName: '',
          teacherName: ''
        }
      }),
      // 2. 获取教师数量
      request.get('/api/user/getTeacherNum'),
      // 3. 获取学生数量
      request.get('/api/user/getStudentNum')
    ])
    
    let coursesCount = 0
    let teachersCount = 0
    let studentsCount = 0
    
    // 处理课程数量（从分页数据中提取总数）
    if (courseResult.code === 0 && courseResult.data && typeof courseResult.data.total === 'number') {
      coursesCount = courseResult.data.total
      console.log('课程数量:', coursesCount)
    } else {
      console.warn('获取课程数量失败:', courseResult.message)
    }
    
    // 处理教师数量
    if (teacherResult.code === 0 && typeof teacherResult.data === 'number') {
      teachersCount = teacherResult.data
      console.log('教师数量:', teachersCount)
    } else {
      console.warn('获取教师数量失败:', teacherResult.message)
    }
    
    // 处理学生数量
    if (studentResult.code === 0 && typeof studentResult.data === 'number') {
      studentsCount = studentResult.data
      console.log('学生数量:', studentsCount)
    } else {
      console.warn('获取学生数量失败:', studentResult.message)
    }
    
    stats.value = {
      courses: coursesCount,
      users: teachersCount,  // 改为只显示教师数量
      tests: studentsCount,  // 改为显示学生数量
      overallProgress: 0
    }
    
    console.log('管理员统计数据加载完成:', stats.value)
    
  } catch (error) {
    console.error('获取管理员统计数据失败:', error)
  stats.value = {
      courses: 0,
      users: 0,
      tests: 0,
    overallProgress: 0
    }
  }
}

const loadStudentStats = async () => {
  try {
    console.log('开始加载学生统计数据...')
    
    const studentId = authStore.user?.id
    if (!studentId) {
      console.error('未找到学生ID')
      return
    }
    
    // 并行请求所有数据
    const [enrollResult, testsResult] = await Promise.all([
      // 1. 获取已选课程数量
      request.get('/api/enroll/list/student', {
        params: { studentId }
      }),
      // 2. 获取完成测试数量
      request.get('/api/records/getFinishedTestNum', {
        params: { studentId }
      })
    ])
    
    let coursesCount = 0
    let finishedTests = 0
    
    // 处理已选课程数量
    if (enrollResult.code === 0 && enrollResult.data) {
      coursesCount = enrollResult.data.length
      console.log('已选课程数量:', coursesCount)
    } else {
      console.warn('获取已选课程失败:', enrollResult.message)
    }
    
    // 处理完成测试数量
    if (testsResult.code === 0 && typeof testsResult.data === 'number') {
      finishedTests = testsResult.data
      console.log('完成测试数量:', finishedTests)
    } else {
      console.warn('获取完成测试数量失败:', testsResult.message)
    }
    
    // 3. 计算总体学习进度
    let progressPercentage = 0
    if (enrollResult.code === 0 && enrollResult.data && enrollResult.data.length > 0) {
      // 为每门课程计算进度并求平均值
      const progressPromises = enrollResult.data.map(async (item) => {
        try {
          const course = item.course
          // 获取课程的课时列表
          const lessonsRes = await request.get('/api/lesson/list', {
            params: { courseId: course.id }
          })

          let totalLessons = 0
          let completedLessons = 0

          if (lessonsRes.code === 0 && lessonsRes.data) {
            totalLessons = lessonsRes.data.length

            // 检查每个课时的完成状态
            for (const lesson of lessonsRes.data) {
              if (lesson.hasQuestion === 1) {
                // 检查是否已完成测试
                try {
                  const recordsRes = await request.get('/api/records/getRecords', {
                    params: { 
                      lessonId: lesson.lessonId,
                      studentId: studentId
                    }
                  })

                  if (recordsRes.code === 0 && recordsRes.data && recordsRes.data.length > 0) {
                    completedLessons++
                  }
                } catch (error) {
                  console.error('检查课时完成状态失败:', error)
                }
              } else {
                // 没有测试的课时默认为已完成
                completedLessons++
              }
            }
          }

          return totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0
        } catch (error) {
          console.error('计算课程进度失败:', error)
          return 0
        }
      })

      const courseProgresses = await Promise.all(progressPromises)
      progressPercentage = courseProgresses.length > 0 
        ? Math.round(courseProgresses.reduce((sum, progress) => sum + progress, 0) / courseProgresses.length)
        : 0
    }
    
    stats.value = {
      courses: coursesCount,
      tests: finishedTests,
      overallProgress: progressPercentage,
      users: 0 // 不再使用
    }
    
    console.log('学生统计数据加载完成:', stats.value)
    
  } catch (error) {
    console.error('获取学生统计数据失败:', error)
    stats.value = {
      courses: 0,
      users: 0,
      tests: 0,
      overallProgress: 0
    }
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 欢迎卡片样式 */
.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.welcome-card :deep(.el-card__header) {
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.welcome-card :deep(.el-card__body) {
  background: transparent;
}

.card-header h2 {
  margin: 0;
  color: white;
}

.welcome-content {
  text-align: center;
  padding: 20px 0;
}

.welcome-content p {
  margin: 10px 0;
  font-size: 16px;
}

.stat-card {
  text-align: center;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.stat-icon {
  margin-right: 20px;
  color: #409eff;
}

.stat-info h3 {
  margin: 0;
  font-size: 28px;
  color: #303133;
}

.stat-info p {
  margin: 5px 0 0 0;
  color: #909399;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
}

.announcement-item {
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.announcement-item:last-child {
  border-bottom: none;
}

.announcement-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.announcement-item p {
  margin: 0 0 8px 0;
  color: #606266;
  line-height: 1.5;
}

.announcement-date {
  font-size: 12px;
  color: #909399;
}

/* 学生端统计卡片样式 */
.student-stats .stat-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: none;
  overflow: hidden;
}

.student-stats .stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.student-stats .stat-card.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.student-stats .stat-card.success {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.student-stats .stat-card.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.student-stats .stat-card.info {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
  color: white;
}

.student-stats .stat-card :deep(.el-card__body) {
  padding: 20px;
}

.student-stats .stat-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.student-stats .stat-icon {
  margin-right: 20px;
  opacity: 0.8;
}

.student-stats .stat-info h3 {
  margin: 0;
  font-size: 32px;
  font-weight: bold;
}

.student-stats .stat-info p {
  margin: 8px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
}

/* 快速操作按钮样式优化 */
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
}

.quick-actions .el-button {
  border-radius: 8px;
  padding: 12px 20px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.quick-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .student-stats .el-col {
    margin-bottom: 20px;
  }
  
  .quick-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .quick-actions .el-button {
    width: 100%;
    max-width: 200px;
  }
}
</style> 