<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>个人信息</h3>
            </div>
          </template>
          <div class="profile-info">
            <el-avatar :size="100" :src="userInfo.avatar">
              {{ userInitials }}
            </el-avatar>
            <el-upload
              class="avatar-uploader"
              action="/api/user/setAvatar"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :on-error="handleAvatarError"
              :before-upload="beforeAvatarUpload"
              :headers="uploadHeaders"
              :with-credentials="true"
              style="margin-top: 16px;"
            >
              <el-button size="small" type="primary">上传头像</el-button>
            </el-upload>
            <h4>{{ userInfo.username }}</h4>
            <p>{{ roleText }}</p>
            <p>用户ID: {{ userInfo.id }}</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>修改信息</h3>
            </div>
          </template>
          
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本信息" name="info">
              <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="user-info-form">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="form.username" />
                </el-form-item>
                <el-form-item label="账号" prop="userAccount">
                  <el-input :value="form.userAccount" disabled />
                </el-form-item>
                <el-form-item label="电话" prop="phone">
                  <el-input v-model="form.phone" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="form.email" />
                </el-form-item>
                <el-form-item label="性别" prop="gender">
                  <el-select v-model="form.gender" placeholder="请选择">
                    <el-option label="未知" :value="0" />
                    <el-option label="男" :value="1" />
                    <el-option label="女" :value="2" />
                  </el-select>
                </el-form-item>
                <el-form-item label="身份" prop="userRole">
                  <el-select v-model="form.userRole" placeholder="请选择" :disabled="!canChangeRole">
                    <el-option 
                      v-for="role in availableRoles" 
                      :key="role.value" 
                      :label="role.label" 
                      :value="role.value"
                      :disabled="role.disabled"
                    />
                  </el-select>
                  <div v-if="!canChangeRole" class="role-change-tip">
                    <el-text type="info" size="small">
                      {{ roleChangeTip }}
                    </el-text>
                  </div>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="onSubmit">保存</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            
            <el-tab-pane label="修改密码" name="password">
              <el-form 
                :model="passwordForm" 
                :rules="passwordRules"
                ref="passwordFormRef"
                label-width="100px"
              >
                <el-form-item label="原密码" prop="oldPassword">
                  <el-input 
                    v-model="passwordForm.oldPassword" 
                    type="password" 
                    show-password
                  />
                </el-form-item>
                <el-form-item label="新密码" prop="newPassword">
                  <el-input 
                    v-model="passwordForm.newPassword" 
                    type="password" 
                    show-password
                  />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input 
                    v-model="passwordForm.confirmPassword" 
                    type="password" 
                    show-password
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="changePassword">修改密码</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

import { getCurrentUser } from '@/api/user/userinfo'
import request from '@/utils/request'

const authStore = useAuthStore()

// 响应式数据
const activeTab = ref('info')
const formRef = ref()
const passwordFormRef = ref()

const userInfo = ref({
  id: '',
  username: '',
  email: '',
  phone: '',
  avatar: '',
  role: ''
})

