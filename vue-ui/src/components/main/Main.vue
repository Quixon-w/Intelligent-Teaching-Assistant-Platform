<template>
  <div>
    <el-card>
      <template #header>项目简介</template>
      教学实训智能体平台<br>
    </el-card>
    <el-card>
      <template #header>项目分工</template>
      组长:王乾旭<br>
      前端:孙逍遥、吴佳昊<br>
      后端:洪宇灿<br>
    </el-card>
    <el-card>
      <template #header>技术栈</template>
    </el-card>
    <div v-if="role==='student'">
      <StudentMain/>
    </div>
    <div v-else-if="role==='teacher'">
      <TeacherMain/>
    </div>
    <div v-else-if="role==='admin'">
      <AdminMain/>
    </div>
  </div>
</template>

<style scoped>
</style>
<script setup>
import StudentMain from "@/components/main/StudentMain.vue";
import TeacherMain from "@/components/main/TeacherMain.vue";
import AdminMain from "@/components/main/AdminMain.vue";
const role = sessionStorage.getItem("role");
</script>
