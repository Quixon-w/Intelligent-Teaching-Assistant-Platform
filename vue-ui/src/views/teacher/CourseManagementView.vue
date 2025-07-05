<template>
  <div class="course-management-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>我的课程</h3>
          <el-button type="primary" @click="showAddCourseDialog = true">
            <el-icon><Plus /></el-icon>
            创建课程
          </el-button>
        </div>
      </template>
      
      <div class="search-section">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="课程名称">
            <el-input v-model="searchForm.courseName" placeholder="请输入课程名称" @keyup.enter="searchCourses" />
          </el-form-item>
          <el-form-item label="课程状态">
            <el-select v-model="searchForm.courseStatus" placeholder="请选择课程状态" @change="searchCourses">
              <el-option label="全部" value="all" />
              <el-option label="进行中" value="ongoing" />
              <el-option label="已结束" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchCourses">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table 
        :data="filteredCourseList" 
        v-loading="loading" 
        style="width: 100%"
        class="course-table"
        stripe
        :header-cell-style="{ background: '#fafafa', color: '#606266' }"
      >
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="name" label="课程名称" min-width="140" show-overflow-tooltip />
                  <el-table-column prop="comment" label="课程描述" min-width="180" show-overflow-tooltip />
        <el-table-column prop="createTime" label="创建时间" width="160" align="center" />
        <el-table-column prop="isOver" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag 
              :type="scope.row.isOver === 0 ? 'success' : 'info'" 
              size="small"
              effect="light"
            >
              {{ scope.row.isOver === 0 ? '进行中' : '已结束' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="scope">
            <div class="action-buttons-container">
              <!-- 第一行：基础操作 -->
              <div class="action-row">
                <el-button 
                  size="small" 
                  :icon="View" 
                  @click="viewCourse(scope.row)"
                  class="action-btn view-btn"
                >
                  查看
                </el-button>
                
            <el-button 
              size="small" 
                  type="primary" 
                  :icon="Edit" 
                  @click="editCourse(scope.row)"
                  class="action-btn edit-btn"
                >
                  编辑
            </el-button>
              </div>
              
              <!-- 第二行：状态操作 -->
              <div class="action-row">
                <!-- 进行中的课程 -->
                <template v-if="scope.row.isOver === 0">
            <el-button 
              size="small" 
              type="success" 
                    :icon="CircleCheck" 
              @click="endCourse(scope.row)"
                    class="action-btn end-btn"
            >
              结课
            </el-button>
                  
                  <el-popconfirm
                    title="确定要删除这个课程吗？"
                    :icon="Delete"
                    icon-color="#f56c6c"
                    confirm-button-text="确定"
                    cancel-button-text="取消"
                    @confirm="deleteCourse(scope.row)"
                  >
                    <template #reference>
                      <el-button 
                        size="small" 
                        type="danger" 
                        :icon="Delete" 
                        class="action-btn danger-btn"
                      >
                        删除
                      </el-button>
                    </template>
                  </el-popconfirm>
                </template>
                
                <!-- 已结课状态 -->
                <template v-else>
                  <div style="width: 100%;">
                    <el-tag 
                      type="info" 
                      size="small" 
                      :icon="Lock"
                      class="finished-tag full-width"
                    >
                      已结课
                    </el-tag>
                  </div>
                </template>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="empty-state" v-if="!loading && filteredCourseList.length === 0">
        <el-empty 
          :description="getEmptyStateDescription()"
        >
          <el-button 
            v-if="courseList.length > 0"
            type="primary" 
            @click="resetSearch"
          >
            清空筛选条件
          </el-button>
          <el-button 
            v-else
            type="primary" 
            @click="showAddCourseDialog = true"
          >
            创建第一个课程
          </el-button>
        </el-empty>
      </div>
    </el-card>
    
    <!-- 添加/编辑课程对话框 -->
    <el-dialog
      v-model="showAddCourseDialog"
      :title="editingCourse ? '编辑课程' : '创建课程'"
      width="500px"
    >
      <el-form :model="courseForm" :rules="courseRules" ref="courseFormRef" label-width="100px">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="courseForm.name" />
        </el-form-item>
        <el-form-item label="课程描述" prop="comment">
          <el-input 
            v-model="courseForm.comment" 
            type="textarea" 
            :rows="4"
            placeholder="请输入课程描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" @click="saveCourse">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Edit, CircleCheck, Delete, Lock } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const showAddCourseDialog = ref(false)
const editingCourse = ref(null)
const courseFormRef = ref()

const searchForm = reactive({
  courseName: '',
  courseStatus: 'all'
})

const courseForm = reactive({
  name: '',
  comment: ''
})

const courseRules = {
  name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '课程名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  comment: [
    { required: true, message: '请输入课程描述', trigger: 'blur' }
  ]
}

const courseList = ref([])

