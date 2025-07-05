<template>
  <div class="course-selection-gallery">
    <div class="header-section">
      <h2>{{ showHotCourses ? '热门课程' : '课程选择' }}</h2>
      <div class="view-toggle">
        <el-button 
          :type="!showHotCourses ? 'primary' : ''" 
          @click="showAllCourses"
          :disabled="!showHotCourses"
        >
          所有课程
        </el-button>
        <el-button 
          :type="showHotCourses ? 'primary' : ''" 
          @click="showHotCoursesView"
          :disabled="showHotCourses"
        >
          🔥 热门课程
        </el-button>
      </div>
    </div>
    
    <!-- 搜索栏 - 只在显示所有课程时显示 -->
    <div class="search-bar" v-if="!showHotCourses">
      <el-input 
        v-model="courseName" 
        placeholder="搜索课程名称" 
        style="width: 200px; margin-right: 10px;"
        @keyup.enter="handleSearch"
      />
      <el-input 
        v-model="teacherName" 
        placeholder="搜索教师姓名" 
        style="width: 200px; margin-right: 10px;"
        @keyup.enter="handleSearch"
      />
      <!-- 课程状态筛选 -->
      <el-select 
        v-model="courseStatus" 
        placeholder="课程状态" 
        style="width: 120px; margin-right: 10px;"
        @change="handleSearch"
      >
        <el-option label="全部" value="all" />
        <el-option label="进行中" value="ongoing" />
        <el-option label="已结束" value="completed" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>
    
    <!-- 热门课程提示 -->
    <div class="hot-courses-tip" v-if="showHotCourses">
      <el-alert
        title="热门课程基于学生选课数量排序，快来选择你感兴趣的课程吧！"
        type="success"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 课程卡片画廊 -->
    <el-row :gutter="20" v-loading="loading" v-if="courses.length > 0">
      <el-col :span="6" v-for="course in courses" :key="course.id">
        <el-card class="course-card" shadow="hover">
          <div class="course-info">
            <h3>{{ course.name || course.courseName }}</h3>
            <p class="teacher-name">教师：{{ course.teacherName }}</p>
            <p class="course-comment">{{ course.comment || '暂无课程介绍' }}</p>
            
            <!-- 课程状态和选课人数 -->
            <div class="course-meta">
              <el-tag :type="course.isOver === 1 ? 'danger' : 'success'">
                {{ course.isOver === 1 ? '已结束' : '进行中' }}
              </el-tag>
              <span class="student-count">
                <el-icon><User /></el-icon>
                {{ course.studentCount || 0 }}人已选课
              </span>
            </div>
            
            <!-- 操作按钮 -->
            <div class="course-actions">
              <el-button 
                type="primary" 
                size="small"
                @click="viewCourse(course)"
                style="margin-right: 8px;"
              >
                查看详情
              </el-button>
              
              <!-- 选课按钮 -->
              <el-button 
                v-if="!isCourseEnrolled(course) && course.isOver !== 1"
                type="success" 
                size="small"
                @click="enrollCourse(course)"
                :loading="course.enrolling"
              >
                选课
              </el-button>
              
              <!-- 已选课标识 -->
              <el-tag v-else-if="isCourseEnrolled(course)" type="success" size="small">
                已选课
              </el-tag>
              
              <!-- 课程已结束标识 -->
              <el-tag v-else-if="course.isOver === 1" type="info" size="small">
                课程已结束
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 空状态 -->
    <div class="empty-state" v-if="!loading && courses.length === 0">
      <el-empty 
        :description="showHotCourses ? '暂无热门课程' : '暂无可选课程'"
        :image-size="120"
      >
        <template v-if="!showHotCourses">
          <el-button type="primary" @click="handleReset">清空搜索条件</el-button>
        </template>
        <template v-else>
          <el-button type="primary" @click="showAllCourses">查看所有课程</el-button>
        </template>
      </el-empty>
    </div>

    <!-- 分页 - 只在显示所有课程时显示 -->
    <div class="pagination-wrapper" v-if="!showHotCourses && courses.length > 0">
      <el-pagination
        background
        layout="total, prev, pager, next, sizes"
        :total="total"
        :page-size="pageSize"
        :current-page="pageNum"
        :page-sizes="[8, 12, 16, 20]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
    
    <!-- 热门课程统计信息 -->
    <div class="hot-courses-stats" v-if="showHotCourses && courses.length > 0">
      <el-text type="info">共找到 {{ courses.length }} 门热门课程</el-text>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { getCourseEnrollmentCount } from '@/api/course'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const courses = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(12)
