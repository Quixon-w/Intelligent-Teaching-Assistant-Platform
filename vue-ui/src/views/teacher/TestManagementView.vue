<template>
  <div class="test-management-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>测试管理</h3>
          <el-button type="primary" @click="showAddTestDialog = true">
            <el-icon><Plus /></el-icon>
            创建测试
          </el-button>
        </div>
      </template>
      
      <div class="lesson-info" v-if="lessonInfo">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="课时标题">{{ lessonInfo.title }}</el-descriptions-item>
          <el-descriptions-item label="课时编号">{{ lessonInfo.lessonNum }}</el-descriptions-item>
          <el-descriptions-item label="测试数量">{{ tests.length }}</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <el-table :data="tests" v-loading="loading" style="width: 100%; margin-top: 20px;">
        <el-table-column prop="id" label="测试ID" width="80" />
        <el-table-column prop="title" label="测试标题" width="200" />
        <el-table-column prop="description" label="测试描述" />
        <el-table-column prop="duration" label="时长" width="100" />
        <el-table-column prop="totalScore" label="总分" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'published' ? 'success' : 'info'">
              {{ scope.row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editTest(scope.row)">编辑</el-button>
            <el-button size="small" type="primary" @click="manageQuestions(scope.row)">题库</el-button>
            <el-button size="small" type="danger" @click="deleteTest(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑测试对话框 -->
    <el-dialog
      v-model="showAddTestDialog"
      :title="editingTest ? '编辑测试' : '创建测试'"
      width="600px"
    >
      <el-form :model="testForm" :rules="testRules" ref="testFormRef" label-width="100px">
        <el-form-item label="测试标题" prop="title">
          <el-input v-model="testForm.title" />
        </el-form-item>
        <el-form-item label="测试描述" prop="description">
          <el-input 
            v-model="testForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入测试描述"
          />
        </el-form-item>
        <el-form-item label="测试时长" prop="duration">
          <el-input-number v-model="testForm.duration" :min="10" :max="180" />
          <span style="margin-left: 10px;">分钟</span>
        </el-form-item>
        <el-form-item label="总分" prop="totalScore">
          <el-input-number v-model="testForm.totalScore" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="及格分数" prop="passScore">
          <el-input-number v-model="testForm.passScore" :min="1" :max="testForm.totalScore" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddTestDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTest">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const route = useRoute()

// 响应式数据
const loading = ref(false)
const showAddTestDialog = ref(false)
const editingTest = ref(null)
const testFormRef = ref()
const lessonInfo = ref(null)

const testForm = reactive({
  title: '',
  description: '',
  duration: 60,
  totalScore: 100,
  passScore: 60
})

const testRules = {
  title: [
    { required: true, message: '请输入测试标题', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入测试描述', trigger: 'blur' }
  ],
  duration: [
    { required: true, message: '请输入测试时长', trigger: 'blur' }
  ],
  totalScore: [
    { required: true, message: '请输入总分', trigger: 'blur' }
  ],
  passScore: [
    { required: true, message: '请输入及格分数', trigger: 'blur' }
  ]
}

const tests = ref([
  {
    id: 1,
    title: 'Vue.js 基础测试',
    description: '测试Vue.js基础知识掌握情况',
    duration: 60,
    totalScore: 100,
    status: 'published'
  },
  {
    id: 2,
    title: 'Vue.js 进阶测试',
    description: '测试Vue.js高级功能掌握情况',
    duration: 90,
    totalScore: 100,
    status: 'draft'
  }
])

// 方法
const editTest = (test) => {
  editingTest.value = test
  Object.assign(testForm, {
    title: test.title,
    description: test.description,
    duration: test.duration,
    totalScore: test.totalScore,
    passScore: test.passScore || 60
  })
  showAddTestDialog.value = true
}

const manageQuestions = (test) => {
  // TODO: 跳转到题库管理页面
  console.log('题库管理:', test)
}

const deleteTest = async (test) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试 "${test.title}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用删除测试API
    ElMessage.success('测试删除成功')
    loadTests()
  } catch {
    // 用户取消
  }
}

const saveTest = async () => {
  try {
    await testFormRef.value.validate()
    
    if (editingTest.value) {
      // TODO: 调用编辑测试API
      ElMessage.success('测试更新成功')
    } else {
      // TODO: 调用创建测试API
      ElMessage.success('测试创建成功')
    }
    
    showAddTestDialog.value = false
    resetTestForm()
    loadTests()
  } catch (error) {
    console.error('保存测试失败:', error)
  }
}

const resetTestForm = () => {
  editingTest.value = null
  Object.assign(testForm, {
    title: '',
    description: '',
    duration: 60,
    totalScore: 100,
    passScore: 60
  })
}

const loadLessonInfo = () => {
  // TODO: 调用获取课时信息API
  lessonInfo.value = {
    id: route.params.lessonId,
    title: 'Vue.js 基础入门',
    lessonNum: 1
  }
}

const loadTests = () => {
  // TODO: 调用获取测试列表API
  console.log('加载测试列表')
}

onMounted(() => {
  loadLessonInfo()
  loadTests()
})
</script>

<style scoped>
.test-management-container {
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

.lesson-info {
  margin-bottom: 20px;
}
</style> 