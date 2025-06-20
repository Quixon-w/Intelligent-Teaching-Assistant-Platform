<script setup>
import {useRouter} from 'vue-router'
import { reactive } from 'vue'
const router = useRouter();
const form = reactive({
  name: '',
  passsword: '',
})
const onLogin = () => {
  localStorage.setItem('token', '123456');
  router.push('/dashboard');
}
const onRegister = () => {
  router.push('/register');
}
</script>
<template>
  <el-form :model="form" label-width="auto" style="max-width: 600px">
    <el-form-item label="账户：">
      <el-input v-model="form.name" />
    </el-form-item>
    <el-form-item label="密码：">
      <el-input v-model="form.passsword" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onLogin">登录</el-button>
      <el-button type="info" @click="onRegister">注册</el-button>
    </el-form-item>
  </el-form>
</template>
<style scoped>
</style>
