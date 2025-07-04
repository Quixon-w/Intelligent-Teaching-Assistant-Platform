import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, logout as logoutApi } from '@/api/auth'
import { mapRoleToText } from '@/utils/roleMapper'
import { getCurrentUser } from '@/api/user/userinfo'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => {
    const role = user.value?.role
    if (role === null || role === undefined) return null
    return mapRoleToText(role)
  })

  // 方法
  const login = async (username, password) => {
    try {
      loading.value = true
      const response = await loginApi(username, password)
      if (response.data && response.data.userAccount) {
        // 登录成功后，获取完整用户信息
        const userInfo = await getCurrentUser()
        const { userAccount, userRole: rawUserRole, id, avatarUrl, username: displayName } = userInfo
        const mappedRole = mapRoleToText(rawUserRole)
        user.value = {
          id,
          username: displayName || userAccount,
          userAccount,
          avatar: avatarUrl,
          role: mappedRole
        }
        token.value = userAccount
        localStorage.setItem('token', userAccount)
        localStorage.setItem('role', mappedRole)
        localStorage.setItem('userId', id)
        localStorage.setItem('userAvatar', avatarUrl || '')
        localStorage.setItem('username', displayName || userAccount)
        return { success: true, data: userInfo }
      } else {
        // 使用后端返回的错误信息
        const errorMessage = response.message || response.description || '登录失败'
        return { success: false, message: errorMessage }
      }
    } catch (error) {
      console.error('登录异常:', error)
      // 优先使用后端返回的错误信息
      let errorMessage = '登录失败'
      if (error.response?.data) {
        errorMessage = error.response.data.message || error.response.data.description || errorMessage
      } else if (error.message) {
        errorMessage = error.message
      }
      return { success: false, message: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const register = async (username, password, confirmPassword) => {
    try {
      loading.value = true
      const response = await registerApi(username, password, confirmPassword)

      console.log('注册API响应:', response)

      if (response.code === 0) {
        // 注册成功，不自动登录，返回成功状态
        return { success: true, message: '注册成功' }
      } else {
        return { success: false, message: response.description || response.message || '注册失败' }
      }
    } catch (error) {
      console.error('注册异常:', error)
      // 优先使用后端返回的错误信息
      let errorMessage = '注册失败'
      if (error.response?.data) {
        errorMessage = error.response.data.message || error.response.data.description || errorMessage
      } else if (error.message) {
        errorMessage = error.message
      }
      return { success: false, message: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await logoutApi()
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 清除本地状态
      user.value = null
      token.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('userId')
      localStorage.removeItem('userAvatar')
      localStorage.removeItem('username')
    }
  }

  const initAuth = () => {
    // 从localStorage恢复用户状态
    const storedToken = localStorage.getItem('token')
    const storedRole = localStorage.getItem('role')
    const storedUserId = localStorage.getItem('userId')
    const storedAvatar = localStorage.getItem('userAvatar')
    const storedUsername = localStorage.getItem('username')

    if (storedToken && storedRole && storedUserId) {
      token.value = storedToken

      // 确保角色是字符串格式
      const mappedRole = mapRoleToText(storedRole)

      user.value = {
        id: storedUserId,
        username: storedUsername || storedToken,
        userAccount: storedToken,
        avatar: storedAvatar,
        role: mappedRole
      }
    }
  }

  return {
    // 状态
    user,
    token,
    loading,

    // 计算属性
    isAuthenticated,
    userRole,

    // 方法
    login,
    register,
    logout,
    initAuth
  }
}) 