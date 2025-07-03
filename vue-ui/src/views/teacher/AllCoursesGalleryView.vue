<template>
  <div class="all-courses-gallery">
    <div class="header-section">
      <h2>{{ showHotCourses ? '热门课程' : '所有课程' }}</h2>
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
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>
    
    <!-- 热门课程提示 -->
    <div class="hot-courses-tip" v-if="showHotCourses">
      <el-alert
        title="热门课程基于学生选课数量排序"
        type="info"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 课程卡片 -->
    <el-row :gutter="20" v-loading="loading" v-if="courses.length > 0">
      <el-col :span="6" v-for="course in courses" :key="course.id">
        <el-card class="course-card" shadow="hover">
          <div class="course-info">
            <h3>{{ course.name }}</h3>
            <p class="teacher-name">教师：{{ course.teacherName }}</p>
            <p class="course-comment">{{ course.comment || '暂无课程介绍' }}</p>
            <p class="course-status">
              <el-tag :type="course.isOver === 1 ? 'danger' : 'success'">
                {{ course.isOver === 1 ? '已结束' : '进行中' }}
              </el-tag>
            </p>
            <el-button type="primary" @click="goToDetail(course.id)">查看详情</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 空状态 -->
    <div class="empty-state" v-if="!loading && courses.length === 0">
      <el-empty 
        :description="showHotCourses ? '暂无热门课程' : '暂无课程数据'"
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
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const courses = ref([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(12)
const courseName = ref('')
const teacherName = ref('')
const loading = ref(false)
const showHotCourses = ref(false)
const router = useRouter()

// 获取所有课程
const getAllCourses = (pageNum = 1, pageSize = 12, courseName = '', teacherName = '') => {
  return request.get('/api/course/listPage', {
    params: { pageNum, pageSize, courseName, teacherName }
  })
}

// 获取热门课程
const getHotCourses = () => {
  return request.get('/api/enroll/list/hot')
}

const fetchCourses = async () => {
  try {
    loading.value = true
    
    if (showHotCourses.value) {
      // 获取热门课程
      const res = await getHotCourses()
      if (res.code === 0 && res.data && Array.isArray(res.data)) {
        courses.value = res.data
        total.value = res.data.length
      } else {
        ElMessage.error(res.message || '获取热门课程失败')
      }
    } else {
      // 获取所有课程
      const res = await getAllCourses(
        pageNum.value, 
        pageSize.value, 
        courseName.value, 
        teacherName.value
      )
      if (res.code === 0 && res.data && Array.isArray(res.data.records)) {
        courses.value = res.data.records
        total.value = res.data.total
      } else {
        ElMessage.error(res.message || '获取课程失败')
      }
    }
  } catch (e) {
    console.error('获取课程失败:', e)
    ElMessage.error(showHotCourses.value ? '获取热门课程失败' : '获取课程失败')
  } finally {
    loading.value = false
  }
}

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

// 切换到所有课程视图
const showAllCourses = () => {
  showHotCourses.value = false
  pageNum.value = 1
  fetchCourses()
}

// 切换到热门课程视图
const showHotCoursesView = () => {
  showHotCourses.value = true
  fetchCourses()
}

const goToDetail = (id) => {
  router.push(`/dashboard/teacher/courses/${id}`)
}

onMounted(fetchCourses)
</script>

<style scoped>
.all-courses-gallery {
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

.view-toggle {
  display: flex;
  gap: 8px;
}

.view-toggle .el-button {
  transition: all 0.2s ease;
}

.search-bar {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
}

.hot-courses-tip {
  margin-bottom: 24px;
}

.course-card {
  margin-bottom: 20px;
  min-height: 280px;
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
  margin-bottom: 12px;
  font-size: 13px;
  min-height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.course-status {
  margin-bottom: 16px;
}

.pagination-wrapper {
  text-align: center;
  margin-top: 32px;
}

.hot-courses-stats {
  text-align: center;
  margin-top: 32px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.empty-state {
  margin-top: 40px;
  text-align: center;
}
</style> 