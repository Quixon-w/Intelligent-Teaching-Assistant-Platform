<script setup>
import { RouterLink, RouterView } from 'vue-router'
import {useRouter} from 'vue-router'
import { ElMessage } from 'element-plus'
const router = useRouter();
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
      <el-scrollbar>
        <el-menu>
          <el-menu-item>
            <RouterLink to="/dashboard/">我的课程</RouterLink>
          </el-menu-item>
          <el-menu-item>
            <RouterLink to="/dashboard/about">占位符</RouterLink>
          </el-menu-item>
        </el-menu>
        <el-menu>
          <el-menu-item>
            <RouterLink to="/dashboard/">我的课程</RouterLink>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
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

<style scoped>
.main-container{
  display: flex;
  height: 100%;
  position: relative;
}
.sidebar{
  width: 10%;
  background-color: #304156;
  height: 100%;
  position: fixed;
  font-size: 0;
  z-index: 1001;
  overflow: hidden;
  -webkit-box-shadow: 2px 0 6px rgba(0,21,41,.35);
  box-shadow: 2px 0 6px rgba(0,21,41,.35);
}
.header{
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 90%;
  height: 7%;
  margin-left: 10%;
  font-size: 0;
  background: #ffffff;
}
.main{
  width: 90%;
  height: 93%;
  margin-left: 10%;
}
</style>
