<template>
  <div class="body">
    <div class="main-box">
      <!-- 注册容器 -->
      <div :class="['container', 'container-register']">
        <form @submit.prevent="onSubmit">
          <h2 class="title">注册</h2>
          <input class="form__input" type="text" v-model="registerForm.username" placeholder="请输入用户名"/>
          <input class="form__input" type="password" v-model="registerForm.password" placeholder="请输入密码"/>
          <input class="form__input" type="password" v-model="registerForm.checkpassword" placeholder="请确认密码"/>
          
          <!-- 用户身份选择 -->
          <div class="role-selector">
            <label class="role-label">选择身份：</label>
            <div class="role-options">
              <label class="role-option">
                <input 
                  type="radio" 
                  v-model="registerForm.userRole" 
                  :value="0" 
                  name="userRole"
                />
                <span class="role-text">学生</span>
              </label>
              <label class="role-option">
                <input 
                  type="radio" 
                  v-model="registerForm.userRole" 
                  :value="1" 
                  name="userRole"
                />
                <span class="role-text">教师</span>
              </label>
            </div>
          </div>
          
          <div class="form__button" @click="onSubmit">立即注册</div>
        </form>
      </div>

      <div class="switch">
        <div class="switch__container">
          <h2>欢迎回来 !</h2>
          <p>如果您已经注册过账号，请点击下方立即登录按钮进行登录</p>
          <div class="form__button" @click="goToLogin">立即登录</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { reactive } from 'vue'
import { register } from '@/api/register/register.js'
import { ElMessage } from 'element-plus'

const router = useRouter()
const registerForm = reactive({
  username: '',
  password: '',
  checkpassword: '',
  userRole: 0
})

const onSubmit = () => {
  register(registerForm.username, registerForm.password, registerForm.checkpassword, registerForm.userRole)
      .then(res => {
        console.log('注册响应:', res)
        if (res.code === 0) {
          ElMessage.success('注册成功！请登录')
          router.push('/login')
        } else {
          ElMessage.error(res.description || res.message || '注册失败')
        }
      })
      .catch(err => {
        console.error('注册错误:', err)
        ElMessage.error(err.message || '注册失败，请检查输入信息')
      })
}

const goToLogin = () => {
  router.push('/login')
}
</script>
<style>
@import "../../assets/css/login.css";

/* 用户身份选择器样式 */
.role-selector {
  margin: 20px 0;
  text-align: center;
}

.role-label {
  display: block;
  margin-bottom: 10px;
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.role-options {
  display: flex;
  justify-content: center;
  gap: 30px;
}

.role-option {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  background: #f5f5f5;
  transition: all 0.3s ease;
}

.role-option:hover {
  background: #e8f4fd;
}

.role-option input[type="radio"] {
  margin-right: 8px;
  cursor: pointer;
}

.role-option input[type="radio"]:checked + .role-text {
  color: #409eff;
  font-weight: 600;
}

.role-text {
  font-size: 14px;
  color: #666;
  transition: all 0.3s ease;
}

.role-option:has(input[type="radio"]:checked) {
  background: #e8f4fd;
  border: 1px solid #409eff;
}
</style>
