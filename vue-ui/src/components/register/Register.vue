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
  checkpassword: ''
})

const onSubmit = () => {
  register(registerForm.username, registerForm.password, registerForm.checkpassword)
      .then(res => {
        if (res.data.code === 0) {
          sessionStorage.setItem('token', registerForm.username)
          sessionStorage.setItem('role', 'student')
          router.push('/dashboard')
        } else {
          ElMessage(res.data.description)
        }
      })
      .catch(err => {
        ElMessage(err)
      })
}

const goToLogin = () => {
  router.push('/login')
}
</script>
<style>
@import "../../assets/css/login.css";
</style>
