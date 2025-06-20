<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <el-container class="layout-common-container" style="width: 100%;height: 100%">
    <el-header style="width: 100%;height: 10%;display: flex;align-items: center;justify-content: space-between">
      <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="50" height="50"/>
      <el-dropdown>
        <span>
          <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="50" height="50"/>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>Action 1</el-dropdown-item>
            <el-dropdown-item>Action 2</el-dropdown-item>
            <el-dropdown-item>Action 3</el-dropdown-item>
            <el-dropdown-item disabled>Action 4</el-dropdown-item>
            <el-dropdown-item divided>Action 5</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </el-header>
    <el-container style="width: 100%;height: 90%">
      <el-aside style="width: 10%;height: 100%">
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
      <el-main style="width: 90%;height: 100%">
        <Router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-common-container .el-header {
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
}
.layout-common-container .el-aside {
  color: var(--el-text-color-primary);
  background: var(--el-color-primary-light-8);
}
.layout-common-container .el-menu {
  border-right: none;
}
.layout-common-container .el-main {
  padding: 0;
}
.layout-common-container .toolbar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  right: 20px;
}
</style>
