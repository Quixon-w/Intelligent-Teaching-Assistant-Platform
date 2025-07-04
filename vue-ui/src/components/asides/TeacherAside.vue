<script setup>
import {useRouter} from 'vue-router'
const router = useRouter();
const toDashboard = () => {
  router.push('/dashboard/home');
}
const toFindCourses=()=>{
  router.push('/dashboard/findcourses');
}
const toClass = () => {
  router.push('/dashboard/teacher/courses');
}
const toAIAssistant = () => {
  router.push('/dashboard/ai-assistant');
}
const toQuestions=()=>{
  router.push('/dashboard/teacher/questions');
}
</script>

<template>
  <el-text style="color: #ffffff;font-family: 华文行楷,serif;font-size:25px">教学实训智能体平台</el-text>
  <el-scrollbar>
    <el-menu class="menu">
      <el-sub-menu index="0">
        <template #title><el-text style="color: #B0C4DE">仪表盘</el-text></template>
        <el-menu-item index="0-1" style="background: #304156" @click="toDashboard"><el-text style="color: #B0C4DE">仪表盘界面</el-text></el-menu-item>
        <el-menu-item index="0-2" style="background: #304156"><el-text style="color: #B0C4DE" @click="toFindCourses">查找课程</el-text></el-menu-item>
        <el-menu-item index="0-3" style="background: #304156"><el-text style="color: #B0C4DE">数据分析</el-text></el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="1">
        <template #title><el-text style="color: #B0C4DE">课程管理</el-text></template>
        <el-menu-item @click="toClass" index="1-0" style="background: #304156"><el-text style="color: #B0C4DE">我的课程</el-text></el-menu-item>
        <el-menu-item @click="toQuestions" index="1-1" style="background: #304156"><el-text style="color: #B0C4DE">我的题库</el-text></el-menu-item>
      </el-sub-menu>
      <el-menu-item @click="toAIAssistant" index="2" style="background: #304156">
        <el-text style="color: #B0C4DE">智能助手</el-text>
      </el-menu-item>
    </el-menu>
  </el-scrollbar>
</template>

<style scoped>
</style>
