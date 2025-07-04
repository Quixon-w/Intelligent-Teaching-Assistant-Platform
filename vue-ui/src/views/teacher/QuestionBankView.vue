<template>
  <div class="question-bank-container">
    <div class="header">
      <h2>题库管理</h2>
      <el-button type="primary" @click="showAddQuestionDialog">
        <el-icon><Plus /></el-icon>
        添加题目
      </el-button>
    </div>

    <div class="filter-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input 
            v-model="searchKeyword" 
            placeholder="搜索题目内容或知识点" 
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </el-col>
        <el-col :span="4">
          <el-button @click="resetSearch">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <div class="question-list">
      <el-table :data="questionList" style="width: 100%" v-loading="loading">
        <el-table-column prop="questionId" label="题目ID" width="80" />
        <el-table-column prop="knowledge" label="知识点" width="150" show-overflow-tooltip />
        <el-table-column prop="question" label="题目内容" show-overflow-tooltip min-width="300" />
        <el-table-column prop="answer" label="正确答案" width="100" align="center">
          <template #default="scope">
            <el-tag type="success">{{ scope.row.answer }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="选项" width="300" show-overflow-tooltip>
          <template #default="scope">
            <div class="options-display">
              <span v-for="(value, key) in parseOptions(scope.row.options)" :key="key">
                <strong>{{ key }}:</strong> {{ value }}
                <br v-if="key !== 'D'" />
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editQuestion(scope.row)">编辑</el-button>
            <el-button size="small" @click="viewQuestionDetail(scope.row)">查看</el-button>
            <el-button size="small" type="danger" @click="deleteQuestion(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination" v-if="questionList.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && questionList.length === 0" class="empty-state">
        <el-empty description="暂无题目数据">
          <el-button type="primary" @click="showAddQuestionDialog">添加第一道题目</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 添加/编辑题目对话框 -->
    <el-dialog
      v-model="showQuestionDialog"
      :title="getDialogTitle()"
      width="60%"
      @close="resetQuestionForm"
    >
      <el-form :model="questionForm" :rules="questionRules" ref="questionFormRef" label-width="100px">
        <el-form-item label="父知识点" prop="parentKnowledge">
          <el-input
            v-model="questionForm.parentKnowledge"
            placeholder="请输入父级知识点，如：数学、物理等"
            :readonly="viewingQuestion"
          />
        </el-form-item>
        <el-form-item label="子知识点" prop="childKnowledge">
          <el-input
            v-model="questionForm.childKnowledge"
            placeholder="请输入具体知识点，如：线性代数、力学等"
            :readonly="viewingQuestion"
          />
        </el-form-item>
        
        <el-form-item label="题目内容" prop="question">
          <el-input
            v-model="questionForm.question"
            type="textarea"
            :rows="4"
            placeholder="请输入题目内容"
            :readonly="viewingQuestion"
          />
        </el-form-item>

        <el-form-item label="选项A" prop="optionA">
          <el-input v-model="questionForm.optionA" placeholder="选项A内容" :readonly="viewingQuestion" />
        </el-form-item>

        <el-form-item label="选项B" prop="optionB">
          <el-input v-model="questionForm.optionB" placeholder="选项B内容" :readonly="viewingQuestion" />
        </el-form-item>

        <el-form-item label="选项C" prop="optionC">
          <el-input v-model="questionForm.optionC" placeholder="选项C内容" :readonly="viewingQuestion" />
        </el-form-item>

        <el-form-item label="选项D" prop="optionD">
          <el-input v-model="questionForm.optionD" placeholder="选项D内容" :readonly="viewingQuestion" />
        </el-form-item>

        <el-form-item label="正确答案" prop="answer">
          <el-select v-model="questionForm.answer" placeholder="请选择正确答案" :disabled="viewingQuestion">
            <el-option label="A" value="A" />
            <el-option label="B" value="B" />
            <el-option label="C" value="C" />
            <el-option label="D" value="D" />
          </el-select>
        </el-form-item>

        <el-form-item label="题目解析" prop="explanation">
          <el-input
            v-model="questionForm.explanation"
            type="textarea"
            :rows="3"
            placeholder="请输入题目解析（可选）"
            :readonly="viewingQuestion"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showQuestionDialog = false">{{ viewingQuestion ? '关闭' : '取消' }}</el-button>
          <el-button 
            v-if="!viewingQuestion" 
            type="primary" 
            @click="saveQuestion" 
            :loading="saving"
          >
            {{ editingQuestion ? '更新题目' : '添加题目' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import { showError, showDetailedError, showSuccess, showWarning, handleApiResponse, handleException } from '@/utils/errorHandler'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const allQuestions = ref([]) // 存储所有题目用于前端搜索
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const showQuestionDialog = ref(false)
const editingQuestion = ref(null)
const viewingQuestion = ref(false) // 标识是否为查看模式
const questionFormRef = ref()

// 计算总数
const total = computed(() => filteredQuestions.value.length)

// 计算过滤后的题目
const filteredQuestions = computed(() => {
  let questions = allQuestions.value
  
  // 前端搜索过滤
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    questions = questions.filter(q => 
      q.question.toLowerCase().includes(keyword) ||
      q.knowledge.toLowerCase().includes(keyword)
    )
  }
  
  return questions
})

// 计算当前页数据
const questionList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredQuestions.value.slice(start, end)
})

