<script setup>
import { RouterView } from 'vue-router'
import {useRouter} from 'vue-router'
import { ElMessage } from 'element-plus'
import CommonAside from '@/components/asides/commonAside.vue'
import TeacherAside from '@/components/asides/teacherAside.vue'
const router = useRouter();
const role="teacher";
const handleCommand = (command) => {
  if (command === 'onExit') {
    localStorage.removeItem('token');
    router.push('/login');
  } else if (command === 'toUserControl') {
    router.push('/');
  }
  ElMessage(`click on item ${command}`);
};
</script>

<template>
  <el-container class="main-container">
    <el-aside class="sidebar">
      <span v-if="role==='test'"><CommonAside/></span>
      <span v-else-if="role==='teacher'"><TeacherAside/></span>
    </el-aside>
    <el-container>
      <el-header class="header">
        <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="50" height="50"/>
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
