<script setup>
import { useRoute } from 'vue-router'
import { onMounted, ref } from 'vue'
import { addLesson, getLessons } from '@/api/course/lesson.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteCourse } from '@/api/course/coures.js'
const route=useRoute();
const showView=ref(0);
const dialogLessonFormVisible=ref(false);
const courseDetail=ref({
  name:"Class"+route.params.id,
  teacher:"K",
  info:"This is a class",
  students:['S1','S2','S3','S4','S5'],
})
const lessonDetail=ref({
  lessons:[],
  lessonForm:{
    courseId:route.params.id,
    lessonName:'',
  }
})

const getLesson=()=>{
  getLessons(route.params.id)
    .then(res=>{
      if (res.code===0){
        lessonDetail.value.lessons=res.data;
      }else {
        ElMessage(res.description);
      }
    })
    .catch(err=>{ElMessage(err);})
}
const removeCourse=()=>{
  ElMessageBox.confirm('你是否确认删除课程？', '删除请求确认', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteCourse(route.params.id)
      .then(res => {
        if (res.code === 0) {
          ElMessage.success('删除成功');
        } else {
          ElMessage.error(res.message);
        }
      })
      .catch(err => {
        ElMessage.error('删除失败: ' + err);
      });
  }).catch(() => {
    // 用户点击取消时的操作
    ElMessage.info('删除操作已取消');
  });
}
const addLessonSubmit=()=>{
  dialogLessonFormVisible.value=false;
  addLesson(lessonDetail.value.lessonForm.courseId,lessonDetail.value.lessonForm.lessonName)
    .then(res=>{
      ElMessage(res.description);
    })
    .catch(err=>{
      ElMessage(err);
    })
}

onMounted(()=>{
  getLesson();
})
</script>

<template>
  <el-container class="class-container">
    <el-header class="class-header">
      <el-button type="info" @click="showView=0">课程信息</el-button>
      <el-button type="primary" @click="showView=1">课时管理</el-button>
      <el-button type="success" @click="showView=2">学生管理</el-button>
      <el-button type="danger" @click="removeCourse">删除课程</el-button>
    </el-header>
    <el-main class="class-main">
      <el-card class="class-card" v-if="showView===0">
        <template #header>
          <div class="card-header">
            <span>课程信息</span>
          </div>
        </template>
        <el-text>课程名：{{courseDetail.name}}</el-text><br>
        <el-text>任课老师：{{courseDetail.teacher}}</el-text><br>
        <el-text>课程简介：{{courseDetail.info}}</el-text>
      </el-card>
      <el-card class="class-card" v-if="showView===1">
        <template #header>
          <el-button @click="dialogLessonFormVisible=true">添加课时</el-button>
        </template>
        <el-table :data="lessonDetail.lessons" border style="width: 100%">
          <el-table-column type="selection" width="55" />
          <el-table-column property="lessonId" v-if="false" />
          <el-table-column property="courseId" label="课程ID" width="120" />
          <el-table-column property="lessonName" label="课时名称" width="120" />
          <el-table-column property="createTime" label="创建时间" width="120" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button size="small" @click="">编辑</el-button>
              <el-button size="small" type="danger" @click="">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      <el-card class="class-card" v-if="showView===2">
        <template #header>
          <div class="card-header">
            <span>学生</span>
          </div>
        </template>
        <el-text v-for="student in courseDetail.students">学生：{{student}}<br></el-text>
      </el-card>
    </el-main>
  </el-container>

  <el-dialog v-model="dialogLessonFormVisible" title="新增课时" width="500" id="addLessonForm">
    <el-form :model="lessonDetail.lessonForm">
      <el-form-item label="课程ID" >
        <el-input v-model="lessonDetail.lessonForm.courseId" disabled />
      </el-form-item>
      <el-form-item label="课时名称" >
        <el-input v-model="lessonDetail.lessonForm.lessonName"/>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogLessonFormVisible = false">关闭</el-button>
        <el-button type="primary" @click="addLessonSubmit">确认</el-button>
      </div>
    </template>
  </el-dialog>

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
  height: 10%;
  padding: 3px;
}
.class-main{
  width: 100%;
  height: 90%;
  padding: 3px;
}
.class-card{
  width: 99%;
  height: 99%;
  overflow: hidden;
}
</style>
