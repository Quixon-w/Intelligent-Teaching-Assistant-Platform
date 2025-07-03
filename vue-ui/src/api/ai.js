import request from '@/utils/request.js'
import axios from 'axios'
import { getCurrentUser } from '@/api/user/userinfo.js'

// 专门用于AI API的请求实例（不使用通用拦截器）
const aiRequest = axios.create({
  timeout: 30000,
  withCredentials: true
})

// AI API专用拦截器
aiRequest.interceptors.response.use(
  response => {
    console.log('🤖 AI API响应:', response.data)
    return response.data
  },
  error => {
    console.error('🤖 AI API错误:', error)
    return Promise.reject(error)
  }
)

// 获取用户信息
const getUserInfo = async () => {
  try {
    const userResponse = await getCurrentUser()
    console.log('🔍 getUserInfo - 原始响应:', userResponse)
    
    if (userResponse && userResponse.data) {
      const user = userResponse.data
      const userId = user.id  // 直接使用id字段
      const isTeacher = user.userRole === 1  // userRole为1表示teacher
      console.log('✅ 获取到用户信息:', { userId, isTeacher, userRole: user.userRole, originalUser: user })
      return { userId, isTeacher }
    }
  } catch (error) {
    console.error('❌ 获取用户信息失败:', error)
  }
  
  // 失败时返回默认值
  console.warn('⚠️ 使用默认用户信息')
  return { userId: 'anonymous', isTeacher: false }
}