// 表单数据
const questionForm = reactive({
  parentKnowledge: '',
  childKnowledge: '',
  question: '',
  optionA: '',
  optionB: '',
  optionC: '',
  optionD: '',
  answer: '',
  explanation: ''
})

// 表单验证规则
const questionRules = {
  parentKnowledge: [
    { required: true, message: '请输入父知识点', trigger: 'blur' }
  ],
  childKnowledge: [
    { required: true, message: '请输入子知识点', trigger: 'blur' }
  ],
  question: [
    { required: true, message: '请输入题目内容', trigger: 'blur' }
  ],
  optionA: [
    { required: true, message: '请输入选项A', trigger: 'blur' }
  ],
  optionB: [
    { required: true, message: '请输入选项B', trigger: 'blur' }
  ],
  optionC: [
    { required: true, message: '请输入选项C', trigger: 'blur' }
  ],
  optionD: [
    { required: true, message: '请输入选项D', trigger: 'blur' }
  ],
  answer: [
    { required: true, message: '请选择正确答案', trigger: 'change' }
  ]
}

// 安全解析选项的函数
const parseOptions = (options) => {
  if (typeof options === 'string') {
    try {
      return JSON.parse(options)
    } catch (e) {
      console.error('解析选项JSON失败:', e)
      return { A: '', B: '', C: '', D: '' }
    }
  }
  return options || { A: '', B: '', C: '', D: '' }
}

// 获取题目列表
const getQuestionList = async () => {
  loading.value = true
  try {
    console.log('获取教师题库, teacherId:', authStore.user?.id)
    
    const result = await request.get('/api/question/listByTeacherId', {
      params: {
        teacherId: authStore.user?.id
      }
    })
    
    console.log('题库API响应:', result)
    
    if (result.code === 0) {
      allQuestions.value = result.data || []
      console.log('获取到题目数量:', allQuestions.value.length)
    } else {
      showDetailedError(result, '获取题目列表失败')
    }
  } catch (error) {
    handleException(error, '获取题目列表')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1 // 重置到第一页
}

// 重置搜索
const resetSearch = () => {
  searchKeyword.value = ''
  currentPage.value = 1
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 获取对话框标题
const getDialogTitle = () => {
  if (viewingQuestion.value) {
    return '查看题目详情'
  } else if (editingQuestion.value) {
    return '编辑题目'
  } else {
    return '添加题目'
  }
}

// 显示添加题目对话框
const showAddQuestionDialog = () => {
  editingQuestion.value = null
  viewingQuestion.value = false
  resetQuestionForm()
  showQuestionDialog.value = true
}

// 查看题目详情
const viewQuestionDetail = (question) => {
  editingQuestion.value = question
  viewingQuestion.value = true
  const options = parseOptions(question.options)
  
  // 处理知识点的拆分
  const knowledge = question.knowledge || ''
  const knowledgeParts = knowledge.split('/')
  
  Object.assign(questionForm, {
    parentKnowledge: knowledgeParts[0] || '',
    childKnowledge: knowledgeParts[1] || '',
    question: question.question,
    optionA: options.A || '',
    optionB: options.B || '',
    optionC: options.C || '',
    optionD: options.D || '',
    answer: question.answer,
    explanation: question.explanation || ''
  })
  
  showQuestionDialog.value = true
}

// 编辑题目
const editQuestion = (question) => {
  editingQuestion.value = question
  viewingQuestion.value = false
  const options = parseOptions(question.options)
  
  // 处理知识点的拆分
  const knowledge = question.knowledge || ''
  const knowledgeParts = knowledge.split('/')
  
  Object.assign(questionForm, {
    parentKnowledge: knowledgeParts[0] || '',
    childKnowledge: knowledgeParts[1] || '',
    question: question.question,
    optionA: options.A || '',
    optionB: options.B || '',
    optionC: options.C || '',
    optionD: options.D || '',
    answer: question.answer,
    explanation: question.explanation || ''
  })
  
  showQuestionDialog.value = true
}

// 删除题目
const deleteQuestion = async (question) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除题目"${question.question}"吗？删除后不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.log('删除题目:', question.questionId)
    
    // 调用删除题目的API
    const result = await request.post('/api/question/deleteOne', null, {
      params: {
        questionId: question.questionId
      }
    })
    
    console.log('删除题目API响应:', result)
    
    if (result.code === 0) {
      showSuccess('题目删除成功')
      
      // 从前端列表中移除已删除的题目
      const index = allQuestions.value.findIndex(q => q.questionId === question.questionId)
      if (index > -1) {
        allQuestions.value.splice(index, 1)
      }
      
      // 如果当前页没有数据了，且不是第一页，回到上一页
      if (questionList.value.length === 1 && currentPage.value > 1) {
        currentPage.value -= 1
      }
    } else {
      showDetailedError(result, '删除题目失败')
    }
    
  } catch (error) {
    if (error !== 'cancel') {
      handleException(error, '删除题目')
    }
  }
}