// 计算属性：根据搜索条件过滤课程列表
const filteredCourseList = computed(() => {
  let filtered = courseList.value
  
  // 按课程名称筛选
  if (searchForm.courseName) {
    filtered = filtered.filter(course => 
      course.name.toLowerCase().includes(searchForm.courseName.toLowerCase())
    )
  }
  
  // 按课程状态筛选
  if (searchForm.courseStatus !== 'all') {
    filtered = filtered.filter(course => {
      if (searchForm.courseStatus === 'ongoing') {
        return course.isOver === 0
      } else if (searchForm.courseStatus === 'completed') {
        return course.isOver === 1
      }
      return true
    })
  }
  
  return filtered
})

// API方法
const getMyCourses = (teacherId) => {
  return request.get('/api/course/listById', {
    params: { teacherId }
  })
}

const createCourse = (name, comment) => {
  return request.post('/api/course/add', null, {
    params: {
      courseName: name,
      comment: comment
    }
  })
}

const updateCourseInfo = (id, name, comment) => {
  return request.post('/api/course/update', { id, name, comment })
}

const deleteCourseById = (id) => {
  return request.post('/api/course/delete', null, {
    params: { courseId: id }
  })
}

const endCourseById = (id) => {
  return request.post('/api/course/over', null, {
    params: { courseId: id }
  })
}

