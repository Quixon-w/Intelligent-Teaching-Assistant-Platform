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
      
      <div v-if="loading" class="loading-section">
        <el-loading-component />
        <p>正在加载题目...</p>
      </div>
      
      <div v-else-if="questions.length === 0" class="empty-section">
        <el-empty description="暂无题目" />
      </div>
      
      <div v-else class="questions-section">
        <div v-for="(question, index) in questions" :key="question.questionId" class="question-item">
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
import { getLessonQuestionsList, commitQuestionHistory } from '@/api/course/lesson'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const testInfo = ref(null)
const questions = ref([])
const remainingTime = ref(3600) // 60分钟
const loading = ref(false)
let timer = null

// 从路由参数获取课程ID和课时ID
const courseId = route.params.courseId
const lessonId = route.params.lessonId

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
    
    // 检查是否有未答题目
    const unansweredQuestions = questions.value.filter(q => !q.answer)
    if (unansweredQuestions.length > 0) {
      const confirmSubmit = await ElMessageBox.confirm(
        `还有 ${unansweredQuestions.length} 道题目未作答，确定要提交吗？`,
        '提示',
        {
          confirmButtonText: '确定提交',
          cancelButtonText: '继续答题',
          type: 'warning'
        }
      )
    }
    
    // 调试：打印提交前的题目数据
    console.log('提交前的题目数据:', questions.value.map(q => ({
      questionId: q.questionId,
      answer: q.answer,
      content: q.content
    })))
    
    // 调用提交测试API
    const response = await commitQuestionHistory(questions.value, lessonId)
    
    if (response.code === 0) {
      ElMessage.success('测试提交成功')
      // 跳转回课程详情页面
      router.push(`/dashboard/student/courses/${courseId}`)
    } else {
      ElMessage.error(response.message || '提交失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交测试失败:', error)
      ElMessage.error('提交失败，请重试')
    }
  }
}

const loadTestInfo = () => {
  // 根据课时ID生成测试信息
  testInfo.value = {
    id: lessonId,
    title: `课时 ${lessonId} 测试`,
    totalScore: 100,
    passScore: 60,
    duration: 60
  }
}

const loadQuestions = async () => {
  if (!lessonId) {
    ElMessage.error('缺少课时ID参数')
    return
  }
  
  try {
    loading.value = true
    const response = await getLessonQuestionsList(lessonId)
    
    if (response.code === 0 && response.data) {
      // 转换题目格式
      questions.value = response.data.map((question, index) => {
        const options = JSON.parse(question.options || '{}')
        return {
          questionId: question.questionId,
          content: question.question,
          type: 'single', // 默认为单选题
          score: 10, // 默认每题10分
          options: [
            { key: 'A', content: options.A || '' },
            { key: 'B', content: options.B || '' },
            { key: 'C', content: options.C || '' },
            { key: 'D', content: options.D || '' }
          ],
          answer: '', // 学生的答案
          correctAnswer: question.answer,
          explanation: question.explanation
        }
      })
      
      console.log('加载的题目:', questions.value)
    } else {
      ElMessage.error('加载题目失败')
    }
  } catch (error) {
    console.error('加载题目失败:', error)
    ElMessage.error('加载题目失败，请重试')
  } finally {
    loading.value = false
  }
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

onMounted(async () => {
  // 检查路由参数
  if (!courseId || !lessonId) {
    ElMessage.error('缺少必要的参数')
    router.push('/dashboard/student/my-courses')
    return
  }
  
  loadTestInfo()
  await loadQuestions()
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

.loading-section {
  text-align: center;
  padding: 40px;
}

.empty-section {
  text-align: center;
  padding: 40px;
}
</style> 