// AI对话完成接口
export async function chatCompletions(sessionId, currentMessage) {
  const { userId, isTeacher } = await getUserInfo()
  
  // 将当前消息包装成messages数组格式
  const messages = [{
    role: 'user',
    content: currentMessage
  }]
  
  const requestData = {
    messages: messages,  // 使用messages数组格式
    model: "rwkv",
    stream: false,
    user_id: userId,
    session_id: sessionId,
    is_teacher: isTeacher
  }
  
  console.log('🚀 发送AI对话请求:', requestData)
  
  try {
    const response = await fetch('/ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    })
    
    console.log('📡 请求状态:', response.status, response.statusText)
    console.log('📡 Response Headers详细信息:')
    console.log('  - Content-Type:', response.headers.get('content-type'))
    console.log('  - 所有Headers:', Object.fromEntries(response.headers.entries()))

    if (!response.ok) {
      let errorDetail = ''
      try {
        const errorResponse = await response.text()
        errorDetail = errorResponse
        console.error('🔥 API错误详情:', errorResponse)
      } catch (e) {
        console.error('🔥 无法获取错误详情')
      }
      throw new Error(`HTTP error! status: ${response.status} - ${errorDetail}`)
    }

    // 首先尝试获取原始文本，查看是否真的是JSON
    const responseText = await response.text()
    console.log('📄 原始响应文本:', responseText)
    console.log('📄 原始响应文本类型:', typeof responseText)
    
    // 然后手动解析JSON
    let result
    try {
      result = JSON.parse(responseText)
      console.log('✅ 第一次JSON解析成功')
      console.log('🔍 第一次解析后的result类型:', typeof result)
      
      // 检查是否需要二次解析（双重编码的情况）
      if (typeof result === 'string') {
        console.log('⚠️ 检测到双重JSON编码，进行二次解析...')
        try {
          result = JSON.parse(result)
          console.log('✅ 二次JSON解析成功')
          console.log('🔍 二次解析后的result类型:', typeof result)
        } catch (secondParseError) {
          console.error('❌ 二次JSON解析失败:', secondParseError)
          // 如果二次解析失败，保持第一次解析的结果
        }
      }
      
      console.log('🔍 最终result类型:', typeof result)
      console.log('🔍 最终result是否为对象:', result && typeof result === 'object')
    } catch (parseError) {
      console.error('❌ JSON解析失败:', parseError)
      console.log('🔍 尝试解析的文本:', responseText)
      throw new Error('响应不是有效的JSON格式')
    }
    
    console.log('🤖 AI对话API响应对象:', result)
    
    // 详细打印响应结构
    console.log('📊 详细响应结构分析:')
    console.log('🔹 Response对象信息:')
    console.log('  - status:', response.status)
    console.log('  - statusText:', response.statusText)
    console.log('  - headers:', Object.fromEntries(response.headers.entries()))
    
    console.log('🔹 Result对象完整结构:')
    console.log('  - result类型:', typeof result)
    console.log('  - result是否为对象:', result && typeof result === 'object')
    if (result && typeof result === 'object') {
      console.log('  - result的所有键:', Object.keys(result))
      console.log('  - result.choices存在:', 'choices' in result)
      console.log('  - result.choices类型:', typeof result.choices)
      console.log('  - result.choices是数组:', Array.isArray(result.choices))
    }
    console.log('  - result完整内容:', JSON.stringify(result, null, 2))
    
    if (result && result.choices) {
      console.log('🔹 Choices数组详细信息:')
      console.log('  - choices类型:', typeof result.choices)
      console.log('  - choices是否为数组:', Array.isArray(result.choices))
      console.log('  - choices长度:', result.choices.length)
      console.log('  - choices完整内容:', JSON.stringify(result.choices, null, 2))
      
      if (result.choices.length > 0) {
        console.log('🔹 第一个Choice详细信息:')
        const firstChoice = result.choices[0]
        console.log('  - choice类型:', typeof firstChoice)
        console.log('  - choice的所有键:', Object.keys(firstChoice || {}))
        console.log('  - choice完整内容:', JSON.stringify(firstChoice, null, 2))
        
        if (firstChoice && firstChoice.message) {
          console.log('🔹 Message对象详细信息:')
          console.log('  - message类型:', typeof firstChoice.message)
          console.log('  - message的所有键:', Object.keys(firstChoice.message || {}))
          console.log('  - message完整内容:', JSON.stringify(firstChoice.message, null, 2))
          console.log('  - content内容:', firstChoice.message.content)
          console.log('  - content类型:', typeof firstChoice.message.content)
        }
      }
    } else {
      console.log('❌ result.choices不存在或为空')
    }
    
    // 确保返回的数据结构正确
    if (result && result.choices && Array.isArray(result.choices) && result.choices.length > 0) {
      const firstChoice = result.choices[0]
      if (firstChoice && firstChoice.message) {
        console.log('✅ AI回复内容:', firstChoice.message.content)
        return result
      } else {
        console.error('❌ choices[0].message不存在')
        throw new Error('AI响应中缺少message字段')
      }
    } else {
      console.error('❌ AI响应结构异常 - choices数组问题')
      throw new Error('AI响应格式不正确')
    }
  } catch (error) {
    console.error('🔥 AI对话API请求失败:', error)
    throw error
  }
}

// 获取用户的所有会话
export async function getAllSessions() {
  try {
    const { userId, isTeacher } = await getUserInfo()
    const response = await aiRequest.get(`/ai/v1/users/${userId}/sessions`, {
      params: {
        is_teacher: isTeacher
      }
    })
    console.log('🔍 会话列表响应:', response)
    return response.sessions || []
  } catch (error) {
    console.error('获取会话失败:', error)
    return []
  }
}

// 获取会话历史对话
export async function getSessionHistory(sessionId, limit = 10) {
  try {
    const { userId, isTeacher } = await getUserInfo()
    const response = await aiRequest.get(`/ai/v1/users/${userId}/sessions/${sessionId}/dialogues`, {
      params: {
        limit: limit,
        is_teacher: isTeacher
      }
    })
    console.log('🔍 会话历史响应:', response)
    return response.dialogues || []
  } catch (error) {
    console.error('获取会话历史失败:', error)
    return []
  }
}

// 获取会话上下文
export async function getSessionContext(sessionId, maxMessages = 10) {
  const { userId, isTeacher } = await getUserInfo()
  return aiRequest.get(`/ai/v1/users/${userId}/sessions/${sessionId}/context`, {
    params: {
      max_messages: maxMessages,
      is_teacher: isTeacher
    }
  }).then(res => {
    return res.context_messages || []
  }).catch(err => {
    console.error('获取会话上下文失败:', err)
    return []
  })
}

// 清空会话历史
export async function clearSessionHistory(sessionId) {
  try {
    const { userId, isTeacher } = await getUserInfo()
    const response = await aiRequest.delete(`/ai/v1/users/${userId}/sessions/${sessionId}/dialogues`, {
      data: {
        is_teacher: isTeacher
      }
    })
    return response
  } catch (error) {
    console.error('清空会话历史失败:', error)
    throw error
  }
}

// 保存会话历史（如果后端需要）
export async function saveSessionHistory(sessionId, messages) {
  try {
    const { userId, isTeacher } = await getUserInfo()
    const response = await aiRequest.post(`/ai/v1/users/${userId}/sessions/${sessionId}/dialogues`, {
      messages: messages,
      is_teacher: isTeacher
    })
    return response
  } catch (error) {
    console.error('保存会话历史失败:', error)
    throw error
  }
}

// 获取会话信息
export async function getSessionInfo(sessionId) {
  const { userId, isTeacher } = await getUserInfo()
  return aiRequest.get(`/ai/v1/users/${userId}/sessions/${sessionId}/info`, {
    params: {
      is_teacher: isTeacher
    }
  }).then(res => {
    return res
  }).catch(err => {
    console.error('获取会话信息失败:', err)
    return null
  })
}

// 智能问答接口
export async function intelligentQA(query, sessionId, courseId = null, lessonNum = null) {
  const { userId, isTeacher } = await getUserInfo()
  
  return fetch('/ai/v1/qa', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      user_id: userId,
      session_id: sessionId,
      is_teacher: isTeacher,
      course_id: courseId,
      lesson_num: lessonNum,
      top_k: 3,
      search_mode: "existing",
      max_tokens: 1000,
      temperature: 0.7,
      use_context: true
    })
  })
}

