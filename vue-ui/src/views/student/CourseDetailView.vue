<template>
  <div class="course-detail-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>{{ courseInfo ? `${courseInfo.name || courseInfo.courseName} - 课程详情` : '课程详情' }}</h3>
          <div class="header-actions">
          <el-button @click="$router.back()">返回</el-button>
            <!-- 选课/取消选课按钮 -->
            <el-button 
              v-if="!isEnrolled && courseInfo?.isOver !== 1"
              type="success"
              @click="enrollCourse"
              :loading="enrolling"
            >
              选择这门课程
            </el-button>
            <el-button 
              v-else-if="isEnrolled && courseInfo?.isOver !== 1"
              type="danger"
              @click="dismissCourse"
            >
              退选课程
            </el-button>
            <el-tag v-else-if="courseInfo?.isOver === 1" type="info">课程已结束</el-tag>
          </div>
        </div>
      </template>
      
      <!-- 课程状态提示 -->
      <div v-if="courseInfo" class="course-status">
        <el-alert
          :title="getStatusTitle()"
          :type="getStatusType()"
          :description="getStatusDescription()"
          show-icon
          :closable="false"
        />
      </div>
      
      <!-- 课程基本信息 -->
      <div v-if="courseInfo" class="course-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程ID">{{ courseInfo.id }}</el-descriptions-item>
          <el-descriptions-item label="课程名称">{{ courseInfo.name || courseInfo.courseName }}</el-descriptions-item>
          <el-descriptions-item label="授课教师">{{ courseInfo.teacherName }}</el-descriptions-item>
          <el-descriptions-item label="课程状态">
            <el-tag :type="courseInfo.isOver === 0 ? 'success' : 'danger'">
              {{ courseInfo.isOver === 0 ? '进行中' : '已结束' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ courseInfo.createTime }}</el-descriptions-item>
          <el-descriptions-item label="选课人数">{{ studentCount }}人</el-descriptions-item>
          <el-descriptions-item label="课程描述" :span="2">
            {{ courseInfo.comment || '暂无课程描述' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 主要内容区域 -->
      <div v-if="courseInfo" class="course-content">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 课时列表 -->
          <el-tab-pane label="课时列表" name="lessons">
            <div class="lessons-section">
              <div class="section-header">
                <h4>课时列表 ({{ lessonsList.length }}个课时)</h4>
                <el-text v-if="!isEnrolled" type="warning">请先选课后查看详细内容</el-text>
              </div>
              
              <el-table :data="lessonsList" v-loading="lessonsLoading" style="width: 100%">
                <el-table-column prop="lessonId" label="课时编号" width="100" />
                <el-table-column prop="lessonName" label="课时名称" />
                <el-table-column prop="createTime" label="创建时间" width="180" />
                
                <!-- 已选课学生显示详细状态 -->
                <template v-if="isEnrolled">
                  <el-table-column label="测试状态" width="120">
                    <template #default="scope">
                      <el-tag :type="getTestPublishStatusType(scope.row)">
                        {{ getTestPublishStatusText(scope.row) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="完成状态" width="120">
                    <template #default="scope">
                      <el-tag 
                        v-if="scope.row.hasQuestion === 1"
                        :type="getTestCompletionStatusType(scope.row)"
                      >
                        {{ getTestCompletionStatusText(scope.row) }}
                      </el-tag>
                      <span v-else class="text-muted">-</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="200">
                  <template #default="scope">
                      <!-- 已发布的测试 -->
                      <template v-if="scope.row.hasQuestion === 1">
                        <!-- 课程进行中：未完成的测试可以参加 -->
                        <template v-if="courseInfo?.isOver === 0">
                          <el-button 
                            v-if="!scope.row.isCompleted"
                            size="small" 
                            type="success"
                            @click="takeTest(scope.row)"
                          >
                            参加测试
                          </el-button>
                          
                          <el-button 
                            v-else
                            size="small" 
                            type="primary"
                            @click="viewTestResult(scope.row)"
                          >
                            查看测试
                          </el-button>
                        </template>
                        
                        <!-- 课程已结课：未完成的测试只能查看题目，已完成的可以查看结果 -->
                        <template v-else-if="courseInfo?.isOver === 1">
                          <el-button 
                            v-if="!scope.row.isCompleted"
                            size="small" 
                            type="info"
                            @click="viewTestQuestions(scope.row)"
                          >
                            查看题目与解析
                          </el-button>
                          
                          <el-button 
                            v-else
                            size="small" 
                            type="primary"
                            @click="viewTestResult(scope.row)"
                          >
                            查看测试
                          </el-button>
                        </template>
                      </template>
                      
                      <!-- 没有测试的课时显示提示 -->
                      <span v-else class="text-muted">暂无测试</span>
                    </template>
                  </el-table-column>
                </template>
                
                <!-- 未选课学生只显示基本信息 -->
                <template v-else>
                  <el-table-column label="测试状态" width="120">
                    <template #default="scope">
                      <el-tag :type="getTestPublishStatusType(scope.row)">
                        {{ getTestPublishStatusText(scope.row) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="200">
                    <template #default="scope">
                      <el-text type="info" size="small">请先选课</el-text>
                  </template>
                </el-table-column>
                </template>
              </el-table>
              
              <!-- 空状态 -->
              <el-empty 
                v-if="!lessonsLoading && lessonsList.length === 0"
                description="暂无课时信息"
                :image-size="100"
              />
            </div>
          </el-tab-pane>
          

          <!-- 课程资料（仅已选课学生可见） -->
          <el-tab-pane v-if="isEnrolled" label="课程资料" name="materials">
            <div class="materials-section">
              <div class="section-header">
                <h4>课程资料</h4>
                <el-button @click="loadCourseMaterials" :loading="courseMaterialsLoading">
                  刷新资料
                </el-button>
              </div>
              
              <!-- 课程资料列表 -->
              <div v-if="courseMaterialsList.length > 0" class="materials-list">
                <el-table :data="courseMaterialsList" v-loading="courseMaterialsLoading" style="width: 100%">
                  <el-table-column prop="filename" label="文件名" />
                  <el-table-column prop="size" label="文件大小" width="120">
                    <template #default="scope">
                      {{ formatFileSize(scope.row.size) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="created_time" label="上传时间" width="180" />
                  <el-table-column label="操作" width="120">
                    <template #default="scope">
                      <el-button 
                        type="primary" 
                        size="small" 
                        @click="downloadCourseMaterial(scope.row)"
                      >
                        下载
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              
              <!-- 空状态 -->
              <div v-else-if="!courseMaterialsLoading" class="empty-materials">
                <el-empty description="暂无课程资料">
                  <template #description>
                    <span>教师尚未上传课程资料</span>
                  </template>
                </el-empty>
              </div>
            </div>
          </el-tab-pane>

          <!-- 学习记录（仅已选课学生可见） -->
          <el-tab-pane v-if="isEnrolled" label="学习记录" name="progress">
            <div class="progress-section">
              <h4>学习进度</h4>
              
              <!-- 测试成绩统计 -->
              <el-row :gutter="20" style="margin-bottom: 20px;">
                <el-col :span="6">
                  <el-statistic title="已完成测试" :value="completedTests" suffix="个" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="待完成测试" :value="pendingTests" suffix="个" />
                </el-col>
                <el-col :span="6">
                  <!-- 只有课程已结课时才显示平均成绩 -->
                  <div v-if="courseInfo?.isOver === 1">
                    <el-statistic title="课程成绩" :value="averageScore" suffix="分" />
                  </div>
                  <div v-else class="score-placeholder">
                    <div class="placeholder-title">课程成绩</div>
                    <div class="placeholder-text">课程未结课</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <el-statistic title="学习进度" :value="studyProgress" suffix="%" />
                </el-col>
              </el-row>
              
              <!-- 成绩趋势图 -->
              <div class="score-trend-section">
                <div class="section-header">
                  <h5>课时成绩变化趋势</h5>
                  <el-button 
                    @click="loadScoreTrend" 
                    :loading="scoreTrendLoading"
                    size="small"
                  >
                    刷新数据
                  </el-button>
                </div>
                
                <!-- 成绩趋势图 -->
                <div v-if="scoreTrendData.length > 0" class="trend-chart-container">
                  <div ref="scoreTrendChart" style="width: 100%; height: 400px;"></div>
                </div>
                
                <!-- 空状态 -->
                <div v-else-if="!scoreTrendLoading" class="empty-trend">
                  <el-empty description="暂无成绩数据">
                    <template #description>
                      <span>您还没有完成任何测试，完成测试后可查看成绩趋势</span>
                    </template>
                  </el-empty>
                </div>
                
                <!-- 加载状态 -->
                <div v-else class="trend-loading">
                  <el-skeleton :rows="3" animated />
                </div>
              </div>
              
              <!-- 详细成绩记录 -->
              <div class="score-records-section">
                <div class="section-header">
                  <h5>详细成绩记录</h5>
                </div>
                
                <el-table 
                  :data="scoreTrendData" 
                  v-loading="scoreTrendLoading"
                  style="width: 100%"
                >
                  <el-table-column prop="lessonId" label="课时编号" width="100" />
                  <el-table-column label="课时名称" min-width="200">
                    <template #default="scope">
                      {{ getLessonName(scope.row.lessonId) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="score" label="成绩" width="100" align="center">
                    <template #default="scope">
                      <el-tag 
                        :type="getScoreType(scope.row.score)"
                        size="large"
                      >
                        {{ scope.row.score }}分
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="等级" width="100" align="center">
                    <template #default="scope">
                      <el-tag 
                        :type="getGradeType(scope.row.score)"
                        size="large"
                      >
                        {{ getGrade(scope.row.score) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="updateTime" label="提交时间" width="180" />
                </el-table>
                
                <!-- 空状态 -->
                <el-empty 
                  v-if="!scoreTrendLoading && scoreTrendData.length === 0"
                  description="暂无成绩记录"
                  :image-size="100"
                />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="8" animated />
      </div>
    </el-card>
    
    <!-- 测试结果详情对话框 -->
    <el-dialog 
      v-model="showTestResultDialog" 
      title="测试结果详情" 
      width="90%"
      :before-close="handleCloseDialog"
    >
      <div v-if="currentTestResult">
        <!-- 测试概要 -->
        <div class="test-summary">
          <h4>{{ currentTestResult.lesson.lessonName }} - 测试结果</h4>
          <el-row :gutter="20" style="margin: 20px 0;">
            <el-col :span="6">
              <el-statistic title="总题数" :value="currentTestResult.totalCount" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="正确数" :value="currentTestResult.correctCount" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="正确率" :value="Math.round((currentTestResult.correctCount / currentTestResult.totalCount) * 100)" suffix="%" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="得分" :value="currentTestResult.score" suffix="分" />
            </el-col>
          </el-row>
        </div>
        
        <!-- 详细答题记录 -->
        <div class="test-details">
          <h5>详细答题记录</h5>
          <el-table 
            :data="currentTestResult.records" 
            style="width: 100%"
            :row-class-name="getRowClassName"
          >
            <!-- 展开行 -->
            <el-table-column type="expand" width="50">
              <template #default="props">
                <div class="expand-content">
                  <div class="question-analysis">
                    <h6>题目解析</h6>
                    <div class="analysis-content">
                      <p v-if="props.row.questionDetails?.explanation" class="analysis-text">
                        {{ props.row.questionDetails.explanation }}
                      </p>
                      <p v-else class="no-analysis">暂无解析</p>
                    </div>
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <!-- 题目序号 -->
            <el-table-column label="题号" width="60" align="center">
              <template #default="scope">
                <span class="question-number">{{ scope.$index + 1 }}</span>
              </template>
            </el-table-column>
            
            <!-- 题目内容 -->
            <el-table-column label="题目内容" min-width="300">
              <template #default="scope">
                <div class="question-content">
                  <p class="question-text">{{ scope.row.questionDetails?.question || '题目信息加载中...' }}</p>
                  <div class="question-options" v-if="scope.row.questionDetails?.options && getQuestionOptions(scope.row.questionDetails.options).length > 0">
                    <div 
                      class="option-item"
                      v-for="option in getQuestionOptions(scope.row.questionDetails.options)" 
                      :key="option.label"
                    >
                      <span class="option-label">{{ option.label }}.</span>
                      <span class="option-text">{{ option.text }}</span>
                    </div>
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <!-- 您的答案 -->
            <el-table-column label="您的答案" width="100" align="center">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.isCorrect === 1 ? 'success' : 'danger'"
                  size="large"
                  class="answer-tag"
                >
                  {{ scope.row.selectedOption }}
                </el-tag>
              </template>
            </el-table-column>
            
            <!-- 正确答案 -->
            <el-table-column label="正确答案" width="100" align="center">
              <template #default="scope">
                <el-tag 
                  type="success" 
                  size="large"
                  class="answer-tag"
                >
                  {{ scope.row.questionDetails?.answer || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <!-- 结果 -->
            <el-table-column label="结果" width="80" align="center">
              <template #default="scope">
                <div class="result-indicator">
                  <el-icon v-if="scope.row.isCorrect === 1" color="#67c23a" size="20">
                    <Check />
                  </el-icon>
                  <el-icon v-else color="#f56c6c" size="20">
                    <Close />
                  </el-icon>
                </div>
              </template>
            </el-table-column>
            
            <!-- 提交时间 -->
            <el-table-column label="提交时间" width="150">
              <template #default="scope">
                <span class="submit-time">
                  {{ formatSubmitTime(scope.row.submitTime) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 提示信息 -->
        <div class="test-tip">
          <el-alert
            title="提示"
            description="点击每行左侧的展开按钮可查看题目解析"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="showTestResultDialog = false">
            <el-icon><Check /></el-icon>
            确认
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'
import request from '@/utils/request'
import axios from 'axios'
import { dismissCourse as dismissCourseAPI } from '@/api/course'
import { getLessonRecords, getLessonQuestionsList } from '@/api/course/lesson'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const courseInfo = ref(null)
const activeTab = ref('lessons')
const isEnrolled = ref(false)
const enrolling = ref(false)
const studentCount = ref(0)

// 课时相关
const lessonsList = ref([])
const lessonsLoading = ref(false)

// 学习进度统计
const completedTests = ref(0)
const pendingTests = ref(0)
const averageScore = ref(0)
const studyProgress = ref(0)

// 测试结果对话框
const showTestResultDialog = ref(false)
const currentTestResult = ref(null)

// 课程资料相关
const courseMaterialsList = ref([])
const courseMaterialsLoading = ref(false)

// 成绩趋势相关
const scoreTrendData = ref([])
const scoreTrendLoading = ref(false)
const scoreTrendChart = ref(null)

// 计算属性
const getStatusTitle = () => {
  if (!courseInfo.value) return ''
  
  if (isEnrolled.value) {
    return courseInfo.value.isOver === 0 ? '您已选择此课程' : '课程已结束'
  } else {
    return courseInfo.value.isOver === 0 ? '可选择的课程' : '课程已结束'
  }
}

const getStatusType = () => {
  if (!courseInfo.value) return 'info'
  
  if (courseInfo.value.isOver === 1) return 'info'
  return isEnrolled.value ? 'success' : 'warning'
}

const getStatusDescription = () => {
  if (!courseInfo.value) return ''
  
  if (courseInfo.value.isOver === 1) {
    return isEnrolled.value ? '课程已结束，您可以查看学习记录' : '此课程已结束，无法选课'
  }
  
  if (isEnrolled.value) {
    return '您可以查看课时内容、参加测试并跟踪学习进度'
  } else {
    return '选课后即可查看课时内容、参加测试'
  }
}

// 测试发布状态相关方法（简化为两种状态）
const getTestPublishStatusType = (lesson) => {
  // 对学生来说，只关心是否已发布
  return lesson.hasQuestion === 1 ? 'success' : 'info'
}

const getTestPublishStatusText = (lesson) => {
  // 对学生来说，只显示已发布或未发布
  return lesson.hasQuestion === 1 ? '已发布' : '未发布'
}

// 测试完成状态相关方法
const getTestCompletionStatusType = (lesson) => {
  return lesson.isCompleted ? 'success' : 'warning'
}

const getTestCompletionStatusText = (lesson) => {
  return lesson.isCompleted ? '已完成' : '未完成'
}

// API 方法
const getCourseById = async (courseId) => {
  try {
    const res = await request.get('/api/course/findOne', {
      params: { courseId }
    })
    

    
    if (res.code === 0) {
      return res.data
    } else {
      throw new Error(res.message || '获取课程信息失败')
    }
  } catch (error) {
    console.error('获取课程信息失败:', error)
    throw error
  }
}

const checkEnrollmentStatus = async (courseId) => {
  try {
    const res = await request.get('/api/enroll/list/student', {
      params: { studentId: authStore.user?.id }
    })
    
    if (res.code === 0 && res.data) {
      const enrolledCourses = res.data
      return enrolledCourses.some(item => item.course.id === parseInt(courseId))
    }
    return false
  } catch (error) {
    console.error('检查选课状态失败:', error)
    return false
  }
}

const getStudentCount = async (courseId) => {
  try {
    const res = await request.get('/api/enroll/list/course', {
      params: { courseId }
    })
    
    if (res.code === 0 && res.data) {
      return res.data.length
    }
    return 0
  } catch (error) {
    console.error('获取选课人数失败:', error)
    return 0
  }
}

const getLessonsList = async (courseId) => {
  try {
    lessonsLoading.value = true
    const res = await request.get('/api/lesson/list', {
      params: { courseId }
    })
    
    if (res.code === 0) {
      lessonsList.value = res.data || []
      
      // 如果学生已选课，获取每个课时的完成状态
      if (isEnrolled.value && authStore.user?.id) {
        await loadLessonsCompletionStatus()
      }
    } else {
      console.error('获取课时列表失败:', res)
    }
  } catch (error) {
    console.error('获取课时列表错误:', error)
  } finally {
    lessonsLoading.value = false
  }
}

// 主要功能方法
const loadCourseInfo = async () => {
  try {
    loading.value = true
    const courseId = route.params.id
    
    // 验证课程ID
    if (!courseId) {
      ElMessage.error('课程ID不能为空')
      router.push('/dashboard/student/my-courses')
      return
    }
    

    
    // 并行加载课程信息、选课状态、选课人数
    const [courseData, enrolledStatus, stuCount] = await Promise.all([
      getCourseById(courseId),
      checkEnrollmentStatus(courseId),
      getStudentCount(courseId)
    ])
    
    // 检查课程是否存在
    if (!courseData) {
      ElMessage.error('课程不存在或已删除')
      router.push('/dashboard/student/my-courses')
      return
    }
    
    courseInfo.value = courseData
    isEnrolled.value = enrolledStatus
    studentCount.value = stuCount
    

    
    // 加载课时列表
    await getLessonsList(courseId)
    
    // 如果已选课，加载学习进度数据和课程资料
    if (isEnrolled.value) {
      await loadStudyProgress()
      await loadCourseMaterials()
      await loadScoreTrend()
    }
    
  } catch (error) {
    console.error('加载课程信息失败:', error)
    ElMessage.error('加载课程信息失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadStudyProgress = async () => {
  try {
    // 根据课时列表计算统计数据
    const publishedTests = lessonsList.value.filter(l => l.hasQuestion === 1)
    const completedTestsCount = publishedTests.filter(l => l.isCompleted).length
    
    // 更新统计数据
    completedTests.value = completedTestsCount
    pendingTests.value = publishedTests.length - completedTestsCount
    studyProgress.value = publishedTests.length > 0 
      ? Math.round((completedTestsCount / publishedTests.length) * 100)
      : 0
    
    // 只有在课程已结课时才获取课程总成绩
    if (courseInfo.value?.isOver === 1 && authStore.user?.id && courseInfo.value?.id) {
      const courseScore = await getStudentCourseScore(courseInfo.value.id, authStore.user.id)
      averageScore.value = courseScore
    } else {
      averageScore.value = 0
    }
    
  } catch (error) {
    console.error('加载学习进度失败:', error)
  }
}

const enrollCourse = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要选择课程 "${courseInfo.value.name || courseInfo.value.courseName}" 吗？`,
      '确认选课',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    enrolling.value = true
    
    const res = await request.post('/api/enroll', null, {
      params: {
        courseId: courseInfo.value.id
      }
    })
    
    if (res.code === 0) {
      ElMessage.success('选课成功！')
      isEnrolled.value = true
      studentCount.value += 1
      
      // 重新加载课时完成状态、学习进度和课程资料
      if (lessonsList.value.length > 0) {
        await loadLessonsCompletionStatus()
        await loadStudyProgress()
        await loadCourseMaterials()
      }
    } else {
      ElMessage.error(res.message || '选课失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('选课失败:', error)
      ElMessage.error('选课失败，请稍后重试')
    }
  } finally {
    enrolling.value = false
  }
}

const dismissCourse = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要退选课程 "${courseInfo.value.name || courseInfo.value.courseName}" 吗？`,
      '确认退选',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await dismissCourseAPI(authStore.user?.id, courseInfo.value.id)
    
    if (res.code === 0) {
      ElMessage.success('退选成功')
      isEnrolled.value = false
      studentCount.value = Math.max(0, studentCount.value - 1)
      
      // 清空学习进度数据和课程资料
      completedTests.value = 0
      pendingTests.value = 0
      averageScore.value = 0
      studyProgress.value = 0
      courseMaterialsList.value = []
    } else {
      ElMessage.error(res.message || '退选失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('退选失败:', error)
      ElMessage.error('退选失败，请稍后重试')
    }
  }
}



const takeTest = (lesson) => {
  const courseId = route.params.id;
  const lessonId = lesson.lessonId;
  
  console.log('参加测试 - 详细信息:', { 
    courseId, 
    lessonId, 
    lesson,
    routeParams: route.params,
    currentPath: route.path 
  });
  
  // 检查必要参数
  if (!courseId) {
    ElMessage.error('缺少课程ID参数');
    return;
  }
  
  if (!lessonId) {
    ElMessage.error('缺少课时ID参数');
    return;
  }
  
  // 跳转到学生做题页面
  const routeConfig = {
    name: 'student-questions',
    params: {
      courseId: courseId,
      lessonId: lessonId
    }
  };
  
  router.push(routeConfig).catch(error => {
    console.error('路由跳转失败:', error);
    ElMessage.error(`跳转失败: ${error.message}`);
  });
}

// 获取学生做题记录
const getStudentRecords = async (lessonId, studentId) => {
  try {
    // 获取测试记录
    const recordsRes = await getLessonRecords(lessonId, studentId)
    
    if (recordsRes.code === 0 && recordsRes.data) {
      // 获取题目详情
      const questionsRes = await getLessonQuestionsList(lessonId)
      
      if (questionsRes.code === 0 && questionsRes.data) {
        // 将记录和题目详情合并
        const mergedRecords = recordsRes.data.map(record => {
          const question = questionsRes.data.find(q => q.questionId === record.questionId)
          return {
            ...record,
            questionDetails: question || null
          }
        })
        
        return mergedRecords
      }
      
      return recordsRes.data
    }
    return []
  } catch (error) {
    console.error('获取做题记录失败:', error)
    return []
  }
}

// 获取学生课程成绩
const getStudentCourseScore = async (courseId, studentId) => {
  try {
    const res = await request.get('/api/course/score', {
      params: { courseId, studentId }
    })
    
    if (res.code === 0) {
      const score = res.data || 0
      return Number(score) // 确保返回数字类型
    }
    return 0
  } catch (error) {
    console.error('获取课程成绩失败:', error)
    return 0
  }
}

// 加载课程资料列表
const loadCourseMaterials = async () => {
  try {
    courseMaterialsLoading.value = true
    
    const courseId = route.params.id
    
    // 检查参数是否有效
    if (!courseId) {
      ElMessage.error('课程信息获取失败')
      return
    }
    
    if (!courseInfo.value?.teacherId) {
      ElMessage.error('教师信息获取失败')
      return
    }
    
    // 学生端使用教师的用户ID来访问课程资料，因为文件是教师上传的
    const teacherId = courseInfo.value.teacherId
    
    // 调用AI端API获取课程资料列表，使用教师ID并设置 is_teacher=true
    const response = await axios.get(`/ai/v1/list/resources/${teacherId}/${courseId}?is_teacher=true`)
    
    const result = response.data
    
    if (result.files) {
      courseMaterialsList.value = result.files
    } else {
      courseMaterialsList.value = []
    }
  } catch (error) {
    console.error('加载课程资料列表失败:', error)
    courseMaterialsList.value = []
    ElMessage.error('加载课程资料列表失败')
  } finally {
    courseMaterialsLoading.value = false
  }
}

// 下载课程资料
const downloadCourseMaterial = async (file) => {
  try {
    // 学生端使用教师的用户ID来下载课程资料，因为文件是教师上传的
    const teacherId = courseInfo.value?.teacherId
    const courseId = route.params.id
    
    if (!teacherId) {
      ElMessage.error('教师信息获取失败')
      return
    }
    
    // 使用教师ID下载，设置 is_teacher=true
    const downloadUrl = `/ai/v1/download/resource/${teacherId}/${courseId}/${file.filename}?is_teacher=true`
    

    
    // 创建一个隐藏的a标签来下载文件
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = file.filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('开始下载文件')
  } catch (error) {
    console.error('下载课程资料失败:', error)
    ElMessage.error('下载失败，请重试')
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 加载所有课时的完成状态
const loadLessonsCompletionStatus = async () => {
  if (!authStore.user?.id) return
  
  try {
    // 并行获取所有已发布测试课时的做题记录
    const publishedLessons = lessonsList.value.filter(lesson => lesson.hasQuestion === 1)
    
    const recordsPromises = publishedLessons.map(lesson => 
      getStudentRecords(lesson.lessonId, authStore.user.id)
    )
    
    const recordsResults = await Promise.all(recordsPromises)
    
    // 更新课时完成状态
    lessonsList.value = lessonsList.value.map(lesson => {
      if (lesson.hasQuestion === 1) {
        const lessonIndex = publishedLessons.findIndex(l => l.lessonId === lesson.lessonId)
        const records = recordsResults[lessonIndex] || []
        
        return {
          ...lesson,
          isCompleted: records.length > 0,
          records: records // 保存记录用于查看结果
        }
      }
      return {
        ...lesson,
        isCompleted: false,
        records: []
      }
    })
    
  } catch (error) {
    console.error('加载课时完成状态失败:', error)
  }
}

const viewTestResult = (lesson) => {
  if (lesson.records && lesson.records.length > 0) {
    showTestResultDialog.value = true
    currentTestResult.value = {
      lesson,
      records: lesson.records,
      correctCount: lesson.records.filter(r => r.isCorrect === 1).length,
      totalCount: lesson.records.length
    }
    
    const score = currentTestResult.value.totalCount > 0 
      ? Math.round((currentTestResult.value.correctCount / currentTestResult.value.totalCount) * 100) 
      : 0
    currentTestResult.value.score = score
    

  } else {
    ElMessage.warning('未找到测试记录')
  }
}

const viewTestQuestions = (lesson) => {
  const courseId = route.params.id;
  const lessonId = lesson.lessonId;
  
  console.log('查看测试题 - 详细信息:', { 
    courseId, 
    lessonId, 
    lesson,
    routeParams: route.params,
    currentPath: route.path 
  });
  
  // 检查必要参数
  if (!courseId) {
    ElMessage.error('缺少课程ID参数');
    return;
  }
  
  if (!lessonId) {
    ElMessage.error('缺少课时ID参数');
    return;
  }
  
  // 跳转到查看测试题页面（只读模式）
  const routeConfig = {
    name: 'student-questions',
    params: {
      courseId: courseId,
      lessonId: lessonId
    },
    query: {
      readonly: 'true' // 添加只读模式参数
    }
  };
  
  router.push(routeConfig).catch(error => {
    console.error('路由跳转失败:', error);
    ElMessage.error(`跳转失败: ${error.message}`);
  });
}

// 对话框关闭处理
const handleCloseDialog = (done) => {
  done()
}

// 表格行类名
const getRowClassName = ({ row }) => {
  if (row.isCorrect === 1) {
    return 'success-row'
  } else {
    return 'error-row'
  }
}

// 格式化提交时间
const formatSubmitTime = (timeString) => {
  if (!timeString) return '未知'
  
  try {
    const date = new Date(timeString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return timeString
  }
}

// 获取题目选项（兼容不同的数据格式）
const getQuestionOptions = (question) => {
  const options = []
  
  // 检查新格式：options 对象
  if (question.options && typeof question.options === 'object') {
    // 如果 options 是对象，尝试解析
    try {
      let optionsData = question.options
      
      // 如果是字符串，尝试解析为JSON
      if (typeof optionsData === 'string') {
        optionsData = JSON.parse(optionsData)
      }
      
      // 检查是否有 A, B, C, D 属性
      if (optionsData.A) options.push({ label: 'A', text: optionsData.A })
      if (optionsData.B) options.push({ label: 'B', text: optionsData.B })
      if (optionsData.C) options.push({ label: 'C', text: optionsData.C })
      if (optionsData.D) options.push({ label: 'D', text: optionsData.D })
      
    } catch (error) {
      console.error('解析选项失败:', error)
    }
  }
  
  // 如果新格式没有找到选项，检查旧格式：optionA, optionB 等
  if (options.length === 0) {
    if (question.optionA) options.push({ label: 'A', text: question.optionA })
    if (question.optionB) options.push({ label: 'B', text: question.optionB })
    if (question.optionC) options.push({ label: 'C', text: question.optionC })
    if (question.optionD) options.push({ label: 'D', text: question.optionD })
  }
  
  return options
}

// 成绩趋势相关方法
const loadScoreTrend = async () => {
  if (!isEnrolled.value || !authStore.user?.id || !courseInfo.value?.id) {
    scoreTrendData.value = []
    return
  }
  
  try {
    scoreTrendLoading.value = true
    
    const result = await request.get('/api/course/scoreList', {
      params: {
        courseId: courseInfo.value.id,
        studentId: authStore.user.id
      }
    })
    
    if (result.code === 0 && result.data) {
      scoreTrendData.value = result.data
      // 如果当前在学习记录标签页，渲染折线图
      if (activeTab.value === 'progress') {
        nextTick(() => {
          renderScoreChart()
        })
      }
    } else {
      scoreTrendData.value = []
    }
  } catch (error) {
    console.error('获取学生成绩趋势失败:', error)
    scoreTrendData.value = []
  } finally {
    scoreTrendLoading.value = false
  }
}

// 渲染成绩趋势折线图
const renderScoreChart = () => {
  if (!scoreTrendChart.value || scoreTrendData.value.length === 0) {
    return
  }
  
  // 准备图表数据
  const chartData = scoreTrendData.value.map(item => ({
    lessonId: item.lessonId,
    score: item.score || 0,
    updateTime: item.updateTime
  }))
  
  // 按课时ID排序
  chartData.sort((a, b) => a.lessonId - b.lessonId)
  
  // 获取课时名称映射
  const lessonNames = lessonsList.value.reduce((map, lesson) => {
    map[lesson.lessonId] = lesson.lessonName
    return map
  }, {})
  
  // 构建图表配置
  const option = {
    title: {
      text: '我的课时成绩趋势',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        return `课时: ${lessonNames[data.dataIndex] || data.dataIndex}<br/>成绩: ${data.value}分`
      }
    },
    xAxis: {
      type: 'category',
      data: chartData.map(item => lessonNames[item.lessonId] || `课时${item.lessonId}`),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      name: '成绩(分)'
    },
    series: [{
      name: '成绩',
      type: 'line',
      data: chartData.map(item => item.score),
      smooth: true,
      lineStyle: {
        color: '#409EFF',
        width: 3
      },
      itemStyle: {
        color: '#409EFF',
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(64, 158, 255, 0.3)'
          }, {
            offset: 1, color: 'rgba(64, 158, 255, 0.1)'
          }]
        }
      }
    }]
  }
  
  // 使用ECharts渲染图表
  const chart = echarts.init(scoreTrendChart.value)
  chart.setOption(option)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 获取课时名称
const getLessonName = (lessonId) => {
  const lesson = lessonsList.value.find(l => l.lessonId === lessonId)
  return lesson ? lesson.lessonName : `课时${lessonId}`
}

// 获取成绩等级
const getGrade = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '不及格'
}

// 获取成绩等级类型
const getGradeType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'success'
  if (score >= 70) return 'warning'
  if (score >= 60) return 'info'
  return 'danger'
}

// 获取成绩标签类型
const getScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'success'
  if (score >= 70) return 'warning'
  if (score >= 60) return 'info'
  return 'danger'
}

// 监听标签页切换，重新渲染图表
watch(activeTab, (newTab) => {
  if (newTab === 'progress' && scoreTrendData.value.length > 0) {
    nextTick(() => {
      renderScoreChart()
    })
  }
})

// 页面初始化
onMounted(() => {
  loadCourseInfo()
})
</script>

<style scoped>
.course-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.course-status {
  margin-bottom: 20px;
}

.course-info {
  margin-bottom: 20px;
}

.course-content {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
}

.lessons-section,
.progress-section,
.materials-section {
  padding: 20px 0;
}

.not-enrolled-tip {
  margin: 20px 0;
}

.loading-state {
  padding: 40px 20px;
}

/* 统计数据样式 */
:deep(.el-statistic__content) {
  color: #409eff;
}

:deep(.el-statistic__number) {
  font-size: 24px;
  font-weight: 600;
}

/* 成绩占位符样式 */
.score-placeholder {
  text-align: center;
}

.placeholder-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.placeholder-text {
  font-size: 20px;
  color: #909399;
  font-weight: 500;
}

/* 表格样式 */
.text-muted {
  color: #909399;
  font-size: 14px;
}

/* 课时操作按钮样式 */
.course-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 测试结果对话框样式 */
.test-summary {
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
}

.test-summary h4 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
  text-align: center;
}

.test-details {
  margin-bottom: 20px;
}

.test-details h5 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.test-tip {
  margin-top: 20px;
}

/* 表格行样式 */
:deep(.success-row) {
  background-color: #f0f9ff;
}

:deep(.error-row) {
  background-color: #fef2f2;
}

/* 展开内容样式 */
.expand-content {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.question-analysis h6 {
  margin: 0 0 15px 0;
  color: #409eff;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.question-analysis h6:before {
  content: "💡";
  font-size: 18px;
}

.analysis-content {
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.analysis-text {
  margin: 0;
  line-height: 1.6;
  color: #333;
  font-size: 14px;
}

.no-analysis {
  margin: 0;
  color: #909399;
  font-style: italic;
  font-size: 14px;
}

/* 题目内容样式 */
.question-content {
  padding: 8px 0;
}

.question-text {
  margin: 0 0 12px 0;
  font-weight: 600;
  color: #303133;
  line-height: 1.6;
}

.question-options {
  margin-top: 8px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  margin: 4px 0;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: #f5f7fa;
}

.option-label {
  font-weight: 600;
  color: #409eff;
  margin-right: 8px;
  min-width: 20px;
}

.option-text {
  color: #606266;
  line-height: 1.4;
}

/* 答案标签样式 */
.answer-tag {
  font-weight: 600;
  font-size: 14px;
}

/* 题目序号样式 */
.question-number {
  font-weight: 600;
  color: #409eff;
  font-size: 16px;
}

/* 结果指示器样式 */
.result-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 提交时间样式 */
.submit-time {
  font-size: 12px;
  color: #909399;
}

/* 对话框底部样式 */
.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* 课程资料样式 */
.materials-list {
  margin-top: 20px;
}

.empty-materials {
  margin-top: 20px;
  padding: 40px;
  text-align: center;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

/* 成绩趋势样式 */
.score-trend-section {
  margin: 30px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.score-trend-section .section-header {
  margin-bottom: 20px;
}

.score-trend-section .section-header h5 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.trend-chart-container {
  margin-top: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-trend {
  margin-top: 20px;
  padding: 40px;
  text-align: center;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.trend-loading {
  margin-top: 20px;
  padding: 20px;
}

.score-records-section {
  margin-top: 30px;
}

.score-records-section .section-header {
  margin-bottom: 20px;
}

.score-records-section .section-header h5 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .course-detail-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
  }
  
  .section-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  /* 移动端表格适配 */
  :deep(.el-table .el-table__cell) {
    padding: 8px 4px;
  }
  
  /* 测试结果对话框移动端适配 */
  .test-summary {
    padding: 15px;
  }
  
  .test-summary h4 {
    font-size: 18px;
  }
  
  .expand-content {
    padding: 15px;
  }
  
  .question-content {
    padding: 6px 0;
  }
  
  .question-text {
    font-size: 14px;
  }
  
  .option-item {
    padding: 3px 6px;
    margin: 2px 0;
  }
  
  .option-text {
    font-size: 13px;
  }
  
  .answer-tag {
    font-size: 12px;
  }
  
  .question-number {
    font-size: 14px;
  }
  
  /* 成绩占位符移动端适配 */
  .score-placeholder {
    padding: 10px 0;
  }
  
  .placeholder-title {
    font-size: 12px;
  }
  
  .placeholder-text {
    font-size: 16px;
  }
}
</style> 