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
        <el-skeleton :rows="8" animated />
      </div>
      
      <div v-else-if="questions.length === 0" class="empty-section">
        <el-empty description="暂无题目" />
      </div>
      
      <div v-else class="questions-section">
        <el-card 
          v-for="(question, index) in questions" 
          :key="question.questionId"
          class="question-card"
          shadow="hover"
        >
          <template #header>
            <div class="question-header">
              <div class="question-info">
                <el-tag type="primary" size="small">第{{ index + 1 }}题</el-tag>
                <el-tag v-if="question.knowledge" type="info" size="small">
                  {{ question.knowledge }}
                </el-tag>
              </div>
            </div>
          </template>
          
          <div class="question-content">
            <!-- 题目内容 -->
            <div class="question-text-container">
              <p class="question-text">{{ question.content }}</p>
            </div>
            
            <!-- 选项 -->
            <div class="question-options">
              <el-radio-group 
                v-model="question.answer"
                class="options-group"
                size="large"
              >
                <el-radio value="A" class="option-item">
                  <div class="option-content">
                    <span class="option-label">A</span>
                    <span class="option-text">{{ question.options.A }}</span>
                  </div>
                </el-radio>
                <el-radio value="B" class="option-item">
                  <div class="option-content">
                    <span class="option-label">B</span>
                    <span class="option-text">{{ question.options.B }}</span>
                  </div>
                </el-radio>
                <el-radio value="C" class="option-item">
                  <div class="option-content">
                    <span class="option-label">C</span>
                    <span class="option-text">{{ question.options.C }}</span>
                  </div>
                </el-radio>
                <el-radio value="D" class="option-item">
                  <div class="option-content">
                    <span class="option-label">D</span>
                    <span class="option-text">{{ question.options.D }}</span>
                  </div>
                </el-radio>
              </el-radio-group>
            </div>
          </div>
        </el-card>
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
      // 转换题目格式，处理options字段
      questions.value = response.data.map((question, index) => {
        let options = {}
        try {
          // 如果options是字符串，尝试解析
          if (typeof question.options === 'string') {
            options = JSON.parse(question.options)
          } else if (typeof question.options === 'object') {
            options = question.options
          }
        } catch (e) {
          console.error('解析options失败:', e)
          options = {}
        }
        
        return {
          questionId: question.questionId,
          content: question.question,
          knowledge: question.knowledge,
          options: options,
          answer: '', // 学生的答案
          correctAnswer: question.answer,
          explanation: question.explanation
        }
      })
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
  padding: 20px;
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

.question-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.question-content {
  padding: 16px 0;
}

.question-text-container {
  margin-bottom: 20px;
}

.question-text {
  font-size: 16px;
  line-height: 1.6;
  color: #303133;
  margin: 0;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.question-options {
  margin-bottom: 24px;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.option-item {
  width: 100%;
  margin: 0;
}

.option-item :deep(.el-radio__input) {
  display: none;
}

.option-item :deep(.el-radio__label) {
  padding: 0;
  width: 100%;
}

.option-content {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  background-color: #ffffff;
  transition: all 0.3s ease;
  cursor: pointer;
  min-height: 60px;
}

.option-item:hover .option-content {
  border-color: #409eff;
  background-color: #f0f9ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.option-item :deep(.el-radio__input.is-checked) + .el-radio__label .option-content {
  border-color: #409eff;
  background-color: #f0f9ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.option-label {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: #f5f7fa;
  color: #606266;
  border-radius: 50%;
  margin-right: 16px;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.option-item :deep(.el-radio__input.is-checked) + .el-radio__label .option-label {
  background-color: #409eff;
  color: white;
}

.option-text {
  flex: 1;
  font-size: 16px;
  color: #303133;
  line-height: 1.5;
  font-weight: 500;
}

.loading-section {
  text-align: center;
  padding: 40px;
}

.empty-section {
  text-align: center;
  padding: 40px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .test-taking-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .test-info {
    width: 100%;
    justify-content: center;
  }
  
  .question-content {
    padding: 12px 0;
  }
  
  .question-text {
    font-size: 14px;
  }
  
  .option-content {
    padding: 12px 16px;
    min-height: 50px;
  }
  
  .option-label {
    width: 28px;
    height: 28px;
    font-size: 14px;
    margin-right: 12px;
  }
  
  .option-text {
    font-size: 14px;
  }
}
</style> 