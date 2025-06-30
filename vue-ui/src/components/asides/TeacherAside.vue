<script setup>
import {useRouter} from 'vue-router'
import {onMounted, ref} from "vue";
import {getAllSessions, getSession} from "@/api/ai/ai.js";
const router = useRouter();
const toDashboard = () => {
  router.push('/dashboard/main');
}
const toFindCourses=()=>{
  router.push('/dashboard/findcourses');
}
const toClass = () => {
  router.push('/dashboard/teacher/class');
}
const AISessions=ref([]);
const getAISessions =async () => {
  let sessions=await getAllSessions();
  for(let session of sessions){
    let sessionName=await getSession(session);
    if(sessionName){
      AISessions.value.push({sessionId:session,sessionName:sessionName[0].content});
    }
  }
  console.log(AISessions);
}
const createAISession=()=>{
  router.push('/dashboard/aitalk/'+Date.now());
}
const toAISession=(id)=>{
  router.push('/dashboard/aitalk/'+id);
}
const toQuestions=()=>{
  router.push('/dashboard/teacher/questionodteacher');
}
onMounted(()=>{
  getAISessions();
})
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
      <el-sub-menu index="2">
        <template #title><el-text style="color: #B0C4DE">AI助手</el-text></template>
        <el-menu-item @click="toAISession(session.sessionId)" index="2-0-{{session}}" style="background: #304156" v-for="session in AISessions"><el-text style="color: #B0C4DE">{{session.sessionName}}</el-text></el-menu-item>
        <el-menu-item @click="createAISession" index="2-1" style="background: #304156"><el-text style="color: #B0C4DE">+创建新对话</el-text></el-menu-item>
      </el-sub-menu>
    </el-menu>
  </el-scrollbar>
</template>

<style scoped>
</style>
