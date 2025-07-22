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
    
    if (userResponse && userResponse.id) {
      const user = userResponse
      const userId = user.id
      const isTeacher = user.userRole === 1
      console.log('✅ 获取到用户信息:', { userId, isTeacher, userRole: user.userRole, originalUser: user })
      return { userId, isTeacher }
    } else {
      console.warn('⚠️ userResponse.id不存在:', userResponse)
    }
  } catch (error) {
    console.error('❌ 获取用户信息失败:', error)
  }
  
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
    messages: messages,
    model: "rwkv",
    stream: false,
    user_id: String(userId),
    session_id: sessionId,
    is_teacher: isTeacher
  }
  
  console.log('🚀 发送AI对话请求数据:', requestData)
  console.log('🔍 用户ID类型和值:', typeof userId, userId)
  console.log('🔍 请求数据JSON:', JSON.stringify(requestData, null, 2))
  
  try {
    const response = await fetch('/ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    })

    if (!response.ok) {
      let errorDetail = ''
      try {
        const errorResponse = await response.text()
        errorDetail = errorResponse
      } catch (e) {
        console.error('🔥 无法获取错误详情')
      }
      throw new Error(`HTTP error! status: ${response.status} - ${errorDetail}`)
    }

    // 解析JSON响应
    const responseText = await response.text()
    let result
    try {
      result = JSON.parse(responseText)
      
      // 处理双重编码的情况
      if (typeof result === 'string') {
        result = JSON.parse(result)
      }
    } catch (parseError) {
      throw new Error('响应不是有效的JSON格式')
    }
    
    // 确保返回的数据结构正确
    if (result && result.choices && Array.isArray(result.choices) && result.choices.length > 0) {
      const firstChoice = result.choices[0]
      if (firstChoice && firstChoice.message) {
        return result
      } else {
        throw new Error('AI响应中缺少message字段')
      }
    } else {
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
    const response = await aiRequest.get(`/ai/v1/users/${String(userId)}/sessions`, {
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
    const response = await aiRequest.get(`/ai/v1/users/${String(userId)}/sessions/${sessionId}/dialogues`, {
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
export async function getSessionContext(sessionId, maxMessages = 20) {
  try {
    const { userId, isTeacher } = await getUserInfo()
    const response = await aiRequest.get(`/ai/v1/qa/sessions/${String(userId)}/${sessionId}/context`, {
    params: {
      max_messages: maxMessages,
      is_teacher: isTeacher
    }
    })
    return response.context_messages || []
  } catch (error) {
    console.error('获取会话上下文失败:', error)
    return []
  }
}

// 删除会话（删除整个会话）
export async function deleteSession(sessionId) {
  try {
    const { userId, isTeacher } = await getUserInfo()
    const response = await aiRequest.delete(`/ai/v1/users/${String(userId)}/sessions/${sessionId}/dialogues`, {
      data: {
        is_teacher: isTeacher
      }
    })
    return response
  } catch (error) {
    console.error('删除会话失败:', error)
    throw error
  }
}

// 清空会话历史（清空问答会话历史）
export async function clearSessionHistory(sessionId) {
  try {
    const { userId, isTeacher } = await getUserInfo()
    const response = await aiRequest.delete(`/ai/v1/qa/sessions/${String(userId)}/${sessionId}/history`, {
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
    const response = await aiRequest.post(`/ai/v1/users/${String(userId)}/sessions/${sessionId}/dialogues`, {
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
  return aiRequest.get(`/ai/v1/users/${String(userId)}/sessions/${sessionId}/info`, {
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
      user_id: String(userId),
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
  formData.append('user_id', String(userId))
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
    user_id: String(userId),
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
  
  return aiRequest.post('/ai/v1/create/content_design', {
    user_id: String(userId),
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
      user_id: String(userId),
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
  
  return aiRequest.get(`/ai/v1/list/outlines/${String(userId)}/${courseId}/${lessonId}`).then(res => {
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
    user_id: String(userId),
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

// 上传文件（is_ask: true，文件智能问答专用）
export async function uploadFileForQA(file, sessionId, courseId, lessonNum) {
  const { userId, isTeacher } = await getUserInfo();
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);
  formData.append('user_id', String(userId));
  formData.append('is_teacher', isTeacher);
  formData.append('is_ask', true);
  if (courseId) formData.append('course_id', courseId);
  if (lessonNum) formData.append('lesson_num', lessonNum);
  // 其余参数可选
  return fetch('/ai/v1/upload', { method: 'POST', body: formData });
}

// 文件智能问答接口（search_mode: uploaded，处理双重编码）
export async function fileQA(query, sessionId, courseId, lessonNum) {
  const { userId, isTeacher } = await getUserInfo();
  const requestData = {
    query,
    user_id: String(userId),
    session_id: sessionId,
    is_teacher: isTeacher,
    course_id: courseId,
    lesson_num: lessonNum,
    top_k: 3,
    search_mode: 'uploaded',
    max_tokens: 1000,
    temperature: 0.7,
    use_context: true
  };
  const response = await fetch('/ai/v1/qa', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData)
  });
  const text = await response.text();
  let result;
  try {
    result = JSON.parse(text);
    if (typeof result === 'string') result = JSON.parse(result);
  } catch (e) {
    throw new Error('响应不是有效的JSON格式');
  }
  return result;
} 

// 生成即时自主练习题目
export async function generateInstantPractice(knowledgePoint, difficulty = 'medium') {
  return aiRequest.post('/ai/v1/practice/generate_instant', {
    knowledge_point: knowledgePoint,
    difficulty: difficulty
  }).then(res => {
    return res
  }).catch(err => {
    console.error('生成即时练习失败:', err)
    throw err
  })
} 