// 方法
const loadCourses = async () => {
  if (!authStore.user?.id) {
    ElMessage.error('用户信息获取失败')
    return
  }
  
  loading.value = true
  try {
    const result = await getMyCourses(authStore.user.id)
    
    if (result.code === 0) {
      courseList.value = result.data || []
    } else {
      ElMessage.error(result.message || '获取课程列表失败')
    }
  } catch (error) {
    console.error('加载课程列表失败:', error)
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

const searchCourses = () => {
  // 前端过滤，无需重新请求
}

const resetSearch = () => {
  searchForm.courseName = ''
  searchForm.courseStatus = 'all'
}

const viewCourse = (course) => {
  router.push(`/dashboard/teacher/courses/${course.id}`)
}

const editCourse = (course) => {
  editingCourse.value = course
  Object.assign(courseForm, {
    name: course.name,
    comment: course.comment
  })
  showAddCourseDialog.value = true
}

const saveCourse = async () => {
  try {
    await courseFormRef.value.validate()
    
    if (editingCourse.value) {
      // 编辑课程
      const result = await updateCourseInfo(editingCourse.value.id, courseForm.name, courseForm.comment)
      if (result.code === 0) {
        ElMessage.success('课程更新成功')
      } else {
        ElMessage.error(result.message || '课程更新失败')
      }
    } else {
      // 创建课程
      const result = await createCourse(courseForm.name, courseForm.comment)
      if (result.code === 0) {
        ElMessage.success('课程创建成功')
      } else {
        ElMessage.error(result.message || '课程创建失败')
      }
    }
    
    showAddCourseDialog.value = false
    resetCourseForm()
    loadCourses()
  } catch (error) {
    console.error('保存课程失败:', error)
  }
}

const deleteCourse = async (course) => {
  try {
    await ElMessageBox.confirm(
      `<div style="text-align: center; line-height: 1.8;">
        <div style="font-size: 24px; color: #f56c6c; margin-bottom: 16px;">
          🚨 危险操作警告 🚨
        </div>
        
        <div style="font-size: 16px; color: #303133; margin-bottom: 20px; padding: 12px; background: #fef0f0; border-radius: 8px; border-left: 4px solid #f56c6c;">
          您即将删除课程：<strong style="color: #e6a23c;">"${course.name}"</strong>
        </div>
        
        <div style="text-align: left; background: #fff; padding: 16px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 16px 0;">
          <div style="font-size: 14px; color: #f56c6c; font-weight: bold; margin-bottom: 12px;">
            📋 删除后将会导致：
          </div>
          <div style="font-size: 13px; color: #606266; line-height: 2;">
            <div style="margin-bottom: 8px;">🗃️ 课程的所有数据将被<span style="color: #f56c6c; font-weight: bold;">永久删除</span></div>
            <div style="margin-bottom: 8px;">👥 学生的选课记录将被<span style="color: #f56c6c; font-weight: bold;">清除</span></div>
            <div style="margin-bottom: 8px;">📚 课程相关的所有课时、作业、成绩等数据将<span style="color: #f56c6c; font-weight: bold;">丢失</span></div>
            <div style="color: #f56c6c; font-weight: bold;">⚠️ 此操作无法撤销和恢复</div>
          </div>
        </div>
        
        <div style="font-size: 14px; color: #909399; margin-top: 16px;">
          请慎重考虑后再进行操作
        </div>
      </div>`,
      '',
      {
        confirmButtonText: '🔓 我已了解风险，确认删除',
        cancelButtonText: '🛡️ 取消删除',
        type: 'error',
        dangerouslyUseHTMLString: true,
        distinguishCancelAndClose: true,
        customClass: 'custom-delete-dialog'
      }
    )
    
    // 二次确认 - 简洁美观的最终确认
    await ElMessageBox.confirm(
      `<div style="text-align: center; padding: 20px;">
        <div style="font-size: 20px; margin-bottom: 16px;">🤔</div>
        <div style="font-size: 16px; color: #303133; line-height: 1.6;">
          最后确认：您真的要删除课程<br/>
          <strong style="color: #e6a23c; font-size: 18px;">"${course.name}"</strong> 吗？
        </div>
      </div>`,
      '🔥 最终确认',
      {
        confirmButtonText: '🗑️ 确认删除',
        cancelButtonText: '💭 我再想想',
        type: 'error',
        dangerouslyUseHTMLString: true
      }
    )
    
    const result = await deleteCourseById(course.id)
    if (result.code === 0) {
      ElMessage.success('课程删除成功')
      loadCourses()
    } else {
      ElMessage.error(result.message || '课程删除失败')
    }
  } catch {
    // 用户取消删除
    ElMessage.info('已取消删除操作')
  }
}

const endCourse = async (course) => {
  try {
    await ElMessageBox.confirm(
      `确定要结束课程 "${course.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const result = await endCourseById(course.id)
    if (result.code === 0) {
      ElMessage.success('课程已结束')
      loadCourses()
    } else {
      ElMessage.error(result.message || '结课失败')
    }
  } catch {
    // 用户取消
  }
}

const resetCourseForm = () => {
  editingCourse.value = null
  Object.assign(courseForm, {
    name: '',
    comment: ''
  })
}

const cancelEdit = () => {
  showAddCourseDialog.value = false
  resetCourseForm()
}

const getEmptyStateDescription = () => {
  if (courseList.value.length === 0) {
    return '暂无课程数据'
  }
  
  if (searchForm.courseName || searchForm.courseStatus !== 'all') {
    let description = '暂无符合条件的课程'
    if (searchForm.courseName) {
      description += `（搜索："${searchForm.courseName}"）`
    }
    if (searchForm.courseStatus !== 'all') {
      const statusText = searchForm.courseStatus === 'ongoing' ? '进行中' : '已结束'
      description += `（状态：${statusText}）`
    }
    return description
  }
  
  return '暂无课程数据'
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.course-management-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
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

.search-section {
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

/* 操作按钮容器样式 */
.action-buttons-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 6px 2px;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: space-between;
}

/* 统一按钮样式 */
.action-btn {
  flex: 1;
  min-width: 68px;
  font-size: 12px;
  padding: 5px 8px;
  border-radius: 6px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  letter-spacing: 0.3px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 按钮类型特殊样式 */
.view-btn {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-color: #dee2e6;
  color: #495057;
}

.view-btn:hover {
  background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
  border-color: #adb5bd;
}

.edit-btn:hover {
  background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);
}

.end-btn:hover {
  background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
}

/* 危险按钮特殊样式 */
.danger-btn {
  position: relative;
  overflow: hidden;
}

.danger-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.danger-btn:hover::before {
  left: 100%;
}

/* 已结课标签样式 */
.finished-tag {
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 12px;
  background: linear-gradient(45deg, #f0f2f5, #e4e7ed);
  border: 1px solid #d9d9d9;
  color: #666;
  font-size: 12px;
  letter-spacing: 0.3px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.finished-tag.full-width {
  width: 100%;
  justify-self: stretch;
}

/* 优化表格单元格内边距 */
.el-table .el-table__cell {
  padding: 14px 8px;
}

/* 让操作列固定在右侧 */
.el-table__fixed-right {
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.06);
}

/* 表格整体样式优化 */
.course-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.course-table .el-table__row:hover {
  background-color: #f8f9fa;
}

/* Popconfirm 样式优化 */
.el-popconfirm .el-popconfirm__main {
  padding: 12px 16px;
  border-radius: 8px;
}

/* 状态标签样式优化 */
.el-tag {
  border-radius: 16px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 操作列头部样式 */
.el-table th.el-table__cell {
  background-color: #fafafa !important;
  font-weight: 600;
  color: #303133 !important;
  border-bottom: 2px solid #e4e7ed;
}

/* 行悬停效果增强 */
.course-table .el-table__row {
  transition: all 0.2s ease;
}

.course-table .el-table__row:hover .action-btn {
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
}

/* 响应式设计优化 */
@media (max-width: 1200px) {
  .action-row {
    gap: 4px;
  }
  
  .action-btn {
    min-width: 60px;
    font-size: 11px;
    padding: 4px 6px;
  }
  
  .finished-tag {
    font-size: 11px;
    padding: 4px 10px;
  }
}

@media (max-width: 768px) {
  .action-buttons-container {
    padding: 4px 1px;
    gap: 4px;
  }
  
  .action-row {
    gap: 3px;
  }
  
  .action-btn {
    min-width: 55px;
    font-size: 10px;
    padding: 3px 5px;
    border-radius: 4px;
  }
  
  .course-management-container {
    padding: 12px;
  }
  
  .finished-tag {
    font-size: 10px;
    padding: 3px 8px;
  }
}

@media (max-width: 1500px) {
  .action-buttons-container {
    gap: 3px;
  }
  
  .action-row {
    gap: 2px;
  }
  
  .action-btn {
    min-width: 50px;
    font-size: 9px;
    padding: 2px 4px;
    letter-spacing: 0;
  }
  
  .finished-tag {
    font-size: 9px;
    padding: 2px 6px;
  }
}
</style> 