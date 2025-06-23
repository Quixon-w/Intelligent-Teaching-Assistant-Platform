<script setup>
import {useRouter} from 'vue-router'
import { reactive } from 'vue'
import { register } from '@/api/register/register.js'
import { ElMessage } from 'element-plus'
const router = useRouter();
const registerForm = reactive({
  username: '',
  password: '',
  checkpassword: ''
})
const onSubmit = () => {
  register(registerForm.username,registerForm.password,registerForm.checkpassword)
    .then(res=>{
      if(res.data.code === 0){
        sessionStorage.setItem('token', registerForm.username);
        sessionStorage.setItem('role', 'student');
        router.push('/dashboard');
      }
      else {
        ElMessage(res.data.description)
      }
  }).catch(err=>{
    ElMessage(err);
  })
}
const onCancel = () => {
router.push('/login');
}
</script>
<template>
  <div class="register">
    <el-form :model="registerForm" class="register-form">
      <h3 class="title">注册界面</h3>
      <el-form-item prop="username" label="账户：">
        <el-input v-model="registerForm.username"/>
      </el-form-item>
      <el-form-item prop="password" label="密码：">
        <el-input v-model="registerForm.password" />
      </el-form-item>
      <el-form-item prop="apassword" label="确认密码：">
        <el-input v-model="registerForm.checkpassword" />
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
