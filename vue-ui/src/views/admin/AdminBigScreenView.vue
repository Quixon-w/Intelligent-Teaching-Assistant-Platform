<template>
  <div class="admin-big-screen">
    <!-- 页面头部 -->
    <div class="header">
      <div class="header-left">
        <h1>管理员大屏概览</h1>
        <p class="subtitle">实时监控教学系统运行状态</p>
      </div>
      <div class="header-right">
        <el-radio-group v-model="period" size="large" class="period-switch">
          <el-radio-button label="today">当日</el-radio-button>
          <el-radio-button label="week">本周</el-radio-button>
          <el-radio-button label="month">本月</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 系统总览 -->
    <el-row :gutter="24" class="overview-section">
      <el-col :span="24">
        <el-card class="overview-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>系统总览</h2>
              <span class="update-time">最后更新：{{ lastUpdateTime }}</span>
            </div>
          </template>
          <div class="overview-stats">
            <div class="stat-item">
              <el-statistic title="总课程数" :value="overview.totalCourses || 0">
                <template #prefix>
                  <el-icon><Reading /></el-icon>
                </template>
              </el-statistic>
            </div>
            <div class="stat-item">
              <el-statistic title="总教师数" :value="overview.totalTeachers || 0">
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-statistic>
            </div>
            <div class="stat-item">
              <el-statistic title="总学生数" :value="overview.totalStudents || 0">
                <template #prefix>
                  <el-icon><UserFilled /></el-icon>
                </template>
              </el-statistic>
            </div>
            <div class="stat-item">
              <el-statistic title="今日活跃用户" :value="overview.todayActiveUsers || 0">
                <template #prefix>
                  <el-icon><View /></el-icon>
                </template>
              </el-statistic>
            </div>
            <div class="stat-item">
              <el-statistic title="本月活跃用户" :value="overview.monthActiveUsers || 0">
                <template #prefix>
                  <el-icon><TrendCharts /></el-icon>
                </template>
              </el-statistic>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 使用统计区域 -->
    <el-row :gutter="24" class="section-row">
      <!-- 教师使用统计 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>教师使用统计</h2>
              <el-tag type="success">{{ teacherUsage.activeTeacherCount || 0 }} 位活跃教师</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div class="chart-summary">
              <div class="summary-item">
                <span class="label">总使用次数</span>
                <span class="value">{{ teacherUsage.totalUsageCount || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="label">平均使用次数</span>
                <span class="value">{{ (teacherUsage.averageUsageCount || 0).toFixed(1) }}</span>
              </div>
            </div>
            <div ref="teacherChart" class="chart"></div>
            <div class="active-modules">
              <h4>活跃板块分布</h4>
              <div class="module-list">
                <div v-for="module in teacherUsage.activeModules" :key="module.moduleType" class="module-item">
                  <span class="module-name">{{ module.moduleName }}</span>
                  <span class="module-count">{{ module.usageCount }}</span>
                  <span class="module-percent">{{ module.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 学生使用统计 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>学生使用统计</h2>
              <el-tag type="primary">{{ studentUsage.activeStudentCount || 0 }} 位活跃学生</el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div class="chart-summary">
              <div class="summary-item">
                <span class="label">总使用次数</span>
                <span class="value">{{ studentUsage.totalUsageCount || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="label">平均使用次数</span>
                <span class="value">{{ (studentUsage.averageUsageCount || 0).toFixed(1) }}</span>
              </div>
            </div>
            <div ref="studentChart" class="chart"></div>
            <div class="active-modules">
              <h4>活跃板块分布</h4>
              <div class="module-list">
                <div v-for="module in studentUsage.activeModules" :key="module.moduleType" class="module-item">
                  <span class="module-name">{{ module.moduleName }}</span>
                  <span class="module-count">{{ module.usageCount }}</span>
                  <span class="module-percent">{{ module.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 教学效率与学习效果 -->
    <el-row :gutter="24" class="section-row">
      <!-- 教学效率指数 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>教学效率指数</h2>
              <el-tag :type="getEfficiencyTagType(teachingEfficiency.overallEfficiencyIndex)">
                {{ (teachingEfficiency.overallEfficiencyIndex || 0).toFixed(1) }} 分
              </el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="efficiencyChart" class="chart"></div>
            <div class="optimization-suggestions" v-if="teachingEfficiency.optimizationSuggestions?.length">
              <h4>优化建议</h4>
              <div class="suggestion-list">
                <div v-for="suggestion in teachingEfficiency.optimizationSuggestions.slice(0, 3)" 
                     :key="suggestion.courseId" class="suggestion-item">
                  <el-tag :type="getPriorityType(suggestion.priority)" size="small">
                    {{ suggestion.priority === 'high' ? '高' : suggestion.priority === 'medium' ? '中' : '低' }}优先级
                  </el-tag>
                  <span class="course-name">{{ suggestion.courseName }}</span>
                  <span class="issue-desc">{{ suggestion.issueDescription }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 学生学习效果 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>学生学习效果</h2>
              <el-tag :type="getCorrectRateTagType(learningEffectiveness.averageCorrectRate)">
                平均正确率 {{ (learningEffectiveness.averageCorrectRate || 0).toFixed(1) }}%
              </el-tag>
            </div>
          </template>
          <div class="chart-container">
            <div ref="effectivenessChart" class="chart"></div>
            <div class="high-frequency-errors" v-if="learningEffectiveness.highFrequencyErrors?.length">
              <h4>高频错误知识点</h4>
              <div class="error-list">
                <div v-for="error in learningEffectiveness.highFrequencyErrors.slice(0, 3)" 
                     :key="error.knowledgePoint" class="error-item">
                  <span class="knowledge-point">{{ error.knowledgePoint }}</span>
                  <span class="error-rate">错误率 {{ error.errorRate.toFixed(1) }}%</span>
                  <span class="error-count">{{ error.errorCount }} 次</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-row :gutter="24" class="section-row">
      <el-col :span="24">
        <el-card class="table-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h2>详细数据</h2>
              <el-tabs v-model="activeTab" @tab-click="handleTabClick">
                <el-tab-pane label="教师排名" name="teacherRanking"></el-tab-pane>
                <el-tab-pane label="学生排名" name="studentRanking"></el-tab-pane>
                <el-tab-pane label="课程通过率" name="coursePassRate"></el-tab-pane>
              </el-tabs>
            </div>
          </template>
          
          <!-- 教师排名表格 -->
          <el-table v-if="activeTab === 'teacherRanking'" :data="teacherUsage.teacherRankings || []" 
                    stripe style="width: 100%">
            <el-table-column prop="ranking" label="排名" width="80" />
            <el-table-column prop="teacherName" label="教师姓名" />
            <el-table-column prop="usageCount" label="使用次数" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewTeacherDetail(scope.row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 学生排名表格 -->
          <el-table v-if="activeTab === 'studentRanking'" :data="studentUsage.studentRankings || []" 
                    stripe style="width: 100%">
            <el-table-column prop="ranking" label="排名" width="80" />
            <el-table-column prop="studentName" label="学生姓名" />
            <el-table-column prop="usageCount" label="使用次数" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewStudentDetail(scope.row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 课程通过率表格 -->
          <el-table v-if="activeTab === 'coursePassRate'" :data="teachingEfficiency.coursePassRates || []" 
                    stripe style="width: 100%">
            <el-table-column prop="courseName" label="课程名称" />
            <el-table-column prop="passRate" label="通过率">
              <template #default="scope">
                <el-progress :percentage="scope.row.passRate" :color="getPassRateColor(scope.row.passRate)" />
              </template>
            </el-table-column>
            <el-table-column prop="totalStudents" label="总学生数" />
            <el-table-column prop="passedStudents" label="通过学生数" />
            <el-table-column prop="averageScore" label="平均分数">
              <template #default="scope">
                {{ scope.row.averageScore.toFixed(1) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, Reading, User, UserFilled, View, 
  TrendCharts, Document, Trophy 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { 
  getCourseNum,
  getTeacherNum,
  getStudentNum,
  getAdminOverview, 
  getActiveUsersCount,
  getTeacherUsage, 
  getStudentUsage, 
  getTeachingEfficiency, 
  getLearningEffectiveness 
} from '@/api/admin'
import request from '@/utils/request'

// 响应式数据
const period = ref('today')
const loading = ref(false)
const lastUpdateTime = ref('')
const activeTab = ref('teacherRanking')

// 统计数据
const overview = ref({
  totalCourses: 0,
  totalTeachers: 0,
  totalStudents: 0,
  todayActiveUsers: 0,
  monthActiveUsers: 0
})
const teacherUsage = ref({})
const studentUsage = ref({})
const teachingEfficiency = ref({})
const learningEffectiveness = ref({})

// 图表实例
let teacherChart = null
let studentChart = null
let efficiencyChart = null
let effectivenessChart = null

// 获取基础统计数据（使用和管理员页面相同的API）
const fetchBasicStats = async () => {
  try {
    const [courseRes, teacherRes, studentRes] = await Promise.all([
      getCourseNum(),
      getTeacherNum(),
      getStudentNum()
    ])
    
    // 更新基础统计数据
    if (courseRes.code === 0) {
      overview.value.totalCourses = courseRes.data || 0
    }
    if (teacherRes.code === 0) {
      overview.value.totalTeachers = teacherRes.data || 0
    }
    if (studentRes.code === 0) {
      overview.value.totalStudents = studentRes.data || 0
    }
    
  } catch (error) {
    console.error('获取基础统计数据失败:', error)
    ElMessage.error('获取基础统计数据失败')
  }
}

// 获取活跃用户统计
const fetchActiveUsers = async () => {
  try {
    // 获取今日活跃用户
    const todayActiveRes = await getActiveUsersCount('today')
    
    // 获取本月活跃用户
    const monthActiveRes = await getActiveUsersCount('month')
    
    if (todayActiveRes.code === 0) {
      overview.value.todayActiveUsers = todayActiveRes.data || 0
    }
    if (monthActiveRes.code === 0) {
      overview.value.monthActiveUsers = monthActiveRes.data || 0
    }
    
  } catch (error) {
    console.error('获取活跃用户统计失败:', error)
    ElMessage.error('获取活跃用户统计失败')
  }
}

// 获取所有数据
const fetchAll = async () => {
  loading.value = true
  try {
    // 先获取基础统计数据
    await fetchBasicStats()
    
    // 获取活跃用户统计
    await fetchActiveUsers()
    
    // 再获取其他统计数据
    const [t, s, e, l] = await Promise.all([
      getTeacherUsage({ period: period.value }),
      getStudentUsage({ period: period.value }),
      getTeachingEfficiency({ period: period.value }),
      getLearningEffectiveness({ period: period.value })
    ])
    
    teacherUsage.value = t.data || {}
    studentUsage.value = s.data || {}
    teachingEfficiency.value = e.data || {}
    learningEffectiveness.value = l.data || {}
    
    updateLastUpdateTime()
    
    // 等待DOM更新后初始化图表
    await nextTick()
    initCharts()
    
  } catch (err) {
    console.error('获取统计数据失败:', err)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  fetchAll()
}

// 更新最后更新时间
const updateLastUpdateTime = () => {
  const now = new Date()
  lastUpdateTime.value = now.toLocaleString('zh-CN')
}

// 初始化所有图表
const initCharts = () => {
  initTeacherChart()
  initStudentChart()
  initEfficiencyChart()
  initEffectivenessChart()
}

// 初始化教师使用统计图表
const initTeacherChart = () => {
  const chartDom = document.querySelector('.chart-card:first-child .chart')
  if (!chartDom) return
  
  if (teacherChart) {
    teacherChart.dispose()
  }
  
  teacherChart = echarts.init(chartDom)
  
  const option = {
    title: {
      text: '教师使用趋势',
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: teacherUsage.value.usageTrends?.map(item => 
        new Date(item.timePoint).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      ) || []
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: teacherUsage.value.usageTrends?.map(item => item.usageCount) || [],
      type: 'line',
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }
  
  teacherChart.setOption(option)
}

// 初始化学生使用统计图表
const initStudentChart = () => {
  const chartDom = document.querySelector('.chart-card:nth-child(2) .chart')
  if (!chartDom) return
  
  if (studentChart) {
    studentChart.dispose()
  }
  
  studentChart = echarts.init(chartDom)
  
  const option = {
    title: {
      text: '学生使用趋势',
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: studentUsage.value.usageTrends?.map(item => 
        new Date(item.timePoint).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      ) || []
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: studentUsage.value.usageTrends?.map(item => item.usageCount) || [],
      type: 'line',
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      itemStyle: {
        color: '#67C23A'
      }
    }]
  }
  
  studentChart.setOption(option)
}

// 初始化教学效率图表
const initEfficiencyChart = () => {
  const chartDom = document.querySelector('.chart-card:nth-child(3) .chart')
  if (!chartDom) return
  
  if (efficiencyChart) {
    efficiencyChart.dispose()
  }
  
  efficiencyChart = echarts.init(chartDom)
  
  const option = {
    title: {
      text: '教学效率趋势',
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['效率指数', '通过率'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: teachingEfficiency.value.efficiencyTrends?.map(item => 
        item.date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
      ) || []
    },
    yAxis: {
      type: 'value',
      max: 100
    },
    series: [
      {
        name: '效率指数',
        data: teachingEfficiency.value.efficiencyTrends?.map(item => item.efficiencyIndex) || [],
        type: 'line',
        smooth: true,
        itemStyle: { color: '#E6A23C' }
      },
      {
        name: '通过率',
        data: teachingEfficiency.value.efficiencyTrends?.map(item => item.passRate) || [],
        type: 'line',
        smooth: true,
        itemStyle: { color: '#F56C6C' }
      }
    ]
  }
  
  efficiencyChart.setOption(option)
}

// 初始化学习效果图表
const initEffectivenessChart = () => {
  const chartDom = document.querySelector('.chart-card:nth-child(4) .chart')
  if (!chartDom) return
  
  if (effectivenessChart) {
    effectivenessChart.dispose()
  }
  
  effectivenessChart = echarts.init(chartDom)
  
  const option = {
    title: {
      text: '正确率趋势',
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: learningEffectiveness.value.correctRateTrends?.map(item => 
        item.date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
      ) || []
    },
    yAxis: {
      type: 'value',
      max: 100
    },
    series: [{
      data: learningEffectiveness.value.correctRateTrends?.map(item => item.correctRate) || [],
      type: 'line',
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      itemStyle: {
        color: '#909399'
      }
    }]
  }
  
  effectivenessChart.setOption(option)
}

// 工具方法
const getEfficiencyTagType = (efficiency) => {
  if (efficiency >= 80) return 'success'
  if (efficiency >= 60) return 'warning'
  return 'danger'
}

const getCorrectRateTagType = (rate) => {
  if (rate >= 80) return 'success'
  if (rate >= 60) return 'warning'
  return 'danger'
}

const getPriorityType = (priority) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

const getPassRateColor = (rate) => {
  if (rate >= 80) return '#67C23A'
  if (rate >= 60) return '#E6A23C'
  return '#F56C6C'
}

// 事件处理
const handleTabClick = () => {
  // 标签页切换处理
}

const viewTeacherDetail = (teacher) => {
  ElMessage.info(`查看教师 ${teacher.teacherName} 的详细信息`)
}

const viewStudentDetail = (student) => {
  ElMessage.info(`查看学生 ${student.studentName} 的详细信息`)
}

// 监听周期变化
watch(period, () => {
  fetchAll()
})

// 页面加载时获取数据
onMounted(() => {
  fetchAll()
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    if (teacherChart && typeof teacherChart.resize === 'function') {
      teacherChart.resize()
    }
    if (studentChart && typeof studentChart.resize === 'function') {
      studentChart.resize()
    }
    if (efficiencyChart && typeof efficiencyChart.resize === 'function') {
      efficiencyChart.resize()
    }
    if (effectivenessChart && typeof effectivenessChart.resize === 'function') {
      effectivenessChart.resize()
    }
  })
})
</script>

<style scoped>
.admin-big-screen {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.period-switch {
  margin-right: 16px;
}

.overview-section {
  margin-bottom: 24px;
}

.overview-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.overview-card :deep(.el-card__header) {
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.overview-card h2 {
  color: white;
  margin: 0;
}

.update-time {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-top: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.stat-item :deep(.el-statistic__title) {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.stat-item :deep(.el-statistic__number) {
  color: white;
  font-size: 24px;
  font-weight: 600;
}

.section-row {
  margin-bottom: 24px;
}

.chart-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  position: relative;
}

.chart-summary {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.summary-item .value {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.chart {
  height: 300px;
  margin-bottom: 16px;
}

.active-modules h4,
.optimization-suggestions h4,
.high-frequency-errors h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.module-list,
.suggestion-list,
.error-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-item,
.suggestion-item,
.error-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 12px;
}

.module-name,
.course-name,
.knowledge-point {
  flex: 1;
  color: #303133;
}

.module-count,
.issue-desc,
.error-count {
  color: #909399;
  margin-left: 8px;
}

.module-percent,
.error-rate {
  color: #409EFF;
  font-weight: 600;
}

.table-card {
  margin-top: 24px;
}

.table-card :deep(.el-card__header) {
  padding: 16px 20px;
}

.table-card :deep(.el-tabs__header) {
  margin: 0;
}

.table-card :deep(.el-tabs__nav-wrap) {
  padding: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .overview-stats {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
  }
  
  .header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 768px) {
  .admin-big-screen {
    padding: 16px;
  }
  
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .chart-summary {
    flex-direction: column;
    gap: 12px;
  }
  
  .summary-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .summary-item .label {
    margin-bottom: 0;
  }
}
</style> 