<template>
  <div class="home-container">
    <!-- 错误信息展示区域 -->
    <div v-if="errorMessages.length > 0" class="error-section">
      <el-alert
        v-for="(error, index) in errorMessages"
        :key="index"
        :title="error.title"
        :description="error.description"
        type="error"
        :closable="true"
        @close="removeError(index)"
        show-icon
        style="margin-bottom: 16px;"
      />
    </div>

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
              <h3>项目简介</h3>
            </div>
          </template>
          <div class="project-intro">
            <div class="intro-item">
              <h4>🎓 智能教学助手平台</h4>
              <p>本项目旨在开发一个基于开源大语言模型的智能教学助手平台，聚焦于教学过程的备课设计自动化、学生个性化练习辅导以及教学数据分析可视化，助力教育数字化转型，提升实训教学效率与个性化水平。</p>
            </div>
            <div class="intro-item">
              <h4>🎯 核心功能</h4>
              <p><strong>教师端：</strong>智能备课设计、自动生成考核题目、学情分析与建议、教学资源导出与管理</p>
              <p><strong>学生端：</strong>在线练习与错题反馈、智能问答助手、随机题目生成与评测建议</p>
              <p><strong>管理端：</strong>用户管理、教学资源管理、可视化大屏分析</p>
            </div>
            <div class="intro-item">
              <h4>💡 技术特色</h4>
              <p>采用前后端分离架构，整合本地知识库与大模型能力，实现从"教师教"到"AI辅助教"，从"学生练"到"AI智能练"的智能化教学生态。</p>
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
import { showDetailedError, handleException } from '@/utils/errorHandler'

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

// 错误信息管理
const errorMessages = ref([])

// 添加错误信息
const addError = (title, description) => {
  errorMessages.value.push({
    title,
    description,
    timestamp: Date.now()
  })
}

// 移除错误信息
const removeError = (index) => {
  errorMessages.value.splice(index, 1)
}

// 清除所有错误信息
const clearErrors = () => {
  errorMessages.value = []
}

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
  try {
    if (!route) {
      addError('操作失败', '无效的操作路径')
      return
    }
    
    router.push(route).catch(error => {
      console.error('路由跳转失败:', error)
      addError('页面跳转失败', `无法跳转到 ${route}，请稍后重试`)
    })
  } catch (error) {
    console.error('快速操作执行失败:', error)
    addError('操作执行失败', error.message || '操作执行时发生错误')
  }
}

const loadStats = async () => {
  try {
    // 清除之前的错误信息
    clearErrors()
    
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
    
    // 添加错误信息到界面
    const errorTitle = '统计数据加载失败'
    let errorDescription = '无法获取统计数据，请稍后重试'
    
    if (error.response?.data) {
      // 后端返回的错误信息
      errorDescription = error.response.data.description || 
                       error.response.data.message || 
                       errorDescription
    } else if (error.message) {
      errorDescription = error.message
    }
    
    addError(errorTitle, errorDescription)
    
    // 设置默认值
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
    
    // 添加错误信息到界面
    const errorTitle = '教师统计数据加载失败'
    let errorDescription = '无法获取教师统计数据，请稍后重试'
    
    if (error.response?.data) {
      errorDescription = error.response.data.description || 
                       error.response.data.message || 
                       errorDescription
    } else if (error.message) {
      errorDescription = error.message
    }
    
    addError(errorTitle, errorDescription)
    
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
      addError('课程数据获取失败', courseResult.message || '无法获取课程数量')
    }
    
    // 处理教师数量
    if (teacherResult.code === 0 && typeof teacherResult.data === 'number') {
      teachersCount = teacherResult.data
      console.log('教师数量:', teachersCount)
    } else {
      console.warn('获取教师数量失败:', teacherResult.message)
      addError('教师数据获取失败', teacherResult.message || '无法获取教师数量')
    }
    
    // 处理学生数量
    if (studentResult.code === 0 && typeof studentResult.data === 'number') {
      studentsCount = studentResult.data
      console.log('学生数量:', studentsCount)
    } else {
      console.warn('获取学生数量失败:', studentResult.message)
      addError('学生数据获取失败', studentResult.message || '无法获取学生数量')
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
    
    // 添加错误信息到界面
    const errorTitle = '管理员统计数据加载失败'
    let errorDescription = '无法获取管理员统计数据，请稍后重试'
    
    if (error.response?.data) {
      errorDescription = error.response.data.description || 
                       error.response.data.message || 
                       errorDescription
    } else if (error.message) {
      errorDescription = error.message
    }
    
    addError(errorTitle, errorDescription)
    
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
      addError('用户信息错误', '无法获取学生ID，请重新登录')
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
      addError('选课数据获取失败', enrollResult.message || '无法获取已选课程信息')
    }
    
    // 处理完成测试数量
    if (testsResult.code === 0 && typeof testsResult.data === 'number') {
      finishedTests = testsResult.data
      console.log('完成测试数量:', finishedTests)
    } else {
      console.warn('获取完成测试数量失败:', testsResult.message)
      addError('测试数据获取失败', testsResult.message || '无法获取完成测试数量')
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
                  addError('学习进度计算失败', `课时 ${lesson.lessonName} 进度检查失败: ${error.message}`)
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
          addError('学习进度计算失败', `课程 ${course?.name || course?.courseName} 进度计算失败: ${error.message}`)
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
    
    // 添加错误信息到界面
    const errorTitle = '学生统计数据加载失败'
    let errorDescription = '无法获取学生统计数据，请稍后重试'
    
    if (error.response?.data) {
      errorDescription = error.response.data.description || 
                       error.response.data.message || 
                       errorDescription
    } else if (error.message) {
      errorDescription = error.message
    }
    
    addError(errorTitle, errorDescription)
    
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

.project-intro {
  padding: 10px 0;
}

.intro-item {
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.intro-item:last-child {
  border-bottom: none;
}

.intro-item h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.intro-item p {
  margin: 0 0 8px 0;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

.intro-item p:last-child {
  margin-bottom: 0;
}

.intro-item strong {
  color: #409eff;
  font-weight: 600;
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

/* 错误信息展示区域样式 */
.error-section {
  margin-bottom: 20px;
}

.error-section .el-alert {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.error-section .el-alert:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.error-section .el-alert__title {
  font-weight: 600;
  font-size: 14px;
}

.error-section .el-alert__description {
  font-size: 13px;
  line-height: 1.5;
  margin-top: 4px;
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
  .error-section {
    margin-bottom: 16px;
  }
  
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