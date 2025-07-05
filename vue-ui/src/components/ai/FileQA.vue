<template>
  <div class="file-qa-container">
    <!-- 会话管理区域 -->
    <div class="session-management">
      <div class="session-header">
        <h3>文件问答会话</h3>
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

    <!-- 文件问答区域 -->
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
      <div class="upload-area">
        <el-upload
          :action="null"
          :http-request="handleFileUpload"
          :show-file-list="false"
          :disabled="!currentSessionId || uploading"
        >
          <el-button type="primary" :loading="uploading" :disabled="!currentSessionId || uploading">
            {{ uploading ? '上传中...' : '上传文件' }}
          </el-button>
        </el-upload>
      </div>
      <div class="messages-container" ref="messagesContainer">
        <div class="messages">
          <div 
            v-for="message in messages" 
            :key="message.id"
            :class="['message', message.role]"
          >
            <div v-if="message.type === 'file'" class="file-upload-msg">
              <el-icon><UploadFilled /></el-icon>
              文件已上传：{{ message.filename }}
            </div>
            <div v-else>
              <div class="message-avatar">
                <el-avatar v-if="message.role === 'user'" :src="userAvatar" :size="36" />
                <el-avatar v-else :size="36">AI</el-avatar>
              </div>
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          placeholder="请输入你的问题"
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, UploadFilled } from '@element-plus/icons-vue'
import { 
  uploadFileForQA, 
  fileQA, 
  getAllSessions, 
  getSessionContext, 
  deleteSession 
} from '@/api/ai'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const userAvatar = computed(() => authStore.user?.avatar || '')

const sessions = ref([])
const currentSessionId = ref('')
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const creatingSession = ref(false)
const clearingHistory = ref(false)
const deletingSession = ref('')
const uploading = ref(false)
const messagesContainer = ref()


const currentSessionName = computed(() => {
  if (!currentSessionId.value) return '请选择或创建会话'
  const session = sessions.value.find(s => s.id === currentSessionId.value)
  return session?.name || `会话 ${currentSessionId.value}`
})

const generateSessionId = () => {
  const shortTimestamp = Date.now().toString().slice(-6)
  const randomStr = Math.random().toString(36).substr(2, 4)
  return `fileqa_${shortTimestamp}_${randomStr}`
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  else if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  else if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  else return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const loadSessions = async () => {
  try {
    const sessionIds = await getAllSessions()
    const sessionsWithContext = []
    for (const sessionId of sessionIds) {
      try {
        const context = await getSessionContext(sessionId, 5)
        let sessionName = `会话 ${sessionId.split('_').slice(-1)[0]}`
        if (context && context.length > 0) {
          const lastAIMessage = context.filter(msg => msg.role === 'assistant').pop()
          if (lastAIMessage && lastAIMessage.content) {
            const preview = lastAIMessage.content.trim()
            sessionName = preview.length > 20 ? preview.substring(0, 20) + '...' : preview
          } else {
            const lastUserMessage = context.filter(msg => msg.role === 'user').pop()
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

const createNewSession = async () => {
  creatingSession.value = true
  try {
    const newSessionId = generateSessionId()
    const newSession = {
      id: newSessionId,
      name: '新对话',
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
      messages.value = [{
        id: Date.now(),
        role: 'assistant',
        content: '您好！请先上传文件，然后向我提问。',
        timestamp: new Date()
      }]
    }
    scrollToBottom()
  } catch (error) {
    messages.value = [{
      id: Date.now(),
      role: 'assistant',
      content: '您好！请先上传文件，然后向我提问。',
      timestamp: new Date()
    }]
    scrollToBottom()
  }
}

const deleteSessionHandler = async (sessionId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个会话吗？删除后无法恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    deletingSession.value = sessionId
    await deleteSession(sessionId)
    const index = sessions.value.findIndex(s => s.id === sessionId)
    if (index > -1) {
      sessions.value.splice(index, 1)
    }
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

const clearCurrentSession = async () => {
  if (!currentSessionId.value) return
  try {
    await ElMessageBox.confirm('确定要清空当前会话的历史记录吗？', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    clearingHistory.value = true
    messages.value = [{
      id: Date.now(),
      role: 'assistant',
      content: '历史记录已清空。请重新上传文件并提问。',
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

const handleFileUpload = async (option) => {
  uploading.value = true
  try {
    await uploadFileForQA(option.file, currentSessionId.value)
    messages.value.push({ id: Date.now(), type: 'file', filename: option.file.name, role: 'system', timestamp: new Date() })
    ElMessage.success('文件上传成功，可开始提问')
    scrollToBottom()
  } catch (error) {
    ElMessage.error('文件上传失败')
  } finally {
    uploading.value = false
  }
}

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
    const result = await fileQA(currentMessage, currentSessionId.value)
    const aiContent = result?.answer
    if (!aiContent) throw new Error('AI回复内容为空')
    const aiMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: aiContent.trim(),
      timestamp: new Date()
    }
    messages.value.push(aiMessage)
    scrollToBottom()
  } catch (error) {
    const errorMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: '抱歉，文件问答失败，请稍后再试。',
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
    scrollToBottom()
    ElMessage.error('发送消息失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadSessions()
  if (sessions.value.length === 0) {
    await createNewSession()
  } else {
    await switchSession(sessions.value[0].id)
  }
})
</script>

<style scoped>
.file-qa-container {
  display: flex;
  height: 100%;
  background: #f8f9fa;
}
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
.upload-area {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
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
.file-upload-msg {
  color: #409EFF;
  font-size: 14px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}
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
</style> 