const courseName = ref('')
const teacherName = ref('')
const loading = ref(false)
const showHotCourses = ref(false)
const enrolledCourseIds = ref(new Set()) // 存储已选课程ID
const courseStatus = ref('all')

// 获取所有课程（学生可选的课程）
const getAllCourses = async (pageNum = 1, pageSize = 12, courseName = '', teacherName = '') => {
  try {
    const res = await request.get('/api/course/listPage', {
      params: { pageNum, pageSize, courseName, teacherName }
    })
    
    if (res.code === 0 && res.data) {
      const coursesData = res.data.records || []
      
      return {
        records: coursesData,
        total: res.data.total || 0
      }
    }
    return { records: [], total: 0 }
  } catch (error) {
    console.error('获取课程列表失败:', error)
    throw error
  }
}

// 获取热门课程
const getHotCourses = async () => {
  try {
    const res = await request.get('/api/enroll/list/hot')
    if (res.code === 0 && res.data) {
      return res.data || []
    }
    return []
  } catch (error) {
    console.error('获取热门课程失败:', error)
    throw error
  }
}

// 获取学生已选课程列表接口
const getStudentEnrolledCourses = async () => {
  try {
    if (!authStore.user?.id) {
      console.warn('用户未登录，无法获取已选课程')
      return []
    }
    
    const res = await request.get('/api/enroll/list/student', {
      params: { studentId: authStore.user.id }
    })
    
    if (res.code === 0) {
      const enrolledCourses = res.data || []
      // 返回课程信息，提取course部分
      return enrolledCourses.map(item => item.course)
    }
    console.error('获取学生已选课程失败:', res)
    return []
  } catch (error) {
    console.error('获取学生已选课程接口错误:', error)
    return []
  }
}

// 标记课程的选课状态
const markEnrollmentStatus = (courseList, enrolledCourses) => {
  // enrolledCourses 是课程对象数组，包含 id 字段
  const enrolledIds = new Set(enrolledCourses.map(course => course.id))
  
  return courseList.map(course => ({
    ...course,
    isEnrolled: enrolledIds.has(course.id)
  }))
}

// 获取所有课程的选课人数
const fetchCoursesEnrollmentCount = async (courseList) => {
  try {
    // 并行获取所有课程的选课人数
    const enrollmentCountPromises = courseList.map(async (course) => {
      const count = await getCourseEnrollmentCount(course.id)
      return { ...course, studentCount: count }
    })
    
    const coursesWithCount = await Promise.all(enrollmentCountPromises)
    return coursesWithCount
  } catch (error) {
    console.error('获取课程选课人数失败:', error)
    // 如果获取失败，返回原始课程列表，选课人数设为0
    return courseList.map(course => ({ ...course, studentCount: 0 }))
  }
}

