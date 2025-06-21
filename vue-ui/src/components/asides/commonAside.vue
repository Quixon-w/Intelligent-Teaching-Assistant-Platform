<script setup>
import {useRouter} from 'vue-router'
const router = useRouter();
const toHome = () => {
  router.push('/dashboard')
}
const toAbout = () => {
  router.push('/dashboard/about')
}
</script>

<template>
  <el-text style="color: #ffffff;font-family: 华文行楷,serif;font-size:25px">教学实训智能体平台</el-text>
  <el-scrollbar>
    <el-menu class="menu">
      <el-menu-item @click="toHome" index="1"><el-text style="color: #B0C4DE">我的课程</el-text></el-menu-item>
      <el-menu-item @click="toAbout" index="2"><el-text style="color: #B0C4DE" >我的课程</el-text></el-menu-item>
      <el-menu-item index="3"><el-text style="color: #B0C4DE">我的课程</el-text></el-menu-item>
    </el-menu>
  </el-scrollbar>
</template>

<style scoped>
</style>
