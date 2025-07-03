import { ElMessage, ElNotification } from 'element-plus'

/**
 * 格式化错误消息
 * @param {Object|string} error - 错误对象或错误信息
 * @param {string} defaultMessage - 默认错误消息
 * @returns {string} 格式化后的错误消息
 */
export function formatErrorMessage(error, defaultMessage = '操作失败') {
  // 如果是字符串，直接返回
  if (typeof error === 'string') {
    return error
  }
  
  // 如果是后端API响应错误
  if (error && typeof error === 'object') {
    // 优先级：description > message > 默认消息
    if (error.description && error.description.trim()) {
      // 如果有详细描述，组合message和description
      if (error.message && error.message !== error.description) {
        return `${error.message}: ${error.description}`
      }
      return error.description
    }
    
    if (error.message && error.message.trim()) {
      return error.message
    }
    
    // 处理网络请求错误
    if (error.response?.data) {
      return formatErrorMessage(error.response.data, defaultMessage)
    }
    
    // 处理axios错误
    if (error.response?.status) {
      return `请求失败 (${error.response.status}): ${error.response.statusText || '未知错误'}`
    }
    
    // 处理其他类型的错误对象
    if (error.message) {
      return error.message
    }
  }
  
  return defaultMessage
}

/**
 * 显示错误消息 - 简单提示
 * @param {Object|string} error - 错误对象或错误信息
 * @param {string} defaultMessage - 默认错误消息
 */
export function showError(error, defaultMessage = '操作失败') {
  const message = formatErrorMessage(error, defaultMessage)
  ElMessage.error(message)
  
  // 同时在控制台输出详细错误信息用于调试
  console.error('错误详情:', error)
}

/**
 * 显示详细错误消息 - 通知形式（适合长文本）
 * @param {Object|string} error - 错误对象或错误信息
 * @param {string} title - 错误标题
 * @param {string} defaultMessage - 默认错误消息
 */
export function showDetailedError(error, title = '操作失败', defaultMessage = '请稍后重试') {
  const message = formatErrorMessage(error, defaultMessage)
  
  // 如果错误信息很长，使用通知而不是消息
  if (message.length > 50) {
    ElNotification({
      title: title,
      message: message,
      type: 'error',
      duration: 6000,
      position: 'top-right'
    })
  } else {
    ElMessage.error(message)
  }
  
  // 同时在控制台输出详细错误信息用于调试
  console.error('错误详情:', error)
}

/**
 * 显示成功消息
 * @param {string} message - 成功消息
 */
export function showSuccess(message = '操作成功') {
  ElMessage.success(message)
}

/**
 * 显示警告消息
 * @param {string} message - 警告消息
 */
export function showWarning(message) {
  ElMessage.warning(message)
}

/**
 * 处理API响应结果的通用方法
 * @param {Object} result - API响应结果
 * @param {string} successMessage - 成功消息
 * @param {string} errorMessage - 错误消息
 * @returns {boolean} 是否成功
 */
export function handleApiResponse(result, successMessage = '操作成功', errorMessage = '操作失败') {
  if (result && result.code === 0) {
    if (successMessage) {
      showSuccess(successMessage)
    }
    return true
  } else {
    showDetailedError(result, '操作失败', errorMessage)
    return false
  }
}

/**
 * 处理异常的通用方法
 * @param {Error} error - 异常对象
 * @param {string} operation - 操作名称
 */
export function handleException(error, operation = '操作') {
  console.error(`${operation}失败:`, error)
  
  // 如果用户取消操作，不显示错误
  if (error === 'cancel' || error?.message === 'cancel') {
    return
  }
  
  showDetailedError(error, `${operation}失败`, `${operation}时发生错误，请稍后重试`)
} 