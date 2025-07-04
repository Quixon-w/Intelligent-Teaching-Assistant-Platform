<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Reading, 
  User, 
  UserFilled, 
  Refresh 
} from '@element-plus/icons-vue'
import { 
  getCourseNum, 
  getTeacherNum, 
  getStudentNum 
} from '@/api/admin.js'
import { handleException } from '@/utils/errorHandler'

const router = useRouter()

// 响应式数据
const courseCount = ref('-')
const teacherCount = ref('-')
const studentCount = ref('-')
const onlineUsers = ref('--')
const lastUpdateTime = ref('')

const loading = ref({
  course: false,
  teacher: false,
  student: false
})

// 获取课程数量
const fetchCourseCount = async () => {
  try {
    loading.value.course = true
    const res = await getCourseNum()
    if (res.code === 0) {
      courseCount.value = res.data || 0
    } else {
      handleException(res, '获取课程数量失败')
      courseCount.value = '获取失败'
    }
  } catch (error) {
    console.error('获取课程数量失败:', error)
    handleException(error, '获取课程数量失败')
    courseCount.value = '获取失败'
  } finally {
    loading.value.course = false
  }
}

// 获取教师数量
const fetchTeacherCount = async () => {
  try {
    loading.value.teacher = true
    const res = await getTeacherNum()
    if (res.code === 0) {
      teacherCount.value = res.data || 0
    } else {
      handleException(res, '获取教师数量失败')
      teacherCount.value = '获取失败'
    }
  } catch (error) {
    console.error('获取教师数量失败:', error)
    handleException(error, '获取教师数量失败')
    teacherCount.value = '获取失败'
  } finally {
    loading.value.teacher = false
  }
}

// 获取学生数量
const fetchStudentCount = async () => {
  try {
    loading.value.student = true
    const res = await getStudentNum()
    if (res.code === 0) {
      studentCount.value = res.data || 0
    } else {
      handleException(res, '获取学生数量失败')
      studentCount.value = '获取失败'
    }
  } catch (error) {
    console.error('获取学生数量失败:', error)
    handleException(error, '获取学生数量失败')
    studentCount.value = '获取失败'
  } finally {
    loading.value.student = false
  }
}

// 刷新所有数据
const refreshData = async () => {
  await Promise.all([
    fetchCourseCount(),
    fetchTeacherCount(),
    fetchStudentCount()
  ])
  updateLastUpdateTime()
  ElMessage.success('数据刷新成功')
}

// 更新最后更新时间
const updateLastUpdateTime = () => {
  const now = new Date()
  lastUpdateTime.value = now.toLocaleString('zh-CN')
}

// 导航到用户管理页面
const goToUserManagement = () => {
  router.push('/dashboard/admin/users')
}

// 导航到课程监控页面
const goToCourseMonitor = () => {
  router.push('/dashboard/admin/courses')
}

// 页面加载时获取数据
onMounted(() => {
  refreshData()
})
</script>

<template>
  <div class="admin-dashboard">
    <!-- 页面标题 -->
    <div class="dashboard-header">
      <h1>管理员仪表板</h1>
      <p>系统概览与统计数据</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-container">
      <el-row :gutter="24">
        <!-- 课程数量 -->
        <el-col :span="8">
          <el-card class="stat-card course-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="48"><Reading /></el-icon>
              </div>
              <div class="stat-info">
                <h3>课程数量</h3>
                <div class="stat-number" v-loading="loading.course">
                  {{ courseCount }}
                </div>
                <p class="stat-desc">系统中的总课程数</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 教师数量 -->
        <el-col :span="8">
          <el-card class="stat-card teacher-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="48"><User /></el-icon>
              </div>
              <div class="stat-info">
                <h3>教师数量</h3>
                <div class="stat-number" v-loading="loading.teacher">
                  {{ teacherCount }}
                </div>
                <p class="stat-desc">系统中的教师总数</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 学生数量 -->
        <el-col :span="8">
          <el-card class="stat-card student-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon size="48"><UserFilled /></el-icon>
              </div>
              <div class="stat-info">
                <h3>学生数量</h3>
                <div class="stat-number" v-loading="loading.student">
                  {{ studentCount }}
                </div>
                <p class="stat-desc">系统中的学生总数</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <el-card class="actions-card">
        <template #header>
          <h3>快捷操作</h3>
        </template>
        <div class="actions-content">
          <el-button type="primary" @click="goToUserManagement">
            <el-icon><User /></el-icon>
            用户管理
          </el-button>
          <el-button type="success" @click="goToCourseMonitor">
            <el-icon><Reading /></el-icon>
            课程监控
          </el-button>
          <el-button type="info" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 系统信息 -->
    <div class="system-info">
      <el-card class="info-card">
        <template #header>
          <h3>系统信息</h3>
        </template>
        <div class="info-content">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="最后更新">{{ lastUpdateTime }}</el-descriptions-item>
            <el-descriptions-item label="在线用户">{{ onlineUsers }}</el-descriptions-item>
            <el-descriptions-item label="系统状态">
              <el-tag type="success">正常运行</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.admin-dashboard {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.dashboard-header {
  margin-bottom: 32px;
  text-align: center;
}

.dashboard-header h1 {
  margin: 0;
  color: #303133;
  font-size: 32px;
  font-weight: 600;
}

.dashboard-header p {
  margin: 8px 0 0 0;
  color: #909399;
  font-size: 16px;
}

.stats-container {
  margin-bottom: 32px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: none;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 8px;
}

.stat-icon {
  margin-right: 20px;
  padding: 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.course-card .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.teacher-card .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.student-card .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
  margin: 8px 0;
  line-height: 1;
}

.stat-desc {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.quick-actions {
  margin-bottom: 32px;
}

.actions-card {
  border-radius: 12px;
}

.actions-card h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.actions-content {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.actions-content .el-button {
  flex: 1;
  min-width: 120px;
}

.system-info {
  margin-bottom: 32px;
}

.info-card {
  border-radius: 12px;
}

.info-card h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.info-content {
  padding: 16px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-dashboard {
    padding: 16px;
  }
  
  .dashboard-header h1 {
    font-size: 24px;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
  }
  
  .stat-icon {
    margin-right: 0;
    margin-bottom: 16px;
  }
  
  .actions-content {
    flex-direction: column;
  }
  
  .actions-content .el-button {
    width: 100%;
  }
}

/* 加载状态样式 */
.stat-number[v-loading] {
  min-height: 50px;
}
</style> 