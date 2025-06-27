<script setup>
import { onMounted, ref } from 'vue'
import {useRouter} from 'vue-router'
import {getCoursesOfStu} from '@/api/course/coures.js'
import { ElMessage } from 'element-plus'
const router = useRouter();
const studentClass=ref([]);
const toClass=(id)=>{
  router.push('/dashboard/student/class/'+id);
}
const getData=()=>{
  getCoursesOfStu(sessionStorage.getItem('userId')).then(res=>{
    studentClass.value=res.data.data;
  })
}
onMounted(()=>{
  getData();
})
</script>

<template>
  <div class="classTable">
    <div class="classOfStudent" v-for="course in studentClass" @click="toClass(course.id)">
      <img src="@/assets/images/login-background.jpg" alt=""/>
      <div class="text-wrapper">
        <el-text>{{ course.name }}</el-text>
      </div>
    </div>
  </div>
</template>

<style scoped>
.classTable{
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
  //justify-content: space-between; /* 子元素平均分布 */
  align-items: center; /* 垂直居中 */
  gap: 2%; /* 每个子项之间的间距为 2% */
  width: 100%;
  height: 100%;
}
.classOfStudent{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 23%;
  height: 30%;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}
.classOfStudent img{
  flex: 9;
  width: 100%;
  height: 80%;
  object-fit: cover;
}
.text-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
</style>
