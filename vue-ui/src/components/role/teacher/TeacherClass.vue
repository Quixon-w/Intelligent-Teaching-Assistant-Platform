<script setup>
import { onMounted, ref } from 'vue'
import {useRouter} from 'vue-router'
const router = useRouter();
const teacherClass=ref([]);
const toClass=(id)=>{
  router.push('/dashboard/teacher/class/'+id);
}
const getData=()=>{
  const data=ref([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
  teacherClass.value=data.value.slice((tableSetting.value.currentPage-1)*tableSetting.value.pageSize,tableSetting.value.currentPage*tableSetting.value.pageSize)
}
const tableSetting=ref({
  role:'',
  total:40,
  pageSize:10,
  currentPage:1,
})
const handleSizeChange=(number)=>{
  console.log(number);
  getData()
}
const handleCurrentChange=(number)=>{
  console.log(number);
  getData()
}
onMounted(()=>{
  getData()
})
</script>

<template>
  <div>
    <el-form :model="tableSetting" label-width="auto" style="max-width: 600px">
      <el-form-item label="课程id">
        <el-input v-model="tableSetting.role"></el-input>
      </el-form-item>
      <el-form-item label="每页大小">
        <el-input v-model="tableSetting.pageSize"></el-input>
      </el-form-item>
      <el-form-item label="当前页">
        <el-input v-model="tableSetting.currentPage"></el-input>
      </el-form-item>
    </el-form>
  </div>
  <div class="classTable">
    <div class="classOfTeacher" v-for="id in teacherClass" @click="toClass(id)">
      <img src="@/assets/images/login-background.jpg" alt=""/>
      <div class="text-wrapper">
        <el-text>{{ id }}</el-text>
      </div>
    </div>
  </div>
  <div>
    <el-pagination
      v-model:current-page="tableSetting.currentPage"
      v-model:page-size="tableSetting.pageSize"
      v-model:total="tableSetting.total"
      :page-sizes="[5, 10, 20, 40]"
      :size="'default'"
      :disabled="disabled"
      :background="background"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
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
