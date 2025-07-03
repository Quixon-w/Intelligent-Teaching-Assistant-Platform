<script setup>
import { useRoute } from 'vue-router'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'

const route = useRoute()
</script>

<template>
  <el-container class="dashboard-container">
    <Sidebar />
    <el-container>
      <Header />
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.dashboard-container {
  height: 100vh;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
