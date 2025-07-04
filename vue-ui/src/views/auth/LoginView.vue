<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-form">
        <div class="form-header">
          <h2>登录</h2>
          <p>欢迎使用智能教学辅助平台</p>
        </div>
        
        <el-form 
          :model="loginForm" 
          :rules="loginRules"
          ref="loginFormRef"
          class="login-form-content"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleLogin"
              class="login-button"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="form-footer">
          <p>还没有账号？</p>
          <el-button type="text" @click="goToRegister">立即注册</el-button>
        </div>
      </div>
      
      <div class="login-banner">
        <div class="banner-content">
          <h1>智能教学辅助平台</h1>
          <p>为教育工作者和学生提供智能化的教学与学习体验</p>
          <div class="features">
            <div class="feature-item">
              <el-icon><Reading /></el-icon>
              <span>智能课程管理</span>
            </div>
            <div class="feature-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI智能助手</span>
            </div>
            <div class="feature-item">
              <el-icon><EditPen /></el-icon>
              <span>在线测试系统</span>
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
import { User, Lock, Reading, ChatDotRound, EditPen } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 方法
const handleLogin = async () => {
  console.log('=== 开始登录流程 ===');
  console.log('用户名:', loginForm.username);
  console.log('密码长度:', loginForm.password.length);
  console.log('当前 authStore 状态:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token,
    user: authStore.user
  });
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    console.log('=== 调用 authStore.login ===');
    const result = await authStore.login(loginForm.username, loginForm.password)
    
    console.log('=== authStore.login 结果 ===');
    console.log('result:', result);
    
    if (result.success) {
      console.log('=== 登录成功，准备跳转 ===');
      console.log('authStore 状态:', {
        isAuthenticated: authStore.isAuthenticated,
        token: authStore.token,
        user: authStore.user
      });
      
      ElMessage.success('登录成功')
      console.log('开始跳转到 /dashboard/home');
      router.push('/dashboard/home').then(() => {
        console.log('路由跳转成功');
      }).catch((err) => {
        console.error('路由跳转失败:', err);
      });
    } else {
      console.error('=== 登录失败 ===');
      console.error('失败原因:', result.message);
      ElMessage.error(result.message || '登录失败')
    }
  } catch (error) {
    console.error('=== 登录异常 ===');
    console.error('错误对象:', error);
    console.error('错误消息:', error.message);
    console.error('错误堆栈:', error.stack);
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-box {
  display: flex;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-width: 900px;
  width: 100%;
}

.login-form {
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

.login-form-content {
  max-width: 300px;
  margin: 0 auto;
  width: 100%;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}

.form-footer p {
  margin: 0 0 10px 0;
  color: #909399;
  font-size: 14px;
}

.login-banner {
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

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
}

.feature-item .el-icon {
  font-size: 20px;
}

@media (max-width: 768px) {
  .login-box {
    flex-direction: column;
  }
  
  .login-banner {
    display: none;
  }
  
  .login-form {
    padding: 30px 20px;
  }
}
</style> 