const form = reactive({
  id: '',
  username: '',
  userAccount: '',
  phone: '',
  email: '',
  gender: 0,
  userRole: 0,
  avatar: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  phone: [{ required: false }],
  email: [{ required: false, type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  userRole: [{ required: true, message: '请选择身份', trigger: 'change' }]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 计算属性
const userInitials = computed(() => {
  const name = userInfo.value.username
  return name ? name.charAt(0).toUpperCase() : 'U'
})

const roleText = computed(() => {
  const roleMap = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return roleMap[userInfo.value.role] || '用户'
})

// 角色更改权限控制
const canChangeRole = computed(() => {
  const currentRole = userInfo.value.role
  // 管理员不能更改身份
  if (currentRole === 'admin') {
    return false
  }
  // 学生和教师可以更改身份，但不能改为管理员
  return currentRole === 'student' || currentRole === 'teacher'
})

const availableRoles = computed(() => {
  const currentRole = userInfo.value.role
  const roles = [
    { label: '学生', value: 0, disabled: false },
    { label: '教师', value: 1, disabled: false },
    { label: '管理员', value: 2, disabled: true } // 普通用户不能选择管理员
  ]
  
  // 如果是管理员，所有选项都禁用
  if (currentRole === 'admin') {
    roles.forEach(role => {
      role.disabled = true
    })
  }
  
  return roles
})

const roleChangeTip = computed(() => {
  const currentRole = userInfo.value.role
  if (currentRole === 'admin') {
    return '管理员身份不可更改'
  } else if (currentRole === 'student' || currentRole === 'teacher') {
    return '您可以在学生和教师身份之间切换，但不能更改为管理员身份'
  }
  return ''
})

// 上传头像相关
const uploadHeaders = computed(() => {
  // 如果系统使用了token认证，可以添加Authorization header
  // return { 'Authorization': 'Bearer ' + authStore.token }
  return {}
})

const handleAvatarSuccess = (response) => {
  if (response.code === 0) {
    ElMessage.success('头像上传成功')
    loadUserInfo()
    // 同步到authStore，保证侧边栏也刷新
    if (response.data) {
      authStore.user.avatar = response.data
      // 同时更新localStorage中的头像信息，确保刷新页面后头像仍然显示
      localStorage.setItem('userAvatar', response.data)
    }
  } else {
    // 优先使用后端返回的具体错误信息
    const errorMessage = response.message || response.description || '头像上传失败'
    console.error('头像上传失败，后端响应:', response)
    ElMessage.error(errorMessage)
  }
}

const handleAvatarError = (error) => {
  console.error('头像上传异常:', error)
  
  // 优先获取后端返回的详细错误信息
  let errorMessage = '头像上传失败'
  
  if (error.response?.data) {
    // 后端返回的错误信息（优先级最高）
    errorMessage = error.response.data.message || 
                  error.response.data.description || 
                  error.response.data.error ||
                  errorMessage
  } else if (error.response?.status) {
    // HTTP状态码错误
    switch (error.response.status) {
      case 400:
        errorMessage = '上传文件格式错误'
        break
      case 401:
        errorMessage = '用户未登录或登录已失效'
        break
      case 403:
        errorMessage = '没有权限上传头像'
        break
      case 413:
        errorMessage = '文件过大，请选择较小的图片'
        break
      case 500:
        errorMessage = '服务器内部错误'
        break
      default:
        errorMessage = `上传失败 (${error.response.status})`
    }
  } else if (error.message) {
    // 网络错误或其他客户端错误
    errorMessage = error.message.includes('Network') ? '网络连接失败，请检查网络' : error.message
  }
  
  ElMessage.error(errorMessage)
}

const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB!')
  }
  return isImage && isLt2M
}

// 方法
const loadUserInfo = async () => {
  console.log('=== loadUserInfo 方法被调用 ===')
  try {
    const userData = await getCurrentUser()
    console.log('getCurrentUser 返回结果:', userData)
    
    if (userData && userData.id) {
      console.log('接口返回的原始数据:', userData)
      console.log('userData.userAccount:', userData.userAccount)
      
      // 直接设置form的各个字段
      form.id = userData.id
      form.username = userData.username || userData.userAccount || ''
      form.userAccount = userData.userAccount || ''
      form.phone = userData.phone || ''
      form.email = userData.email || ''
      form.gender = userData.gender || 0
      form.userRole = userData.userRole || 0
      form.avatar = userData.avatarUrl || ''
      
      // 设置userInfo
      userInfo.value.id = userData.id
      userInfo.value.username = userData.username || userData.userAccount || ''
      userInfo.value.email = userData.email || ''
      userInfo.value.phone = userData.phone || ''
      userInfo.value.avatar = userData.avatarUrl || ''
      
      // 同步更新authStore和localStorage中的头像信息
      if (authStore.user) {
        authStore.user.avatar = userData.avatarUrl || ''
      }
      localStorage.setItem('userAvatar', userData.avatarUrl || '')
      
      // 正确映射用户角色：0-学生，1-教师，2-管理员
      if (userData.userRole === 0) {
        userInfo.value.role = 'student'
      } else if (userData.userRole === 1) {
        userInfo.value.role = 'teacher'
      } else if (userData.userRole === 2) {
        userInfo.value.role = 'admin'
      } else {
        userInfo.value.role = 'student' // 默认为学生
      }
      
      console.log('设置后的form:', form)
    console.log('form.userAccount:', form.userAccount)
      console.log('form.userAccount类型:', typeof form.userAccount)
    } else {
      console.error('接口返回数据无效:', userData)
    }
  } catch (error) {
    console.error('loadUserInfo 方法出错:', error)
  }
}

const onSubmit = async () => {
  try {
    await formRef.value.validate()
    
    // 额外的权限验证
    const currentRole = userInfo.value.role
    if (currentRole === 'admin') {
      ElMessage.error('管理员身份不可更改')
      return
    }
    
    // 防止普通用户更改为管理员身份
    if (form.userRole === 2 && currentRole !== 'admin') {
      ElMessage.error('普通用户不能更改为管理员身份')
      return
    }
    
    console.log('提交的表单数据:', form)
    
    // 准备更新数据，不包含头像字段（头像通过专门接口更新）
    const updateData = {
      id: form.id,
      username: form.username,
      userAccount: form.userAccount,
      gender: form.gender,
      phone: form.phone,
      email: form.email,
      userRole: form.userRole
    }
    
    const response = await request.post('/api/user/update', updateData)
    
    console.log('更新用户信息响应:', response)
    
    if (response.code === 0) {
        ElMessage.success('信息更新成功')
      // 重新加载用户信息以确保数据同步
      await loadUserInfo()
      // 更新 authStore 中的用户信息
      if (authStore.user) {
        authStore.user.username = form.username
        // 同步更新localStorage中的用户名
        localStorage.setItem('username', form.username)
      }
      } else {
      // 优先使用后端返回的具体错误信息
      const errorMessage = response.message || response.description || '更新失败'
      console.error('更新失败，后端响应:', response)
      ElMessage.error(errorMessage)
    }
  } catch (error) {
    console.error('提交表单异常:', error)
    
    // 优先获取后端返回的详细错误信息
    let errorMessage = '更新失败'
    
    if (error.response?.data) {
      // 后端返回的错误信息（优先级最高）
      errorMessage = error.response.data.message || 
                    error.response.data.description || 
                    error.response.data.error ||
                    errorMessage
    } else if (error.response?.status) {
      // HTTP状态码错误
      switch (error.response.status) {
        case 400:
          errorMessage = '请求参数错误'
          break
        case 401:
          errorMessage = '用户未登录或登录已失效'
          break
        case 403:
          errorMessage = '没有权限执行此操作'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        default:
          errorMessage = `请求失败 (${error.response.status})`
      }
    } else if (error.message) {
      // 网络错误或其他客户端错误
      errorMessage = error.message.includes('Network') ? '网络连接失败，请检查网络' : error.message
    }
    
    ElMessage.error(errorMessage)
  }
}

const changePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    
    const passwordChangeRequest = {
      userId: authStore.user?.id || form.id,
      oldPassword: passwordForm.value.oldPassword,
      newPassword: passwordForm.value.newPassword,
      checkPassword: passwordForm.value.confirmPassword
    }
    
    const response = await request.post('/api/user/password', passwordChangeRequest)
    
    if (response.code === 0) {
      ElMessage.success('密码修改成功，请重新登录')
      
      // 清空密码表单
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      
      // 延迟一下让用户看到成功消息，然后登出并跳转到登录页
      setTimeout(async () => {
        try {
          await authStore.logout()
          // 使用 router 跳转到登录页
          window.location.href = '/login'
        } catch (error) {
          console.error('登出失败:', error)
          // 如果登出失败，直接跳转到登录页
          window.location.href = '/login'
        }
      }, 1500)
    } else {
      // 优先使用后端返回的具体错误信息
      const errorMessage = response.message || response.description || '密码修改失败'
      console.error('密码修改失败，后端响应:', response)
      ElMessage.error(errorMessage)
    }
  } catch (error) {
    console.error('密码修改异常:', error)
    
    // 优先获取后端返回的详细错误信息
    let errorMessage = '密码修改失败'
    
    if (error.response?.data) {
      // 后端返回的错误信息（优先级最高）
      errorMessage = error.response.data.message || 
                    error.response.data.description || 
                    error.response.data.error ||
                    errorMessage
    } else if (error.response?.status) {
      // HTTP状态码错误
      switch (error.response.status) {
        case 400:
          errorMessage = '请求参数错误'
          break
        case 401:
          errorMessage = '用户未登录或登录已失效'
          break
        case 403:
          errorMessage = '没有权限执行此操作'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        default:
          errorMessage = `请求失败 (${error.response.status})`
      }
    } else if (error.message) {
      // 网络错误或其他客户端错误
      errorMessage = error.message.includes('Network') ? '网络连接失败，请检查网络' : error.message
    }
    
    ElMessage.error(errorMessage)
  }
}

onMounted(() => {
  console.log('=== ProfileView onMounted 被调用 ===')
  loadUserInfo()
})
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.profile-info {
  text-align: center;
  padding: 20px 0;
}

.profile-info h4 {
  margin: 15px 0 5px 0;
  color: #303133;
}

.profile-info p {
  margin: 5px 0;
  color: #606266;
}

.el-form {
  max-width: 400px;
  min-width: 260px;
}

.role-change-tip {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}
</style> 