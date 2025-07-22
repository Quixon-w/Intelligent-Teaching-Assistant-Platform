<template>
  <el-dialog 
    v-model="visible" 
    :title="`自主练习 - ${knowledgePoint}`" 
    width="70%" 
    :before-close="handleClose"
    :close-on-click-modal="false"
  >
    <div class="instant-practice">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="6" animated />
        <div class="loading-text">正在生成练习题目...</div>
      </div>
      <div v-else-if="error" class="error">
        <el-alert :title="error" type="error" show-icon :closable="false" />
        <div class="action-buttons">
          <el-button type="primary" @click="generateNewQuestion">重试</el-button>
          <el-button @click="visible = false">关闭</el-button>
        </div>
      </div>
      <div v-else>
        <div class="question-info">
          <el-tag type="info">{{ difficultyText }}</el-tag>
          <el-tag type="warning">自主练习（不保存）</el-tag>
        </div>
        <div class="practice-content">
          <!-- 优先用 Markdown 渲染 -->
          <div v-if="renderedMarkdown" v-html="renderedMarkdown"></div>
          <!-- 回退为原有分段渲染 -->
          <div v-else>
            <div v-for="(block, idx) in visibleBlocks" :key="idx" class="practice-block">
              <template v-if="block.type === 'stem'">
                <b>题干：</b>{{ block.text }}
              </template>
              <template v-else-if="block.type === 'option'">
                <div style="margin-left: 1em;"><b>{{ block.text.slice(0,2) }}</b>{{ block.text.slice(2) }}</div>
              </template>
              <template v-else-if="block.type === 'answer'">
                <div v-if="showAnswer" style="margin-top: 1em;"><b>正确答案：</b>{{ block.text }}</div>
              </template>
              <template v-else-if="block.type === 'explanation'">
                <div v-if="showAnswer" style="margin-top: 0.5em;"><b>解析：</b>{{ block.text }}</div>
              </template>
              <template v-else-if="block.type === 'knowledge'">
                <div style="margin-top: 0.5em;"><b>所属知识点：</b>{{ block.text }}</div>
              </template>
              <template v-else>
                <div>{{ block.text }}</div>
              </template>
            </div>
          </div>
          <div v-if="hasAnswer || hasExplanation" class="action-buttons" style="margin-top: 1em;">
            <el-button v-if="!showAnswer" type="primary" @click="showAnswer = true">显示答案和解析</el-button>
            <el-button v-else @click="generateNewQuestion">再练一题</el-button>
            <el-button v-else @click="visible = false">完成练习</el-button>
          </div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { generateInstantPractice } from '@/api/ai'
import { marked } from 'marked'

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
    const rawText = ref('')
    const error = ref('')
    const showAnswer = ref(false)
    
    // 计算属性
    const difficultyText = computed(() => {
      const map = {
        'easy': '简单',
        'medium': '中等',
        'hard': '困难'
      }
      return map[props.difficulty] || '中等'
    })

    // 分段渲染处理
    const parsedBlocks = computed(() => {
      if (!rawText.value) return []
      // 按行分割
      const lines = rawText.value.split(/\r?\n/).map(line => line.trim()).filter(Boolean)
      const blocks = []
      let currentBlock = []
      let inAnswer = false
      let inExplanation = false
      lines.forEach(line => {
        if (/^题干：/.test(line)) {
          currentBlock.push({ type: 'stem', text: line.replace(/^题干：/, '') })
        } else if (/^[A-D]\.\s?/.test(line)) {
          currentBlock.push({ type: 'option', text: line })
        } else if (/^正确答案：/.test(line)) {
          currentBlock.push({ type: 'answer', text: line.replace(/^正确答案：/, '') })
        } else if (/^解析：/.test(line)) {
          currentBlock.push({ type: 'explanation', text: line.replace(/^解析：/, '') })
        } else if (/^所属知识点：/.test(line)) {
          currentBlock.push({ type: 'knowledge', text: line.replace(/^所属知识点：/, '') })
        } else {
          // 其他内容归入上一块或新块
          if (currentBlock.length && ['stem','option','answer','explanation','knowledge'].includes(currentBlock[currentBlock.length-1].type)) {
            currentBlock[currentBlock.length-1].text += ' ' + line
          } else {
            currentBlock.push({ type: 'other', text: line })
          }
        }
      })
      return currentBlock
    })

    // 只在点击后显示答案和解析
    const visibleBlocks = computed(() => {
      return parsedBlocks.value.filter(block => {
        if (block.type === 'answer' || block.type === 'explanation') {
          return showAnswer.value
        }
        return true
      })
    })

    const hasAnswer = computed(() => parsedBlocks.value.some(b => b.type === 'answer'))
    const hasExplanation = computed(() => parsedBlocks.value.some(b => b.type === 'explanation'))

    const generateNewQuestion = async () => {
      loading.value = true
      error.value = ''
      rawText.value = ''
      showAnswer.value = false
      try {
        const response = await generateInstantPractice(props.knowledgePoint, props.difficulty)
        if (response.success) {
          rawText.value = response.data
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

    const handleClose = async () => {
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
        visible.value = false
      } catch {
        // 用户选择继续练习
      }
    }

    watch(visible, (newVal) => {
      if (newVal) {
        generateNewQuestion()
      }
    })

    // 新增：Markdown 渲染
    const renderedMarkdown = computed(() => {
      if (!rawText.value) return ''
      try {
        const html = marked.parse(rawText.value)
        // 简单判断是否为纯文本（无标签）
        if (/<[a-z][\s\S]*>/i.test(html)) {
          return html
        }
        return ''
      } catch {
        return ''
      }
    })

    return {
      visible,
      loading,
      rawText,
      error,
      showAnswer,
      difficultyText,
      parsedBlocks,
      visibleBlocks,
      hasAnswer,
      hasExplanation,
      generateNewQuestion,
      handleClose,
      renderedMarkdown
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
  gap: 10px;
}
.question-info {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}
.practice-block {
  margin-bottom: 4px;
}
</style> 