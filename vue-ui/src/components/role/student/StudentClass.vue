<script setup>
import { onMounted, ref } from 'vue'
import {useRouter} from 'vue-router'
import {getCourses, getHotCourses} from '@/api/course/coures.js'
import { ElMessage } from 'element-plus'
const router = useRouter();
const studentClass=ref([]);
const toClass=(id)=>{
  router.push('/dashboard/student/class/'+id);
}
const getData=()=>{
  getCourses(tableSetting.value.currentPage,tableSetting.value.pageSize,tableSetting.value.courseName, tableSetting.value.teacherName)
      .then(res=>{
        studentClass.value=res.data.data.records;
        tableSetting.value.total=res.data.data.total;
      }).catch(err=>{
    ElMessage(err);
  })
}
const tableSetting=ref({
  role:sessionStorage.getItem('role'),
  total:0,
  pageSize:10,
  currentPage:1,
  courseName:'',
  teacherName:'',
})
const handleSizeChange=(number)=>{
  console.log(number);
  getData()
}
const handleCurrentChange=(number)=>{
  console.log(number);
  getData()
}
const getHotCourse=()=>{
  getHotCourses().then(res=>{studentClass.value=res;}).catch(err=>{ElMessage(err);})
}
onMounted(()=>{
  //getData()
  getHotCourse()
})
</script>

<template>
  <div style="display: flex;gap: 50px">
    <el-form :model="tableSetting" label-width="auto" style="width: 600px">
      <el-form-item label="课程名称">
        <el-input v-model="tableSetting.courseName"></el-input>
      </el-form-item>
    </el-form>
    <div>
      <el-button type="primary" @click="getData()">查询课程</el-button>
    </div>
  </div>
  <div class="classTable">
    <div class="classOfStudent" v-for="course in studentClass" @click="toClass(course.id)">
      <img src="@/assets/images/login-background.jpg" alt=""/>
      <div class="text-wrapper">
        <el-text>{{ course.name }}</el-text>
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
        :disabled="false"
        :background="true"
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
  align-items: flex-start;
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
