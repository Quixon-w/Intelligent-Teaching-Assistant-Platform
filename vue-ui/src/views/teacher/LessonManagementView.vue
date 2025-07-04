<template>
  <div class="lesson-management-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>课时管理</h3>
          <el-button type="primary" @click="showAddLessonDialog = true">
            <el-icon><Plus /></el-icon>
            添加课时
          </el-button>
        </div>
      </template>
      
      <div class="course-info" v-if="courseInfo">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="课程名称">{{ courseInfo.courseName }}</el-descriptions-item>
          <el-descriptions-item label="课程ID">{{ courseInfo.id }}</el-descriptions-item>
          <el-descriptions-item label="课时总数">{{ lessons.length }}</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <el-table :data="lessons" v-loading="loading" style="width: 100%; margin-top: 20px;">
        <el-table-column prop="id" label="课时ID" width="80" />
        <el-table-column prop="lessonNum" label="课时编号" width="100" />
        <el-table-column prop="title" label="课时标题" width="200" />
        <el-table-column prop="description" label="课时描述" />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editLesson(scope.row)">编辑</el-button>
            <el-button size="small" type="primary" @click="uploadMaterials(scope.row)">上传资料</el-button>
            <el-button size="small" type="danger" @click="deleteLesson(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑课时对话框 -->
    <el-dialog
      v-model="showAddLessonDialog"
      :title="editingLesson ? '编辑课时' : '添加课时'"
      width="500px"
    >
      <el-form :model="lessonForm" :rules="lessonRules" ref="lessonFormRef" label-width="100px">
        <el-form-item label="课时编号" prop="lessonNum">
          <el-input-number v-model="lessonForm.lessonNum" :min="1" />
        </el-form-item>
        <el-form-item label="课时标题" prop="title">
          <el-input v-model="lessonForm.title" />
        </el-form-item>
        <el-form-item label="课时描述" prop="description">
          <el-input 
            v-model="lessonForm.description" 
            type="textarea" 
            :rows="4"
            placeholder="请输入课时描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddLessonDialog = false">取消</el-button>
        <el-button type="primary" @click="saveLesson">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { findCourseByID } from '@/api/course.js'

const route = useRoute()

// 响应式数据
const loading = ref(false)
const showAddLessonDialog = ref(false)
const editingLesson = ref(null)
const lessonFormRef = ref()
const courseInfo = ref(null)

const lessonForm = reactive({
  lessonNum: 1,
  title: '',
  description: ''
})

const lessonRules = {
  lessonNum: [
    { required: true, message: '请输入课时编号', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入课时标题', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入课时描述', trigger: 'blur' }
  ]
}

const lessons = ref([
  {
    id: 1,
    lessonNum: 1,
    title: 'Vue.js 基础入门',
    description: '学习Vue.js的基本概念和语法',
    createTime: '2024-01-01 10:00:00'
  },
  {
    id: 2,
    lessonNum: 2,
    title: 'Vue.js 组件开发',
    description: '掌握Vue.js组件的创建和使用',
    createTime: '2024-01-02 14:30:00'
  }
])

// 方法
const editLesson = (lesson) => {
  editingLesson.value = lesson
  Object.assign(lessonForm, {
    lessonNum: lesson.lessonNum,
    title: lesson.title,
    description: lesson.description
  })
  showAddLessonDialog.value = true
}

const uploadMaterials = (lesson) => {
  // TODO: 跳转到资料上传页面
  console.log('上传资料:', lesson)
}

const deleteLesson = async (lesson) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除课时 "${lesson.title}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用删除课时API
    ElMessage.success('课时删除成功')
    loadLessons()
  } catch {
    // 用户取消
  }
}

const saveLesson = async () => {
  try {
    await lessonFormRef.value.validate()
    
    if (editingLesson.value) {
      // TODO: 调用编辑课时API
      ElMessage.success('课时更新成功')
    } else {
      // TODO: 调用添加课时API
      ElMessage.success('课时添加成功')
    }
    
    showAddLessonDialog.value = false
    resetLessonForm()
    loadLessons()
  } catch (error) {
    console.error('保存课时失败:', error)
  }
}

const resetLessonForm = () => {
  editingLesson.value = null
  Object.assign(lessonForm, {
    lessonNum: 1,
    title: '',
    description: ''
  })
}

const loadCourseInfo = async () => {
  try {
    const courseId = route.params.courseId
    const result = await findCourseByID(courseId)
    
    if (result.code === 0) {
      courseInfo.value = result.data
    } else {
      console.error('获取课程信息失败:', result.message)
    }
  } catch (error) {
    console.error('加载课程信息失败:', error)
  }
}

const loadLessons = () => {
  // TODO: 调用获取课时列表API
  console.log('加载课时列表')
}

onMounted(() => {
  loadCourseInfo()
  loadLessons()
})
</script>

<style scoped>
.lesson-management-container {
  max-width: 1200px;
  margin: 0 auto;
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

.course-info {
  margin-bottom: 20px;
}
</style> 