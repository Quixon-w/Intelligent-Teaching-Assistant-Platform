<script setup>
import {useRouter} from 'vue-router'
import { reactive } from 'vue'
import { login } from '@/api/login/login.js'
import { ElMessage } from 'element-plus'
const router = useRouter();
const loginForm = reactive({
  username: '',
  password: '',
})
const onLogin = () => {
  login(loginForm.username,loginForm.password)
    .then(res=>{
      console.log(res.data.data.userAccount)
      sessionStorage.setItem('token', res.data.data.userAccount);
      router.push('/dashboard');
    })
    .catch(err=>{
      ElMessage({
        message: '用户名或密码错误',
        type: 'error',
      });
    });
}
const onRegister = () => {
  router.push('/register');
}
</script>
<template>
  <div class="login">
    <el-form :model="loginForm" class="login-form">
      <h3 class="title">登录界面</h3>
      <el-form-item prop="username" label="账户：">
        <el-input v-model="loginForm.username"/>
      </el-form-item>
      <el-form-item prop="password" label="密码：">
        <el-input v-model="loginForm.password" />
      </el-form-item>
      <el-form-item prop="onClick">
        <el-button type="primary" @click="onLogin" style="width: 100%">登录</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="info" @click="onRegister" style="width: 100%">注册</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-image: url("src/assets/images/login-background.jpg");
  background-size: cover;
}
.title {
  margin: 0px auto 30px auto;
  text-align: center;
  color: #707070;
}

.login-form {
  border-radius: 6px;
  background: #ffffff;
  width: 400px;
  padding: 25px 25px 5px 25px;
}
</style>