// 保存题目
const saveQuestion = async () => {
  try {
    await questionFormRef.value.validate()
    saving.value = true
    
    console.log('保存题目数据:', questionForm)
    
    // 合并父子知识点
    const parentKnowledge = questionForm.parentKnowledge?.trim() || ''
    const childKnowledge = questionForm.childKnowledge?.trim() || ''
    const combinedKnowledge = parentKnowledge && childKnowledge 
      ? `${parentKnowledge}/${childKnowledge}`
      : parentKnowledge || childKnowledge
    
    const questionData = {
      questionId: editingQuestion.value ? editingQuestion.value.questionId : 0,
      teacherId: parseInt(authStore.user?.id || 0),
      knowledge: combinedKnowledge,
      question: questionForm.question.trim(),
      options: {
        A: questionForm.optionA.trim(),
        B: questionForm.optionB.trim(),
        C: questionForm.optionC.trim(),
        D: questionForm.optionD.trim()
      },
      answer: questionForm.answer,
      explanation: questionForm.explanation?.trim() || ''
    }
    
    console.log('发送请求数据:', questionData)
    
    let result
    if (editingQuestion.value) {
      // 更新现有题目
      console.log('更新题目, questionId:', editingQuestion.value.questionId)
      console.log('完整的题目数据:', JSON.stringify(questionData, null, 2))
      result = await request.post('/api/question/update', questionData)
    } else {
      // 新增题目到个人题库
      console.log('新增题目到个人题库')
      console.log('新增题目数据:', JSON.stringify(questionData, null, 2))
      
      // 移除 questionId 字段，因为后端会自动生成
      const { questionId, ...addQuestionData } = questionData
      result = await request.post('/api/question/addOne', addQuestionData)
    }
    
    console.log('API响应:', result)
    
    if (result.code === 0) {
      showSuccess(editingQuestion.value ? '题目更新成功' : '题目添加成功')
      showQuestionDialog.value = false
      resetQuestionForm()
      // 重新加载题目列表
      await getQuestionList()
    } else {
      showDetailedError(result, '保存题目失败')
    }
    
  } catch (error) {
    handleException(error, '保存题目')
  } finally {
    saving.value = false
  }
}

// 重置表单
const resetQuestionForm = () => {
  editingQuestion.value = null
  viewingQuestion.value = false
  Object.assign(questionForm, {
    parentKnowledge: '',
    childKnowledge: '',
    question: '',
    optionA: '',
    optionB: '',
    optionC: '',
    optionD: '',
    answer: '',
    explanation: ''
  })
  questionFormRef.value?.resetFields()
}

onMounted(() => {
  getQuestionList()
})
</script>

<style scoped>
.question-bank-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #303133;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.question-list {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.options-display {
  font-size: 12px;
  line-height: 1.4;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-table__cell) {
  padding: 12px 0;
}

:deep(.el-dialog__body) {
  padding: 20px 20px 0;
}
</style> 