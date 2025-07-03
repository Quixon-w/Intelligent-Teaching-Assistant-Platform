<template>
  <div class="my-courses-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h2 class="page-title">我的课程</h2>
          <p class="page-subtitle">管理您已选择的课程，查看学习进度</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" size="large" @click="goToAllCourses">
            <el-icon><Plus /></el-icon>
            选择更多课程
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview" v-if="enrolledCourses.length > 0">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ enrolledCourses.length }}</div>
              <div class="stats-label">已选课程</div>
            </div>
            <el-icon class="stats-icon"><Reading /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ completedCourses }}</div>
              <div class="stats-label">已完成课程</div>
            </div>
            <el-icon class="stats-icon success"><Check /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ totalPendingTests }}</div>
              <div class="stats-label">待完成测试</div>
            </div>
            <el-icon class="stats-icon warning"><EditPen /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ Math.round(averageProgress) }}%</div>
              <div class="stats-label">平均进度</div>
            </div>
            <el-icon class="stats-icon info"><TrendCharts /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 课程列表 -->
    <div class="courses-section">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="4" animated />
      </div>

      <!-- 空状态 -->
      <div v-else-if="enrolledCourses.length === 0" class="empty-state">
        <el-empty :image-size="120" description="您还没有选择任何课程">
          <div class="empty-actions">
            <el-button type="primary" size="large" @click="goToAllCourses">
              <el-icon><Plus /></el-icon>
              去选择课程
            </el-button>
          </div>
        </el-empty>
      </div>

      <!-- 课程网格 -->
      <div v-else class="courses-grid">
        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :lg="8" v-for="course in enrolledCourses" :key="course.id">
            <el-card class="course-card" shadow="hover">
                             <!-- 课程头部 -->
               <template #header>
                 <div class="course-header">
                   <div class="course-info-section">
                     <h3 class="course-name" :title="course.name || course.courseName">{{ course.name || course.courseName || '未知课程' }}</h3>
                     <div class="course-meta-header">
                       <span class="course-teacher">
                         <el-icon><UserFilled /></el-icon>
                         {{ course.teacherName }}
                       </span>
                     </div>
                   </div>
                   <el-tag 
                     :type="course.isOver === 0 ? 'success' : 'info'" 
                     size="large"
                     class="course-status"
                   >
                     {{ course.isOver === 0 ? '进行中' : '已结束' }}
                   </el-tag>
                 </div>
               </template>

                             <!-- 课程内容 -->
               <div class="course-content">
                 <!-- 学习进度 -->
                 <div class="progress-section">
                   <div class="progress-header">
                     <span class="progress-label">学习进度</span>
                     <span class="progress-value">
                       {{ getProgressText(course) }}
                     </span>
                   </div>
                   <div v-if="course.totalLessons > 0">
                     <el-progress 
                       :percentage="course.progressPercentage || 0"
                       :color="getProgressColor(course.progressPercentage || 0)"
                       :stroke-width="8"
                       class="progress-bar"
                     />
                     <div class="progress-stats">
                       <span class="stat-item">
                         <el-icon><Check /></el-icon>
                         已完成 {{ course.completedLessons || 0 }} 个课时
                       </span>
                       <span class="stat-item" v-if="course.pendingTests > 0">
                         <el-icon class="warning-icon"><Warning /></el-icon>
                         {{ course.pendingTests }} 个待测试
                       </span>
                     </div>
                   </div>
                   <div v-else class="no-lessons">
                     <el-icon><InfoFilled /></el-icon>
                     <span>暂时没有课时安排</span>
                   </div>
                 </div>

                                 <!-- 课程信息 -->
                <div class="course-meta">
                  <div class="meta-item">
                    <span class="meta-label">加入时间:</span>
                    <span class="meta-value">{{ formatDate(course.startTime) }}</span>
                  </div>
                  <div class="meta-item" v-if="course.isOver === 1 && course.finalScore !== undefined && course.finalScore !== null">
                    <span class="meta-label">课程成绩:</span>
                    <span class="meta-value score">{{ course.finalScore }}分</span>
                  </div>
                  <div class="meta-item" v-if="course.comment">
                    <span class="meta-label">课程简介:</span>
                    <span class="meta-value">{{ course.comment }}</span>
                  </div>
                </div>
              </div>

              <!-- 操作按钮 -->
              <template #footer>
                <div class="course-actions">
                  <el-button 
                    type="primary" 
                    size="default"
                    @click.stop="viewCourse(course)"
                    class="action-btn primary"
                  >
                    <el-icon><View /></el-icon>
                    查看详情
                  </el-button>
                  
                  <el-button 
                    v-if="course.pendingTests > 0"
                    type="warning" 
                    size="default"
                    @click.stop="takeTest(course)"
                    class="action-btn warning"
                  >
                    <el-icon><EditPen /></el-icon>
                    参加测试({{ course.pendingTests }})
                  </el-button>
                  
                  <el-button 
                    v-if="course.isOver === 0"
                    type="danger" 
                    size="default"
                    plain
                    @click.stop="dismissCourse(course)"
                    class="action-btn danger"
                  >
                    <el-icon><Close /></el-icon>
                    退课
                  </el-button>
                </div>
              </template>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import { dismissCourse as dismissCourseAPI } from '@/api/course'
