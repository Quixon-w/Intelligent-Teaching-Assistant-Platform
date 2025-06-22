<script setup>
import {useRouter} from 'vue-router'
const router = useRouter();
const toClass = () => {
  router.push('/dashboard/teacher/class');
}
</script>

<template>
  <el-text style="color: #ffffff;font-family: 华文行楷,serif;font-size:25px">教学实训智能体平台</el-text>
  <el-scrollbar>
    <el-menu class="menu">
      <el-sub-menu index="0">
        <template #title><el-text style="color: #B0C4DE">仪表盘</el-text></template>
        <el-menu-item index="0-1" style="background: #304156"><el-text style="color: #B0C4DE">仪表盘界面</el-text></el-menu-item>
        <el-menu-item index="0-2" style="background: #304156"><el-text style="color: #B0C4DE">数据分析</el-text></el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="1">
        <template #title><el-text style="color: #B0C4DE">课程管理</el-text></template>
        <el-menu-item @click="toClass" index="1" style="background: #304156"><el-text style="color: #B0C4DE">我的课程</el-text></el-menu-item>
      </el-sub-menu>
    </el-menu>
  </el-scrollbar>
</template>

<style scoped>
</style>
