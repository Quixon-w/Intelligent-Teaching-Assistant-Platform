<script setup>
import {useRoute, useRouter} from 'vue-router'
import { onMounted, ref } from 'vue'
import { addLesson, getLessons } from '@/api/course/lesson.js'
import { ElMessage, ElMessageBox, } from 'element-plus'
import {dismissCourse, enrollCourse, findCourseByID, isMyCourse,} from '@/api/course/coures.js'
import {downloadFile, downloadUrl} from "@/api/file.js";
const router=useRouter();
const route=useRoute();
const showView=ref(0);
const dialogQuestionVisible=ref(false);
const isMine=ref(false);
const dialogPreviewVisible=ref(false);
const dialogDownloadVisible=ref(false);
const courseDetail=ref({
  name:"",
  teacher:"",
  createTime:"",
  info:"",
  students:[],
})
const lessonDetail=ref({
  lessons:[],
  lessonForm:{
    courseId:route.params.id,
    lessonName:'',
  },
  lessonQuestions:[],
})
const getLesson=()=>{
  getLessons(route.params.id)
      .then(res=>{
        lessonDetail.value.lessons=res;
      })
      .catch(err=>{ElMessage(err);})
}
const haveLessonQuestion=(lessonId)=>{
  for(let lesson of lessonDetail.value.lessons){
    if(lesson.lessonId===lessonId){
      return lesson.hasQuestion;
    }
  }
  return null;
}
const getCourseByID=()=>{
  findCourseByID(route.params.id)
      .then(res=>{
        if (res.data.code===0){
          courseDetail.value.name=res.data.data.name;
          courseDetail.value.teacher=res.data.data.teacherName;
          courseDetail.value.createTime=res.data.data.createTime;
          courseDetail.value.info=res.data.data.comment;
        }else {
          ElMessage(res.description);
        }
      })
}
const getLessonQuestion=(lessonId)=>{
  router.push('/dashboard/student/'+route.params.id+'/questions/'+lessonId);
}
const joinCourse=()=>{
  ElMessageBox.confirm('确定要加入该课程吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    enrollCourse(route.params.id)
      .then(res=>{
        ElMessage(res.data);
        if (res.data.code===0){
          ElMessageBox.alert('加入课程成功！', '提示', {})
        }
      })
  })
}
const exitCourse=()=>{
  ElMessageBox.confirm('确定要退出该课程吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    dismissCourse(sessionStorage.getItem('userId'),route.params.id)
      .then(res=>{
        ElMessage(res.data);
        if (res.data.code===0){
          ElMessageBox.alert('退出课程成功！', '提示', {})
        }
      })
  })
}
const downloadUrls=(lessonId)=>{
  for(let lesson of lessonDetail.value.lessons){
    if(lesson.lessonId===lessonId){
      lessonDetail.value.lessonDownloadUrls=lesson.outlineDownload;
    }
  }
  dialogDownloadVisible.value=true;
}

const gotoStudentStatics = (courseId) => {
  router.push({
    path: '/studentStatics',
    query: { courseId: courseId }
  })
}
const getLessonQuestionFinished=(lessonId)=>{
  router.push('/dashboard/student/questionfinished/'+lessonId);
}
onMounted(()=>{
  isMyCourse(sessionStorage.getItem('userId'), route.params.id).then(res=>{isMine.value=res;});
  getLesson();
  getCourseByID();
})
</script>

<template>
  <el-container class="class-container">
    <el-header class="class-header">
      <el-button type="info" @click="showView=0">课程信息</el-button>
      <el-button type="primary" @click="showView=1" v-if="isMine===true">课时信息</el-button>
      <el-button type="success" @click="joinCourse" v-if="isMine===false">加入课程</el-button>
      <el-button type="text" @click="gotoStudentStatics(route.params.id)" v-if="isMine===true">我的课程成绩统计</el-button>
      <el-button type="danger" @click="exitCourse" v-if="isMine===true">退出课程</el-button>
    </el-header>
    <el-main class="class-main">
      <el-card class="class-card" v-if="showView===0">
        <template #header>
          <div class="card-header">
            <span>课程信息</span>
          </div>
        </template>
        <el-text>课程名程：{{courseDetail.name}}</el-text><br>
        <el-text>任课老师：{{courseDetail.teacher}}</el-text><br>
        <el-text>创建时间：{{courseDetail.createTime}}</el-text><br>
        <el-text>课程简介：{{courseDetail.info}}</el-text>
        <template #footer>
          <el-button type="primary" @click="dialogPreviewVisible=true">查看课件</el-button>
          <el-button type="danger" @click="">下载课件</el-button>
        </template>
      </el-card>
      <el-card class="class-card" v-if="showView===1">
        <el-table :data="lessonDetail.lessons" border style="width: 100%">
          <el-table-column type="selection" width="55" />
          <el-table-column property="lessonId" v-if="false" />
          <el-table-column property="courseId" label="课程ID" width="120" />
          <el-table-column property="lessonName" label="课时名称" width="120" />
          <el-table-column property="createTime" label="创建时间" width="120" />
          <el-table-column property="isFinished" label="测验完成情况" width="120" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button v-if="haveLessonQuestion(scope.row.lessonId)===1&&scope.row.isQuestionFinished===false" size="default" @click="getLessonQuestion(scope.row.lessonId)">完成测试</el-button>
              <el-button v-if="haveLessonQuestion(scope.row.lessonId)===1&&scope.row.isQuestionFinished===true" size="default" @click="getLessonQuestionFinished(scope.row.lessonId)">查看测试完成情况</el-button>
              <el-button type="danger" @click="downloadUrls(scope.row.lessonId)" v-if="scope.row.outlineStatus===true">下载课程大纲</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-main>
  </el-container>

  <el-dialog v-model="dialogQuestionVisible" title="测验信息">
    <el-card v-for="question in lessonDetail.lessonQuestions">
      <template #header>
        <el-text>第{{question.questionId}}题</el-text>
        <el-text>{{question.questionKonwledge}}</el-text>
      </template>
      <el-text>{{question.questionContent}}<</el-text>
      <el-text>{{question.questionExplanation}}</el-text>
      <template #footer>
        <el-radio-group v-model="question.questionAnswer[0]" style="gap: 3px" disabled>
          <el-radio-button value="A" size="large" border>{{question.questionAnswer[1]}}</el-radio-button>
          <el-radio-button value="B" size="large" border>{{question.questionAnswer[2]}}</el-radio-button>
          <el-radio-button value="C" size="large" border>{{question.questionAnswer[3]}}</el-radio-button>
          <el-radio-button value="D" size="large" border>{{question.questionAnswer[4]}}</el-radio-button>
        </el-radio-group>
        <el-button type="success">向AI提问</el-button>
      </template>
    </el-card>
    <el-button type="success">完成测试</el-button>
  </el-dialog>
  <el-dialog v-model="dialogDownloadVisible" title="文件下载">
    <el-text v-for="url in lessonDetail.lessonDownloadUrls" @click="downloadUrl(url)" style=":hover{color: #409eff}">{{url}}<br></el-text>
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
