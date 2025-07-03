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
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loginForm = reactive({
  username: '',
  password: ''
})

const onLogin = () => {
  console.log('=== 开始登录流程 ===');
  console.log('用户名:', loginForm.username);
  console.log('密码长度:', loginForm.password.length);
  console.log('当前 authStore 状态:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token,
    user: authStore.user
  });
  
  login(loginForm.username, loginForm.password)
      .then(res => {
        console.log('=== 登录API响应 ===');
        console.log('完整响应:', res);
        console.log('响应类型:', typeof res);
        console.log('res.data:', res.data);
        console.log('res.data 类型:', typeof res.data);
        console.log('res.data.userRole:', res.data.userRole);
        console.log('UserRoleMap:', UserRoleMap);
        console.log('UserRoleMap[res.data.userRole]:', UserRoleMap[res.data.userRole]);
        
        if (res && res.data) {
          console.log('=== 开始处理登录成功 ===');
          
          // 更新 auth store
          const userInfo = {
            id: res.data.id,
            username: res.data.userAccount,
            role: UserRoleMap[res.data.userRole]
          };
          
          console.log('准备设置的用户信息:', userInfo);
          
          authStore.user = userInfo;
          authStore.token = res.data.userAccount;
          
          console.log('authStore 更新后状态:', {
            user: authStore.user,
            token: authStore.token,
            isAuthenticated: authStore.isAuthenticated
          });
          
          // 存储到 localStorage（与 auth store 保持一致）
          localStorage.setItem('token', res.data.userAccount);
          localStorage.setItem('role', UserRoleMap[res.data.userRole]);
          localStorage.setItem('userId', res.data.id);
          sessionStorage.setItem('currentWeb','主页');
          
          console.log('=== 存储信息 ===');
          console.log('localStorage token:', localStorage.getItem('token'));
          console.log('localStorage role:', localStorage.getItem('role'));
          console.log('localStorage userId:', localStorage.getItem('userId'));
          console.log('sessionStorage currentWeb:', sessionStorage.getItem('currentWeb'));
          
          console.log('=== 准备跳转 ===');
          console.log('目标路由: /dashboard');
          console.log('当前路由:', router.currentRoute.value.path);
          
          ElMessage({
            message: '登录成功',
            type: 'success'
          });
          
          console.log('开始路由跳转...');
          router.push('/dashboard').then(() => {
            console.log('路由跳转成功');
          }).catch((err) => {
            console.error('路由跳转失败:', err);
          });
          
        } else {
          console.error('=== 响应数据格式不正确 ===');
          console.error('res:', res);
          console.error('res.data:', res.data);
          ElMessage({
            message: '登录响应格式错误',
            type: 'error'
          })
        }
      })
      .catch(err => {
        console.error('=== 登录失败 ===');
        console.error('错误对象:', err);
        console.error('错误消息:', err.message);
        console.error('错误堆栈:', err.stack);
        ElMessage({
          message: err.message || '用户名或密码错误',
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
