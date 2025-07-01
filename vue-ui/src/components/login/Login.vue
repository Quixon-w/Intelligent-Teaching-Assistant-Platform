<template>
  <div class="body">
    <div class="main-box">
      <!-- 登录容器 -->
      <div :class="['container', 'container-login']">
        <form @submit.prevent="onLogin">
          <h2 class="title">登录</h2>
          <input class="form__input" type="text" v-model="loginForm.username" placeholder="账户"/>
          <input class="form__input" type="password" v-model="loginForm.password" placeholder="请输入密码"/>
          <div class="form__button" @click="onLogin">立即登录</div>
        </form>
      </div>

      <!-- 注册切换面板 -->
      <div class="switch">
        <div class="switch__container">
          <h2>您好 !</h2>
          <p>如果您还没有账号，请点击下方立即注册按钮进行账号注册</p>
          <div class="form__button" @click="goToRegister">立即注册</div>
        </div>
      </div>


    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { reactive } from 'vue'
import { login } from '@/api/login/login.js'
import { ElMessage } from 'element-plus'
import UserRoleMap from '@/utils/userrole.js'

const router = useRouter()
const loginForm = reactive({
  username: '',
  password: ''
})

const onLogin = () => {
  login(loginForm.username, loginForm.password)
      .then(res => {
        sessionStorage.setItem('token', res.data.data.userAccount);
        sessionStorage.setItem('role', UserRoleMap[res.data.data.userRole]);
        sessionStorage.setItem('userId',res.data.data.id);
        sessionStorage.setItem('currentWeb','主页');
        router.push('/dashboard');
      })
      .catch(err => {
        ElMessage({
          message: '用户名或密码错误',
          type: 'error'
        })
      })
}

const goToRegister = () => {
  router.push('/register')
}
</script>
<style>
@import "../../assets/css/login.css";
</style>