import {
  Plus,
  Reading,
  Check,
  EditPen,
  TrendCharts,
  UserFilled,
  View,
  Warning,
  Close,
  InfoFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const enrolledCourses = ref([])
const loading = ref(false)

// 计算属性
const completedCourses = computed(() => {
  // 根据课程结课状态计算已完成课程数量（isOver !== 0 表示课程已结束）
  return enrolledCourses.value.filter(course => course.isOver !== 0).length
})

const totalPendingTests = computed(() => {
  return enrolledCourses.value.reduce((total, course) => {
    return total + (course.pendingTests || 0)
  }, 0)
})

const averageProgress = computed(() => {
  if (enrolledCourses.value.length === 0) return 0
  const totalProgress = enrolledCourses.value.reduce((sum, course) => {
    return sum + (course.progressPercentage || 0)
  }, 0)
  return totalProgress / enrolledCourses.value.length
})

// 方法
const getProgressColor = (percentage) => {
  if (percentage === 100) return '#67c23a'
  if (percentage >= 75) return '#409eff'
  if (percentage >= 50) return '#e6a23c'
  return '#f56c6c'
}

const getProgressText = (course) => {
  const totalLessons = course.totalLessons || 0
  const completedLessons = course.completedLessons || 0
  
  if (totalLessons === 0) {
    return '暂时没有课时'
  }
  
  return `${completedLessons}/${totalLessons}`
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const loadEnrolledCourses = async () => {
  if (!authStore.user?.id) {
    ElMessage.error('用户信息不完整')
    return
  }

  loading.value = true

  try {
    // 获取学生已选课程
    const response = await request.get('/api/enroll/list/student', {
      params: { studentId: authStore.user.id }
    })

    if (response.code === 0 && response.data) {
      // 为每门课程计算进度和待测试数量
      const coursesWithProgress = await Promise.all(
        response.data.map(async (item) => {
          try {
            const course = item.course
            const enroll = item.enroll
            
            // 获取课程的课时列表
            const lessonsRes = await request.get('/api/lesson/list', {
              params: { courseId: course.id }
            })

            let totalLessons = 0
            let completedLessons = 0
            let pendingTests = 0

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
                        studentId: authStore.user.id 
                      }
                    })

                    if (recordsRes.code === 0 && recordsRes.data && recordsRes.data.length > 0) {
                      completedLessons++
                    } else {
                      pendingTests++
                    }
                  } catch (error) {
                    console.error('检查课时完成状态失败:', error)
                    pendingTests++
                  }
                } else {
                  // 没有测试的课时默认为已完成
                  completedLessons++
                }
              }
            }

            const progressPercentage = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0

            // 只有在课程已结课时才获取课程成绩
            let finalScore = null
            if (course.isOver === 1) {
              try {
                const scoreRes = await request.get('/api/course/score', {
                  params: { 
                    courseId: course.id, 
                    studentId: authStore.user.id 
                  }
                })
                
                if (scoreRes.code === 0) {
                  finalScore = scoreRes.data || 0
                }
              } catch (error) {
                console.error('获取课程成绩失败:', error)
              }
            }

            return {
              // 合并课程和选课信息
              ...course,
              ...enroll,
              // 确保课程ID正确
              id: course.id,
              name: course.name || course.courseName,
              totalLessons,
              completedLessons,
              pendingTests,
              progressPercentage,
              finalScore
            }
          } catch (error) {
            console.error('获取课程进度失败:', error)
            return {
              ...item.course,
              ...item.enroll,
              // 确保课程ID正确
              id: item.course.id,
              name: item.course.name || item.course.courseName,
              totalLessons: 0,
              completedLessons: 0,
              pendingTests: 0,
              progressPercentage: 0,
              finalScore: null
            }
          }
        })
      )

      enrolledCourses.value = coursesWithProgress
      console.log('已选课程数据:', enrolledCourses.value)
      
      // 验证课程数据结构
      enrolledCourses.value.forEach((course, index) => {
        if (!course.id) {
          console.warn(`课程 ${index} 缺少ID:`, course)
        }
      })
    } else {
      ElMessage.error(response.message || '获取已选课程失败')
    }
  } catch (error) {
    console.error('获取已选课程失败:', error)
    ElMessage.error('获取已选课程失败')
  } finally {
    loading.value = false
  }
}

const viewCourse = (course) => {
  console.log('查看课程:', course)
  
  // 验证课程ID
  if (!course || !course.id) {
    ElMessage.error('课程信息不完整，无法跳转')
    console.error('课程信息不完整:', course)
    return
  }
  
  try {
    // 跳转到课程详情页
    router.push(`/dashboard/student/courses/${course.id}`)
  } catch (error) {
    console.error('跳转失败:', error)
    ElMessage.error('页面跳转失败，请稍后重试')
  }
}