// 文件上传接口
export async function uploadFile(file, sessionId, courseId = null, lessonNum = null, isResource = false, isAsk = false) {
  const { userId, isTeacher } = await getUserInfo()
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('session_id', sessionId)
  formData.append('user_id', userId)
  formData.append('is_teacher', isTeacher)
  
  if (courseId) formData.append('course_id', courseId)
  if (lessonNum) formData.append('lesson_num', lessonNum)
  formData.append('is_resource', isResource)
  formData.append('is_ask', isAsk)
  
  return fetch('/ai/v1/upload', {
    method: 'POST',
    body: formData
  })
}

// 获取系统状态
export function getSystemStatus() {
  return aiRequest.get('/ai/status').then(res => {
    return res
  }).catch(err => {
    console.error('获取系统状态失败:', err)
    throw err
  })
}

// 获取知识库状态
export function getKnowledgeStatus() {
  return aiRequest.get('/ai/v1/knowledge/status').then(res => {
    return res
  }).catch(err => {
    console.error('获取知识库状态失败:', err)
    throw err
  })
}

// 搜索知识库
export async function searchKnowledge(query, courseId = null, lessonNum = null, topK = 5) {
  const { userId, isTeacher } = await getUserInfo()
  
  return aiRequest.post('/ai/v1/knowledge/search', {
    query: query,
    user_id: userId,
    is_teacher: isTeacher,
    course_id: courseId,
    lesson_num: lessonNum,
    is_ask: false,
    top_k: topK,
    use_rerank: true
  }).then(res => {
    return res
  }).catch(err => {
    console.error('搜索知识库失败:', err)
    throw err
  })
}

// 创建课程大纲
export async function createLessonOutline(courseId, lessonId) {
  const { userId, isTeacher } = await getUserInfo()
  
  return aiRequest.post('/ai/v1/create/outline', {
    user_id: userId,
    session_id: `outline_${Date.now()}`,
    course_id: courseId,
    lesson_num: lessonId,
    is_teacher: isTeacher,
    max_words: 1000
  }).then(res => {
    return res
  }).catch(err => {
    console.error('创建课程大纲失败:', err)
    throw err
  })
}

// 检查课程大纲状态
export async function lessonOutlineStatus(courseId, lessonId) {
  const { userId, isTeacher } = await getUserInfo()
  
  return aiRequest.get('/ai/v1/create/outline/status', {
    params: {
      user_id: userId,
      course_id: courseId,
      lesson_num: lessonId,
      is_teacher: isTeacher
    }
  }).then(res => {
    return res.has_outline
  }).catch(err => {
    console.error('检查课程大纲状态失败:', err)
    throw err
  })
}

// 下载课程大纲
export async function lessonOutlineDownload(courseId, lessonId) {
  const { userId } = await getUserInfo()
  
  return aiRequest.get(`/ai/v1/list/outlines/${userId}/${courseId}/${lessonId}`).then(res => {
    const files = res.files || []
    const urls = files.map(file => file.download_url)
    return urls
  }).catch(err => {
    console.error('下载课程大纲失败:', err)
    throw err
  })
}

// 生成习题
export async function generateExercises(courseId, lessonId, questionCount = 5, difficulty = 'medium') {
  const { userId, isTeacher } = await getUserInfo()
  
  return aiRequest.post('/ai/v1/exercise/generate', {
    user_id: userId,
    session_id: `exercise_${Date.now()}`,
    course_id: courseId,
    lesson_num: lessonId,
    is_teacher: isTeacher,
    question_count: questionCount,
    difficulty: difficulty,
    max_tokens: 2000,
    temperature: 0.7,
    generation_mode: 'block'
  }).then(res => {
    return res
  }).catch(err => {
    console.error('生成习题失败:', err)
    throw err
  })
} 