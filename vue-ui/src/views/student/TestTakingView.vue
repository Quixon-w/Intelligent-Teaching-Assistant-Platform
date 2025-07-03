<template>
  <div class="test-taking-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>在线测试</h3>
          <div class="test-info">
            <span>剩余时间: {{ formatTime(remainingTime) }}</span>
            <el-button type="primary" @click="submitTest">提交测试</el-button>
          </div>
        </div>
      </template>
      
      <div v-if="testInfo" class="test-info-section">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="测试标题">{{ testInfo.title }}</el-descriptions-item>
          <el-descriptions-item label="总分">{{ testInfo.totalScore }}分</el-descriptions-item>
          <el-descriptions-item label="及格分数">{{ testInfo.passScore }}分</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <div class="questions-section">
        <div v-for="(question, index) in questions" :key="question.id" class="question-item">
          <div class="question-header">
            <h4>第{{ index + 1 }}题 ({{ question.score }}分)</h4>
          </div>
          <div class="question-content">
            <p>{{ question.content }}</p>
            
            <!-- 单选题 -->
            <div v-if="question.type === 'single'" class="options">
              <el-radio-group v-model="question.answer">
                <el-radio 
                  v-for="option in question.options" 
                  :key="option.key" 
                  :label="option.key"
                >
                  {{ option.key }}. {{ option.content }}
                </el-radio>
              </el-radio-group>
            </div>
            
            <!-- 多选题 -->
            <div v-if="question.type === 'multiple'" class="options">
              <el-checkbox-group v-model="question.answer">
                <el-checkbox 
                  v-for="option in question.options" 
                  :key="option.key" 
                  :label="option.key"
                >
                  {{ option.key }}. {{ option.content }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
            
            <!-- 填空题 -->
            <div v-if="question.type === 'fill'" class="fill-answer">
              <el-input 
                v-model="question.answer" 
                placeholder="请输入答案"
                type="textarea"
                :rows="3"
              />
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

// 响应式数据
const testInfo = ref(null)
const questions = ref([])
const remainingTime = ref(3600) // 60分钟
let timer = null

// 模拟测试数据
const mockTestInfo = {
  id: 1,
  title: 'Vue.js 基础测试',
  totalScore: 100,
  passScore: 60,
  duration: 60
}

const mockQuestions = [
  {
    id: 1,
    type: 'single',
    content: 'Vue.js 是什么类型的框架？',
    score: 10,
    options: [
      { key: 'A', content: '后端框架' },
      { key: 'B', content: '前端框架' },
      { key: 'C', content: '数据库框架' },
      { key: 'D', content: '移动端框架' }
    ],
    answer: ''
  },
  {
    id: 2,
    type: 'multiple',
    content: 'Vue.js 的核心特性包括哪些？',
    score: 20,
    options: [
      { key: 'A', content: '响应式数据绑定' },
      { key: 'B', content: '组件化开发' },
      { key: 'C', content: '虚拟DOM' },
      { key: 'D', content: '路由管理' }
    ],
    answer: []
  },
  {
    id: 3,
    type: 'fill',
    content: '请简述Vue.js的生命周期钩子函数有哪些？',
    score: 30,
    answer: ''
  }
]

// 方法
const formatTime = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const submitTest = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要提交测试吗？提交后将无法修改答案。',
      '提示',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '继续答题',
        type: 'warning'
      }
    )
    
    // TODO: 调用提交测试API
    ElMessage.success('测试提交成功')
    router.push('/student/my-courses')
  } catch {
    // 用户取消
  }
}

const loadTestInfo = () => {
  // TODO: 调用获取测试信息API
  testInfo.value = mockTestInfo
}

const loadQuestions = () => {
  // TODO: 调用获取题目列表API
  questions.value = mockQuestions
}

const startTimer = () => {
  timer = setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
    } else {
      clearInterval(timer)
      ElMessage.warning('测试时间已到，系统将自动提交')
      submitTest()
    }
  }, 1000)
}

onMounted(() => {
  loadTestInfo()
  loadQuestions()
  startTimer()
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.test-taking-container {
  max-width: 1000px;
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

.test-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.test-info span {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
}

.test-info-section {
  margin-bottom: 30px;
}

.questions-section {
  margin-top: 20px;
}

.question-item {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

.question-header h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.question-content p {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.options {
  margin-top: 15px;
}

.options .el-radio,
.options .el-checkbox {
  display: block;
  margin-bottom: 10px;
}

.fill-answer {
  margin-top: 15px;
}
</style> 