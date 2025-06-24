<script setup>
import { RouterView } from 'vue-router'
import {useRouter} from 'vue-router'
import { ElMessage } from 'element-plus'
import CommonAside from '@/components/asides/AdminAside.vue'
import TeacherAside from '@/components/asides/TeacherAside.vue'
import { onExit } from '@/api/dashboard.js'
import StudentAside from '@/components/asides/StudentAside.vue'
const router = useRouter();
const role=sessionStorage.getItem('role');
const handleCommand = (command) => {
  if (command === 'onExit') {
    onExit().then(res=>{
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('role');
      router.push('/login');
    }).catch(err=>{
      ElMessage({
        message: '退出失败',
        type: 'error',
      });
    })
  } else if (command === 'toUserControl') {
    router.push('/dashboard/user/central');
  }
};
</script>

<template>
  <el-container class="main-container">
    <el-aside class="sidebar">
      <span v-if="role==='admin'"><CommonAside/></span>
      <span v-else-if="role==='teacher'"><TeacherAside/></span>
      <span v-else-if="role==='student'"><StudentAside/></span>
    </el-aside>
    <el-container>
      <el-header class="header">
        <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="50" height="50"/>
        <el-button type="success" @click="router.push('/dashboard/aitalk')">与ai对话</el-button>
        <div>
          <el-text style="color: #B0C4DE;font-size: 30px">{{role}}</el-text>
          <el-dropdown @command="handleCommand">
            <span>
              <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="50" height="50"/>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="toUserControl">用户中心</el-dropdown-item>
                <el-dropdown-item command="onExit">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <Router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
<style src="@/assets/css/dashboard/dashboard.css"></style>
<style scoped>
</style>
