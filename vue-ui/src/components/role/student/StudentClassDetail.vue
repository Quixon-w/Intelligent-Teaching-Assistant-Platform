<script setup>
import { useRoute } from 'vue-router'
import { ref } from 'vue'
const route=useRoute();
const classDetail=ref({
  name:"Class"+route.params.id,
  teacher:"K",
  info:"This is a class",
  students:['S1','S2','S3','S4','S5'],
})
</script>

<template>
  <el-container class="class-container">
    <el-header class="class-header">
      <el-card class="class-card">
        <template #header>
          <div class="card-header">
            <span>课程信息</span>
          </div>
        </template>
        <el-text>课程名：{{classDetail.name}}</el-text><br>
        <el-text>任课老师：{{classDetail.teacher}}</el-text><br>
        <el-text>课程简介：{{classDetail.info}}</el-text>
      </el-card>
    </el-header>
    <el-container>
      <el-aside class="class-aside">
        <el-card class="class-card">
          <template #header>
            <div class="card-header" style="display: flex;justify-content: space-between;">
              <span>课时</span>
              <el-button type="primary">新建课时</el-button>
            </div>
          </template>
          <div style="display: flex;justify-content: space-between;">
            <el-text>课时：2025-6-10 10:00</el-text>
            <div>
              <el-button type="primary">增加测试</el-button>
              <el-button type="primary">查看测试结果</el-button>
            </div>
          </div>
        </el-card>
      </el-aside>
      <el-main class="class-main">
        <el-card class="class-card">
          <template #header>
            <div class="card-header">
              <span>学生</span>
            </div>
          </template>
          <el-text v-for="student in classDetail.students">学生：{{student}}<br></el-text>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.class-container{
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
}
.class-header{
  width: 100%;
  height: 40%;
  padding: 3px;
}
.class-aside{
  width: 50%;
  height: 100%;
  padding: 3px;
}
.class-main{
  width: 50%;
  height: 100%;
  padding: 3px;
}
.class-card{
  width: 99%;
  height: 99%;
  overflow: hidden;
}
</style>
