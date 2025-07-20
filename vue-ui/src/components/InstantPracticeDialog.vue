<template>
  <el-dialog 
    v-model="visible" 
    :title="`自主练习 - ${knowledgePoint}`" 
    width="70%" 
    :before-close="handleClose"
    :close-on-click-modal="false"
  >
    <div class="instant-practice">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <el-skeleton :rows="6" animated />
        <div class="loading-text">正在生成练习题目...</div>
      </div>
      
      <!-- 练习内容 -->
      <div v-else-if="practiceQuestion" class="practice-content">
        <!-- 题目信息 -->
        <div class="question-info">
          <el-tag type="info">{{ difficultyText }}</el-tag>
          <el-tag type="warning">自主练习（不保存）</el-tag>
        </div>
        
        <!-- 题目内容 -->
        <div class="question-section">
          <h4>题目：</h4>
          <div class="question-text">{{ practiceQuestion.question_text }}</div>
        </div>
        
        <!-- 选项 -->
        <div class="options-section">
          <h4>选项：</h4>
          <el-radio-group 
            v-model="selectedAnswer" 
            :disabled="showAnswer"
            class="options-group"
          >
            <div 
              v-for="(option, index) in practiceQuestion.options" 
              :key="index"
              class="option-item"
              :class="{ 
                'correct': showAnswer && index === correctAnswerIndex,
                'wrong': showAnswer && selectedAnswer === getOptionLabel(index) && index !== correctAnswerIndex
              }"
            >
              <el-radio :label="getOptionLabel(index)">
                <span class="option-label">{{ getOptionLabel(index) }}.</span>
                <span class="option-text">{{ option }}</span>
              </el-radio>
            </div>
          </el-radio-group>
        </div>
        
        <!-- 答题按钮 -->
        <div v-if="!showAnswer" class="action-buttons">
          <el-button 
            type="primary" 
            @click="submitAnswer"
            :disabled="!selectedAnswer"
          >
            提交答案
          </el-button>
          <el-button @click="generateNewQuestion">
            重新生成
          </el-button>
        </div>
        
        <!-- 答案和解析 -->
        <div v-if="showAnswer" class="answer-section">
          <el-divider />
          <h4>答案和解析：</h4>
          
          <div class="result-info">
            <el-tag 
              :type="isCorrect ? 'success' : 'danger'"
              size="large"
            >
              {{ isCorrect ? '回答正确！' : '回答错误' }}
            </el-tag>
            <div class="correct-answer">
              正确答案：<strong>{{ practiceQuestion.correct_answer }}</strong>
            </div>
          </div>
          
          <div class="explanation">
            <h5>解析：</h5>
            <div class="explanation-text">{{ practiceQuestion.explanation }}</div>
          </div>
          
          <div class="action-buttons">
            <el-button type="primary" @click="generateNewQuestion">
              再练一题
            </el-button>
            <el-button @click="closeDialog">
              完成练习
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error">
        <el-alert 
          :title="error" 
          type="error" 
          show-icon 
          :closable="false"
        />
        <div class="action-buttons">
          <el-button type="primary" @click="generateNewQuestion">
            重试
          </el-button>
          <el-button @click="closeDialog">
            关闭
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { generateInstantPractice } from '@/api/ai'