const takeTest = (course) => {
  console.log('参加测试:', course)
  
  // 验证课程ID
  if (!course || !course.id) {
    ElMessage.error('课程信息不完整，无法跳转')
    console.error('课程信息不完整:', course)
    return
  }
  
  try {
    router.push(`/dashboard/student/courses/${course.id}`)
    ElMessage.info(`已跳转到"${course.name}"课程详情，请选择要参加测试的课时`)
  } catch (error) {
    console.error('跳转失败:', error)
    ElMessage.error('页面跳转失败，请稍后重试')
  }
}

const dismissCourse = async (course) => {
  try {
    await ElMessageBox.confirm(
             `确定要退出课程 "${course.name}" 吗？退课后您将无法继续学习该课程。`,
      '确认退课',
      {
        confirmButtonText: '确定退课',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )

    console.log('正在退课，参数:', { studentId: authStore.user.id, courseId: course.id })

    const result = await dismissCourseAPI(authStore.user.id, course.id)

    console.log('退课API响应:', result)

    if (result.code === 0) {
      ElMessage.success('退课成功')
      // 重新加载已选课程列表
      loadEnrolledCourses()
    } else {
      ElMessage.error(result.message || '退课失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('退课失败:', error)
      ElMessage.error('退课失败，请稍后重试')
    }
  }
}

const goToAllCourses = () => {
  router.push('/dashboard/student/courses')
}

// 生命周期
onMounted(() => {
  loadEnrolledCourses()
})
</script>

<style scoped>
.my-courses-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* 页面头部 */
.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 24px 0;
  border-bottom: 1px solid #e4e7ed;
}

.title-section {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  flex-shrink: 0;
}

/* 统计概览 */
.stats-overview {
  margin-bottom: 32px;
}

.stats-card {
  border: none;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  transition: all 0.3s ease;
  cursor: pointer;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stats-card :deep(.el-card__body) {
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.stats-icon {
  font-size: 36px;
  color: #909399;
}

.stats-icon.success {
  color: #67c23a;
}

.stats-icon.warning {
  color: #e6a23c;
}

.stats-icon.info {
  color: #409eff;
}

/* 课程列表 */
.courses-section {
  min-height: 400px;
}

.loading-container {
  padding: 40px;
}

.empty-state {
  padding: 80px 0;
  text-align: center;
}

.empty-actions {
  margin-top: 20px;
}

.courses-grid {
  margin-top: 20px;
}

/* 课程卡片 */
.course-card {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  margin-bottom: 24px;
  height: 100%;
  transition: all 0.3s ease;
  cursor: pointer;
}

.course-card:hover {
  border-color: #409eff;
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(64, 158, 255, 0.15);
}

.course-card :deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f5f7fa;
}

.course-card :deep(.el-card__body) {
  padding: 24px;
}

.course-card :deep(.el-card__footer) {
  padding: 16px 24px;
  background-color: #fafbfc;
  border-top: 1px solid #f5f7fa;
}

/* 课程头部 */
.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.course-info-section {
  flex: 1;
  min-width: 0;
}

.course-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133 !important;
  margin: 0 0 8px 0;
  line-height: 1.4;
  word-break: break-word;
  display: block;
  min-height: 24px;
}

.course-meta-header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.course-teacher {
  font-size: 14px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.course-status {
  flex-shrink: 0;
}

/* 课程内容 */
.course-content {
  margin-bottom: 20px;
}

/* 进度部分 */
.progress-section {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.progress-value {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}

.progress-bar {
  margin-bottom: 12px;
}

.progress-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
}

.warning-icon {
  color: #e6a23c;
}

.no-lessons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  background-color: #f8f9fa;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  color: #909399;
  font-size: 14px;
  margin-top: 12px;
}

.no-lessons .el-icon {
  font-size: 16px;
}

/* 课程元信息 */
.course-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.meta-label {
  color: #909399;
}

.meta-value {
  color: #303133;
  font-weight: 500;
}

.meta-value.score {
  color: #67c23a;
  font-weight: 600;
}

/* 操作按钮 */
.course-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 100px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #409eff, #50bfff);
  border: none;
}

.action-btn.warning {
  background: linear-gradient(135deg, #e6a23c, #f7ba2a);
  border: none;
}

.action-btn.danger {
  color: #f56c6c;
  border-color: #f56c6c;
}

.action-btn.danger:hover {
  background-color: #f56c6c;
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .my-courses-container {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .stats-overview {
    margin-bottom: 24px;
  }

  .course-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .course-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .course-info-section {
    width: 100%;
  }

  .course-name {
    font-size: 16px;
    -webkit-line-clamp: 3;
  }

  .course-meta-header {
    justify-content: space-between;
    width: 100%;
  }

  .progress-stats {
    flex-direction: column;
    gap: 8px;
  }

  .no-lessons {
    padding: 16px;
    font-size: 13px;
  }
}
</style> 