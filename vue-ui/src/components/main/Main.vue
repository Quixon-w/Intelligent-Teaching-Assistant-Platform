<template>
  <div>
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="项目信息" name="projectInfo">
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
          前端:Vue3 + Element Plus + TypeScript<br>
          后端:SpringBoot + MyBatis + MySQL<br>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="用户端介绍" name="userIntroduction">
        <div v-if="role === 'student'">
          <StudentMain />
        </div>
        <div v-else-if="role === 'teacher'">
          <TeacherMain />
        </div>
        <div v-else-if="role === 'admin'">
          <AdminMain />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import StudentMain from "@/components/main/StudentMain.vue";
import TeacherMain from "@/components/main/TeacherMain.vue";
import AdminMain from "@/components/main/AdminMain.vue";
import {ref} from "vue";

const role = sessionStorage.getItem("role");
const activeTab = ref("projectInfo");
</script>

<style scoped>
</style>
