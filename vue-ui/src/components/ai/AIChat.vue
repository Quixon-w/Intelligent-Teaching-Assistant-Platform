<template>
  <div class="ai-chat-container">
    <!-- 会话管理区域 -->
    <div class="session-management">
      <div class="session-header">
        <h3>会话管理</h3>
        <el-button type="primary" @click="createNewSession" :loading="creatingSession">
          <el-icon><Plus /></el-icon>
          新建会话
        </el-button>
      </div>
      
      <div class="session-list">
        <div 
          v-for="session in sessions" 
          :key="session.id"
          :class="['session-item', { active: session.id === currentSessionId }]"
          @click="switchSession(session.id)"
        >
          <div class="session-info">
            <span class="session-name">{{ session.name || `会话 ${session.id}` }}</span>
            <span class="session-time">{{ formatTime(session.lastActive) }}</span>
          </div>
          <el-button 
            size="small" 
            type="danger" 
            text
            @click.stop="deleteSessionHandler(session.id)"
            :loading="deletingSession === session.id"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-area">
      <div class="chat-header">
        <h3>{{ currentSessionName }}</h3>
        <div class="chat-controls">
          <el-button 
            size="small" 
            type="warning" 
            @click="clearCurrentSession"
            :loading="clearingHistory"
            :disabled="!currentSessionId || messages.length === 0"
          >
            <el-icon><Delete /></el-icon>
            清空历史
          </el-button>
        </div>
      </div>
      
      <div class="messages-container" ref="messagesContainer">
        <div class="messages">
          <div 
            v-for="message in messages" 
            :key="message.id"
            :class="['message', message.role]"
          >
            <div class="message-avatar">
              <el-avatar :size="36">
                {{ message.role === 'user' ? 'U' : 'AI' }}
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="loading" class="message assistant loading-message">
            <div class="message-avatar">
              <el-avatar :size="36">AI</el-avatar>
            </div>
            <div class="message-content">
              <div class="message-text">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          placeholder="请输入您的问题..."
          type="textarea"
          :rows="3"
          resize="none"
          :disabled="loading || !currentSessionId"
          @keyup.ctrl.enter="sendMessage"
        />
        <div class="input-controls">
          <span class="input-hint">Ctrl + Enter 发送</span>
          <el-button 
            type="primary" 
            @click="sendMessage"
            :loading="loading"
            :disabled="!inputMessage.trim() || !currentSessionId"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { 
  chatCompletions, 
  getAllSessions, 
  getSessionHistory, 
  clearSessionHistory,
  saveSessionHistory,
  getSessionContext,
  deleteSession
} from '@/api/ai'

// 响应式数据
const sessions = ref([])
const currentSessionId = ref('')
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const creatingSession = ref(false)
const clearingHistory = ref(false)
const deletingSession = ref('')
const messagesContainer = ref()


// 计算属性
const currentSessionName = computed(() => {
  if (!currentSessionId.value) return '请选择或创建会话'
  const session = sessions.value.find(s => s.id === currentSessionId.value)
  return session?.name || `会话 ${currentSessionId.value}`
})

// 生成会话ID
const generateSessionId = () => {
  // 使用更短的格式：取时间戳后6位 + 4位随机字符
  const shortTimestamp = Date.now().toString().slice(-6)
  const randomStr = Math.random().toString(36).substr(2, 4)
  return `chat_${shortTimestamp}_${randomStr}`
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) { // 小于1分钟
    return '刚刚'
  } else if (diff < 3600000) { // 小于1小时
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 小于1天
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 加载会话列表
const loadSessions = async () => {
  try {
    const sessionIds = await getAllSessions()
    const sessionsWithContext = []
    
    // 为每个会话加载上下文以获取最后一次AI回复
    for (const sessionId of sessionIds) {
      try {
        const context = await getSessionContext(sessionId, 5) // 只获取最近5条消息
        let sessionName = `会话 ${sessionId.split('_').slice(-1)[0]}`
        
        // 查找最后一次AI回复
        if (context && context.length > 0) {
          const lastAIMessage = context
            .filter(msg => msg.role === 'assistant')
            .pop()
          
          if (lastAIMessage && lastAIMessage.content) {
            // 取AI回复内容的前20个字符作为会话名称
            const preview = lastAIMessage.content.trim()
            sessionName = preview.length > 20 ? preview.substring(0, 20) + '...' : preview
          } else {
            // 如果没有AI回复，查找用户最后一条消息
            const lastUserMessage = context
              .filter(msg => msg.role === 'user')
              .pop()
            
            if (lastUserMessage && lastUserMessage.content) {
              const preview = lastUserMessage.content.trim()
              sessionName = '问：' + (preview.length > 15 ? preview.substring(0, 15) + '...' : preview)
            }
          }
        }
        
        sessionsWithContext.push({
          id: sessionId,
          name: sessionName,
          lastActive: new Date()
        })
      } catch (error) {
        // 如果获取上下文失败，使用默认名称
        sessionsWithContext.push({
          id: sessionId,
          name: `会话 ${sessionId.split('_').slice(-1)[0]}`,
      lastActive: new Date()
        })
      }
    }
    
    sessions.value = sessionsWithContext
  } catch (error) {
    console.error('❌ 加载会话失败:', error)
    sessions.value = []
  }
}

// 创建新会话
const createNewSession = async () => {
  creatingSession.value = true
  try {
    const newSessionId = generateSessionId()
    const newSession = {
      id: newSessionId,
      name: '新对话', // 使用更友好的默认名称
      lastActive: new Date()
    }
    
    sessions.value.unshift(newSession)
    await switchSession(newSessionId)
    
    ElMessage.success('新会话创建成功')
  } catch (error) {
    console.error('创建会话失败:', error)
    ElMessage.error('创建会话失败')
  } finally {
    creatingSession.value = false
  }
}

// 切换会话
const switchSession = async (sessionId) => {
  if (currentSessionId.value === sessionId) return
  
  currentSessionId.value = sessionId
  messages.value = []
  
  try {
    const context = await getSessionContext(sessionId, 20)
    
    if (context && context.length > 0) {
      messages.value = context.map(msg => ({
        id: msg.id || Date.now() + Math.random(),
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
      }))
    } else {
      // 添加欢迎消息
      messages.value = [{
        id: Date.now(),
        role: 'assistant',
        content: '您好！我是您的AI智能助手。我可以帮助您解答各种问题，请随时向我提问。',
        timestamp: new Date()
      }]
    }
    
    scrollToBottom()
  } catch (error) {
    console.warn('⚠️ 加载会话上下文失败:', error)
    
    // 如果失败，创建一个新的干净会话
    messages.value = [{
      id: Date.now(),
      role: 'assistant',
      content: '您好！我是您的AI智能助手。我可以帮助您解答各种问题，请随时向我提问。',
      timestamp: new Date()
    }]
    scrollToBottom()
  }
}

// 删除会话
const deleteSessionHandler = async (sessionId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个会话吗？删除后无法恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    deletingSession.value = sessionId
    
    // 调用删除会话API
    await deleteSession(sessionId)
    
    // 从列表中移除
    const index = sessions.value.findIndex(s => s.id === sessionId)
    if (index > -1) {
      sessions.value.splice(index, 1)
    }
    
    // 如果删除的是当前会话，切换到其他会话或清空
    if (currentSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        await switchSession(sessions.value[0].id)
      } else {
        currentSessionId.value = ''
        messages.value = []
      }
    }
    
    ElMessage.success('会话删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除会话失败:', error)
      ElMessage.error('删除会话失败')
    }
  } finally {
    deletingSession.value = ''
  }
}

