<template>
  <div class="course-monitor">
    <div class="header-section">
      <h2>课程监控</h2>
          <div class="header-actions">
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
        </div>
    
    <!-- 搜索栏 -->
    <div class="search-bar">
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
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
      </div>
      
    <!-- 课程卡片 -->
    <el-row :gutter="20" v-loading="loading" v-if="courses.length > 0">
      <el-col :span="6" v-for="course in courses" :key="course.id">
        <el-card class="course-card" shadow="hover">
          <div class="course-info">
            <h3>{{ course.name }}</h3>
            <p class="teacher-name">教师：{{ course.teacherName }}</p>
            <p class="course-comment">{{ course.comment || '暂无课程介绍' }}</p>
            <div class="course-meta">
              <p class="course-status">
                <el-tag :type="course.isOver === 1 ? 'danger' : 'success'">
                  {{ course.isOver === 1 ? '已结束' : '进行中' }}
            </el-tag>
              </p>
              <p class="enrollment-count">
                <el-icon><User /></el-icon>
                选课人数：{{ course.enrollmentCount || 0 }}
              </p>
              <p class="create-time">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(course.createTime) }}
              </p>
            </div>
                         <div class="course-actions">
               <el-button 
                 type="danger" 
                 @click="handleDeleteCourse(course)"
               >
                 删除课程
               </el-button>
             </div>
      </div>
    </el-card>
      </el-col>
    </el-row>
    
    <!-- 空状态 -->
    <div class="empty-state" v-if="!loading && courses.length === 0">
      <el-empty 
        description="暂无课程数据"
        :image-size="120"
      >
        <el-button type="primary" @click="handleReset">清空搜索条件</el-button>
      </el-empty>
      </div>
    
    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="courses.length > 0">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, User, Calendar } from '@element-plus/icons-vue'
import { getCourses, deleteCourse, getCourseEnrollmentCount } from '@/api/course.js'
import { handleException } from '@/utils/errorHandler'

const courses = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(12)
const courseName = ref('')
const teacherName = ref('')
const loading = ref(false)

// 获取课程列表
const fetchCourses = async () => {
  try {
    loading.value = true
    
    const res = await getCourses(
      pageNum.value, 
      pageSize.value, 
      courseName.value, 
      teacherName.value
    )
    
    if (res.code === 0 && res.data && Array.isArray(res.data.records)) {
      courses.value = res.data.records
      total.value = res.data.total
      
      // 获取每个课程的选课人数
      await Promise.all(
        courses.value.map(async (course) => {
          try {
            const count = await getCourseEnrollmentCount(course.id)
            course.enrollmentCount = count
          } catch (error) {
            console.error(`获取课程 ${course.id} 选课人数失败:`, error)
            course.enrollmentCount = 0
          }
        })
      )
    } else {
      handleException(res, '获取课程列表失败')
    }
  } catch (error) {
    console.error('获取课程失败:', error)
    handleException(error, '获取课程失败')
  } finally {
    loading.value = false
  }
}

// 删除课程
const handleDeleteCourse = async (course) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除课程"${course.name}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    const res = await deleteCourse(course.id)
    
    if (res.code === 0) {
      ElMessage.success('课程删除成功')
      // 重新加载课程列表
      await fetchCourses()
    } else {
      handleException(res, '删除课程失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除课程失败:', error)
      handleException(error, '删除课程失败')
    }
  }
}

// 分页处理
const handlePageChange = (val) => {
  pageNum.value = val
  fetchCourses()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  pageNum.value = 1
  fetchCourses()
}

// 搜索处理
const handleSearch = () => {
  pageNum.value = 1
  fetchCourses()
}

const handleReset = () => {
  courseName.value = ''
  teacherName.value = ''
  pageNum.value = 1
  fetchCourses()
}

// 刷新数据
const refreshData = () => {
  fetchCourses()
  ElMessage.success('数据已刷新')
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(fetchCourses)
</script>

<style scoped>
.course-monitor {
  padding: 24px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-section h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.search-bar {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
}

.course-card {
  margin-bottom: 20px;
  min-height: 320px;
  transition: transform 0.2s;
}

.course-card:hover {
  transform: translateY(-2px);
}

.course-info {
  text-align: center;
  padding: 16px;
}

.course-info h3 {
  color: #303133;
  margin-bottom: 12px;
  font-size: 18px;
  font-weight: 600;
}

.teacher-name {
  color: #606266;
  margin-bottom: 8px;
  font-size: 14px;
}

.course-comment {
  color: #909399;
  margin-bottom: 16px;
  font-size: 13px;
  min-height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.course-meta {
  margin-bottom: 16px;
}

.course-status {
  margin-bottom: 8px;
}

.enrollment-count,
.create-time {
  color: #909399;
  font-size: 12px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.course-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.pagination-wrapper {
  text-align: center;
  margin-top: 32px;
}

.empty-state {
  margin-top: 40px;
  text-align: center;
}

/* 已结束课程的特殊样式 */
.course-card:has(.el-tag--danger) {
  opacity: 0.8;
}

.course-card:has(.el-tag--danger) .course-info h3 {
  color: #909399;
}
</style> 