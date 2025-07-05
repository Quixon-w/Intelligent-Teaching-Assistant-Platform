<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-form">
        <div class="form-header">
          <h2>注册</h2>
          <p>创建您的智能教学辅助平台账号</p>
        </div>
        
        <el-form 
          :model="registerForm" 
          :rules="registerRules"
          ref="registerFormRef"
          class="register-form-content"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请确认密码"
              size="large"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleRegister"
            />
          </el-form-item>
          
          <!-- 用户身份选择 -->
          <el-form-item prop="userRole">
            <div class="role-selector">
              <label class="role-label">选择身份：</label>
              <div class="role-options">
                <el-radio-group v-model="registerForm.userRole" size="large">
                  <el-radio :label="0" border>
                    <el-icon><User /></el-icon>
                    学生
                  </el-radio>
                  <el-radio :label="1" border>
                    <el-icon><UserFilled /></el-icon>
                    教师
                  </el-radio>
                </el-radio-group>
              </div>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleRegister"
              class="register-button"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="form-footer">
          <p>已有账号？</p>
          <el-button type="text" @click="goToLogin">立即登录</el-button>
        </div>
      </div>
      
      <div class="register-banner">
        <div class="banner-content">
          <h1>加入我们</h1>
          <p>成为智能教学辅助平台的一员，体验现代化的教学与学习方式</p>
          <div class="benefits">
            <div class="benefit-item">
              <el-icon><Check /></el-icon>
              <span>免费注册，立即使用</span>
            </div>
            <div class="benefit-item">
              <el-icon><Check /></el-icon>
              <span>智能AI助手支持</span>
            </div>
            <div class="benefit-item">
              <el-icon><Check /></el-icon>
              <span>丰富的教学资源</span>
            </div>
            <div class="benefit-item">
              <el-icon><Check /></el-icon>
              <span>个性化学习体验</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { User, Lock, Check, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const registerFormRef = ref()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  userRole: 0
})

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 方法
const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    const result = await authStore.register(
      registerForm.username,
      registerForm.password,
      registerForm.confirmPassword,
      registerForm.userRole
    )
    
    if (result.success) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } else {
      ElMessage.error(result.message || '注册失败')
    }
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error('注册失败，请检查输入信息')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-box {
  display: flex;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-width: 900px;
  width: 100%;
}

.register-form {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
}

.form-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.register-form-content {
  max-width: 300px;
  margin: 0 auto;
  width: 100%;
}

.register-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}

.form-footer p {
  margin: 0;
  color: #666;
}

/* 用户身份选择器样式 */
.role-selector {
  text-align: center;
}

.role-label {
  display: block;
  margin-bottom: 15px;
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.role-options {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.role-options .el-radio-group {
  display: flex;
  gap: 20px;
}

.role-options .el-radio {
  margin-right: 0;
  padding: 12px 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.role-options .el-radio:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.role-options .el-radio.is-checked {
  background: #e8f4fd;
  border-color: #409eff;
}

.role-options .el-radio__label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.register-banner {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-content {
  text-align: center;
}

.banner-content h1 {
  margin: 0 0 20px 0;
  font-size: 32px;
  font-weight: bold;
}

.banner-content p {
  margin: 0 0 40px 0;
  font-size: 16px;
  opacity: 0.9;
  line-height: 1.6;
}

.benefits {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
}

.benefit-item .el-icon {
  font-size: 18px;
  color: #67c23a;
}

@media (max-width: 768px) {
  .register-box {
    flex-direction: column;
  }
  
  .register-banner {
    display: none;
  }
  
  .register-form {
    padding: 30px 20px;
  }
}
</style> 