// 清空当前会话历史
const clearCurrentSession = async () => {
  if (!currentSessionId.value) return
  
  try {
    await ElMessageBox.confirm('确定要清空当前会话的历史记录吗？', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    clearingHistory.value = true
    
    await clearSessionHistory(currentSessionId.value)
    
    // 重置消息，只保留欢迎消息
    messages.value = [{
      id: Date.now(),
      role: 'assistant',
      content: '历史记录已清空。我是您的AI智能助手，请随时向我提问。',
      timestamp: new Date()
    }]
    
    scrollToBottom()
    ElMessage.success('历史记录已清空')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空历史失败:', error)
      ElMessage.error('清空历史失败')
    }
  } finally {
    clearingHistory.value = false
  }
}

// 更新当前会话名称
const updateCurrentSessionName = (aiContent) => {
  if (!currentSessionId.value || !aiContent) return
  
  const currentSession = sessions.value.find(s => s.id === currentSessionId.value)
  if (currentSession) {
    // 取AI回复内容的前20个字符作为会话名称
    const preview = aiContent.trim()
    currentSession.name = preview.length > 20 ? preview.substring(0, 20) + '...' : preview
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value || !currentSessionId.value) return
  
  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date()
  }
  
  messages.value.push(userMessage)
  const currentMessage = inputMessage.value.trim()
  inputMessage.value = ''
  loading.value = true
  
  scrollToBottom()
  
  try {
    // 调用AI API - 发送当前消息（后端会自动管理历史记录上下文）
    const result = await chatCompletions(currentSessionId.value, currentMessage)
    
    const aiContent = result?.choices?.[0]?.message?.content
    
    if (!aiContent) {
      throw new Error('AI回复内容为空')
    }
    
    // 添加AI回复
    const aiMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: aiContent.trim(),
      timestamp: new Date()
    }
    
    messages.value.push(aiMessage)
    scrollToBottom()
    
    // 更新当前会话的名称
    updateCurrentSessionName(aiContent.trim())
    
  } catch (error) {
    console.error('发送消息失败:', error)
    
    // 添加错误消息
    const errorMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: '抱歉，我暂时无法回复您的问题。请稍后再试。',
      timestamp: new Date()
    }
    
    messages.value.push(errorMessage)
    scrollToBottom()
    
    ElMessage.error('发送消息失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 组件挂载时初始化
onMounted(async () => {
  await loadSessions()
  
  // 如果没有会话，创建一个新会话
  if (sessions.value.length === 0) {
    await createNewSession()
  } else {
    // 切换到第一个会话
    await switchSession(sessions.value[0].id)
  }
})
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  height: 100%;
  background: #f8f9fa;
}

/* 会话管理区域 */
.session-management {
  width: 300px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.session-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 16px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.session-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-item:hover {
  background: #e9ecef;
}

.session-item.active {
  background: #667eea;
  color: white;
}

.session-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.session-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.session-time {
  font-size: 12px;
  opacity: 0.7;
}

/* 聊天区域 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 16px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.messages {
  max-width: 800px;
  margin: 0 auto;
}

.message {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .message-content {
  background: #667eea;
  color: white;
  margin-right: 12px;
}

.message.assistant .message-content {
  background: #f1f3f4;
  color: #1f2937;
  margin-left: 12px;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
}

.message-text {
  line-height: 1.5;
  margin-bottom: 4px;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
}

/* 输入区域 */
.input-area {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  background: #f8f9fa;
}



.input-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-hint {
  font-size: 12px;
  color: #6b7280;
}

/* 加载动画 */
.loading-message .typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-chat-container {
    flex-direction: column;
  }
  
  .session-management {
    width: 100%;
    height: 200px;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style> 