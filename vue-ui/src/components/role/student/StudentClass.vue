<script setup>
import { ref } from 'vue'
import {useRouter} from 'vue-router'
const router = useRouter();
const studentClass=ref([1,4,10,11,12,13,17]);
const toClass=(id)=>{
  router.push('/dashboard/student/class/'+id);
}
</script>

<template>
  <div class="classTable">
    <div class="classOfTeacher" v-for="id in studentClass" @click="toClass(id)">
      <img src="@/assets/images/login-background.jpg" alt=""/>
      <div class="text-wrapper">
        <el-text>{{ id }}</el-text>
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
.classOfTeacher{
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
.classOfTeacher img{
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
