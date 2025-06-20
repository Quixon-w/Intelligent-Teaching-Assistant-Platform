<script setup>
import {useRouter} from 'vue-router'
import { reactive } from 'vue'
const router = useRouter();
const registerForm = reactive({
username: '',
passsword: '',
})
const onSubmit = () => {
  localStorage.setItem('token', '123456');
  router.push('/dashboard');
}
const onCancel = () => {
router.push('/login');
}
</script>
<template>
  <div class="register">
    <el-form :model="registerForm" class="register-form">
      <h3 class="title">登录界面</h3>
      <el-form-item prop="username" label="账户：">
        <el-input v-model="registerForm.username"/>
      </el-form-item>
      <el-form-item prop="password" label="密码：">
        <el-input v-model="registerForm.passsword" />
      </el-form-item>
      <el-form-item prop="onClick">
        <el-button type="primary" @click="onSubmit" style="width: 100%">注册</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="info" @click="onCancel" style="width: 100%">返回</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
<style scoped>
.register {
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
.register-form {
  border-radius: 6px;
  background: #ffffff;
  width: 400px;
  padding: 25px 25px 5px 25px;
}
</style>