export default {
  name: 'InstantPracticeDialog',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    knowledgePoint: {
      type: String,
      required: true
    },
    difficulty: {
      type: String,
      default: 'medium'
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const visible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })
    
    const loading = ref(false)
    const practiceQuestion = ref(null)
    const selectedAnswer = ref('')
    const showAnswer = ref(false)
    const error = ref('')
    
    // 计算属性
    const difficultyText = computed(() => {
      const map = {
        'easy': '简单',
        'medium': '中等',
        'hard': '困难'
      }
      return map[props.difficulty] || '中等'
    })
    
    const correctAnswerIndex = computed(() => {
      if (!practiceQuestion.value) return -1
      const answer = practiceQuestion.value.correct_answer
      return answer.charCodeAt(0) - 65 // A=0, B=1, C=2, D=3
    })
    
    const isCorrect = computed(() => {
      return selectedAnswer.value === practiceQuestion.value?.correct_answer
    })
    
    // 方法
    const getOptionLabel = (index) => {
      return String.fromCharCode(65 + index) // A, B, C, D
    }
    
    const parseQuestionFromResponse = (responseText) => {
      try {
        // 解析生成的题目文本
        const lines = responseText.split('\n').filter(line => line.trim())
        let questionText = ''
        let options = []
        let correctAnswer = ''
        let explanation = ''
        let knowledgePoint = ''
        
        let currentSection = ''
        
        for (let line of lines) {
          line = line.trim()
          
          if (line.startsWith('题干：')) {
            currentSection = 'question'
            questionText = line.replace('题干：', '').trim()
          } else if (line.startsWith('A.') || line.startsWith('B.') || line.startsWith('C.') || line.startsWith('D.')) {
            currentSection = 'options'
            const option = line.substring(2).trim()
            options.push(option)
          } else if (line.startsWith('正确答案：')) {
            currentSection = 'answer'
            correctAnswer = line.replace('正确答案：', '').trim()
          } else if (line.startsWith('解析：')) {
            currentSection = 'explanation'
            explanation = line.replace('解析：', '').trim()
          } else if (line.startsWith('所属知识点：')) {
            currentSection = 'knowledge'
            knowledgePoint = line.replace('所属知识点：', '').trim()
          } else {
            // 继续当前部分的内容
            if (currentSection === 'question' && questionText) {
              questionText += ' ' + line
            } else if (currentSection === 'explanation' && explanation) {
              explanation += ' ' + line
            }
          }
        }
        
        // 验证解析结果
        if (!questionText || options.length !== 4 || !correctAnswer || !explanation) {
          throw new Error('题目格式解析失败')
        }
        
        return {
          question_text: questionText,
          options: options,
          correct_answer: correctAnswer,
          explanation: explanation,
          knowledge_point: knowledgePoint || props.knowledgePoint
        }
      } catch (error) {
        console.error('解析题目失败:', error)
        throw new Error('题目格式解析失败，请重试')
      }
    }
    
    const generateNewQuestion = async () => {
      loading.value = true
      error.value = ''
      practiceQuestion.value = null
      selectedAnswer.value = ''
      showAnswer.value = false
      
      try {
        const response = await generateInstantPractice(props.knowledgePoint, props.difficulty)
        
        if (response.success) {
          const parsedQuestion = parseQuestionFromResponse(response.data)
          practiceQuestion.value = parsedQuestion
        } else {
          error.value = response.message || '生成题目失败'
        }
      } catch (err) {
        console.error('生成即时练习失败:', err)
        error.value = err.response?.data?.detail || err.message || '生成题目失败，请重试'
      } finally {
        loading.value = false
      }
    }
    
    const submitAnswer = () => {
      if (!selectedAnswer.value) {
        ElMessage.warning('请选择一个答案')
        return
      }
      showAnswer.value = true
    }
    
    const handleClose = async () => {
      if (showAnswer.value) {
        // 如果已经显示答案，直接关闭
        closeDialog()
      } else {
        // 如果还没答题，提示用户
        try {
          await ElMessageBox.confirm(
            '确定要关闭练习吗？当前练习内容不会保存，如需保存请手动记录。',
            '提示',
            {
              confirmButtonText: '确定关闭',
              cancelButtonText: '继续练习',
              type: 'warning'
            }
          )
          closeDialog()
        } catch {
          // 用户选择继续练习
        }
      }
    }
    
    const closeDialog = () => {
      visible.value = false
      // 重置状态
      setTimeout(() => {
        practiceQuestion.value = null
        selectedAnswer.value = ''
        showAnswer.value = false
        error.value = ''
        loading.value = false
      }, 300)
    }
    
    // 监听弹窗打开，自动生成题目
    watch(visible, (newVal) => {
      if (newVal) {
        generateNewQuestion()
      }
    })
    
    return {
      visible,
      loading,
      practiceQuestion,
      selectedAnswer,
      showAnswer,
      error,
      difficultyText,
      correctAnswerIndex,
      isCorrect,
      getOptionLabel,
      generateNewQuestion,
      submitAnswer,
      handleClose,
      closeDialog
    }
  }
}
</script>

<style scoped>
.instant-practice {
  min-height: 400px;
}

.loading {
  text-align: center;
  padding: 40px;
}

.loading-text {
  margin-top: 20px;
  color: #909399;
  font-size: 14px;
}

.practice-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-info {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.question-section h4,
.options-section h4,
.answer-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.question-text {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  line-height: 1.6;
  font-size: 15px;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.option-item:hover {
  background: #f5f7fa;
}

.option-item.correct {
  background: #f0f9ff;
  border-color: #67c23a;
}

.option-item.wrong {
  background: #fef0f0;
  border-color: #f56c6c;
}

.option-label {
  font-weight: bold;
  margin-right: 8px;
  color: #409eff;
}

.option-text {
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.correct-answer {
  font-size: 16px;
  color: #303133;
}

.explanation {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.explanation h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.explanation-text {
  line-height: 1.6;
  color: #606266;
}

.error {
  text-align: center;
  padding: 40px;
}

.error .action-buttons {
  margin-top: 20px;
}
</style> 