// 主要数据获取方法
const fetchCourses = async () => {
  try {
    loading.value = true
    
    // 先获取学生已选课程状态
    const enrolledCourses = await getStudentEnrolledCourses()
    enrolledCourseIds.value = new Set(enrolledCourses.map(course => course.id))
    
    let coursesWithStatus = []
    
    if (showHotCourses.value) {
      // 获取热门课程
      const hotCoursesData = await getHotCourses()
      coursesWithStatus = markEnrollmentStatus(hotCoursesData, enrolledCourses)
      total.value = hotCoursesData.length
    } else {
      // 获取所有可选课程
      const coursesData = await getAllCourses(
        pageNum.value, 
        pageSize.value, 
        courseName.value, 
        teacherName.value
      )
      
      coursesWithStatus = markEnrollmentStatus(coursesData.records, enrolledCourses)
      total.value = coursesData.total
    }
    
    // 获取每个课程的选课人数
    const coursesWithEnrollmentCount = await fetchCoursesEnrollmentCount(coursesWithStatus)
    
    // 根据课程状态进行筛选
    let filteredCourses = coursesWithEnrollmentCount
    if (!showHotCourses.value && courseStatus.value !== 'all') {
      filteredCourses = coursesWithEnrollmentCount.filter(course => {
        if (courseStatus.value === 'ongoing') {
          return course.isOver === 0
        } else if (courseStatus.value === 'completed') {
          return course.isOver === 1
        }
        return true
      })
    }
    
    courses.value = filteredCourses
    
  } catch (error) {
    console.error('获取课程失败:', error)
    ElMessage.error(showHotCourses.value ? '获取热门课程失败' : '获取课程失败')
  } finally {
    loading.value = false
  }
}

// 选课功能
const enrollCourse = async (course) => {
  try {
    await ElMessageBox.confirm(
      `确定要选择课程 "${course.name || course.courseName}" 吗？`,
      '确认选课',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    course.enrolling = true
    
    // 调用选课接口
    const res = await request.post('/api/enroll', null, {
      params: {
        courseId: course.id
      }
    })
    
    if (res.code === 0) {
      ElMessage.success('选课成功！')
      
      // 立即更新本地状态
      course.isEnrolled = true
      enrolledCourseIds.value.add(course.id)
      
      // 更新学生数量
      if (course.studentCount !== undefined) {
        course.studentCount = (course.studentCount || 0) + 1
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
    course.enrolling = false
  }
}

// 查看课程详情
const viewCourse = (course) => {
  // 跳转到课程详情页面
  router.push(`/dashboard/student/courses/${course.id}`)
}

// 检查课程是否已选
const isCourseEnrolled = (course) => {
  return course.isEnrolled || enrolledCourseIds.value.has(course.id)
}

// 分页处理
const handlePageChange = (val) => {
  if (!showHotCourses.value) {
    pageNum.value = val
    fetchCourses()
  }
}

const handleSizeChange = (val) => {
  if (!showHotCourses.value) {
    pageSize.value = val
    pageNum.value = 1
    fetchCourses()
  }
}

// 搜索功能
const handleSearch = () => {
  pageNum.value = 1
  fetchCourses()
}

const handleReset = () => {
  courseName.value = ''
  teacherName.value = ''
  courseStatus.value = 'all'
  pageNum.value = 1
  fetchCourses()
}

// 视图切换
const showAllCourses = () => {
  showHotCourses.value = false
  pageNum.value = 1
  fetchCourses()
}

const showHotCoursesView = () => {
  showHotCourses.value = true
  fetchCourses()
}

// 页面初始化
onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
.course-selection-gallery {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-section h2 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.view-toggle {
  display: flex;
  gap: 10px;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.hot-courses-tip {
  margin-bottom: 20px;
}

.course-card {
  margin-bottom: 20px;
  transition: transform 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.course-card:hover {
  transform: translateY(-5px);
}

.course-info {
  padding: 10px;
}

.course-info h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  min-height: 25px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.teacher-name {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
}

.course-comment {
  margin: 8px 0 12px 0;
  color: #909399;
  font-size: 13px;
  line-height: 1.4;
  min-height: 36px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 12px 0;
}

.student-count {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.student-count .el-icon {
  margin-right: 4px;
}

.course-actions {
  display: flex;
  align-items: center;
  margin-top: 15px;
}

.empty-state {
  text-align: center;
  margin: 60px 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.hot-courses-stats {
  text-align: center;
  margin-top: 20px;
  padding: 10px;
  background: #f0f9ff;
  border-radius: 6px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .course-selection-gallery {
    padding: 15px;
  }
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .search-bar {
    flex-direction: column;
    gap: 10px;
  }
  
  .search-bar .el-input {
    width: 100% !important;
  }
}
</style> 