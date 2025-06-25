<script setup>
import { useRoute } from 'vue-router'
import { onMounted, ref } from 'vue'
import { getLessonQuestions,addLesson, getLessons } from '@/api/course/lesson.js'
import { ElMessage, ElMessageBox, } from 'element-plus'
import {deleteCourse, findCourseByID, getAllStudents, updateCourse} from '@/api/course/coures.js'
import FileUp from "@/components/file/FileUp.vue";
const route=useRoute();
const showView=ref(0);
const dialogLessonFormVisible=ref(false);
const dialogQuestionVisible=ref(false);
const dialogCourseOutlineVisible=ref(false);
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
      if (res.data.code===0){
        lessonDetail.value.lessons=res.data.data;
      }else {
        ElMessage(res.description);
      }
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
const changeCourseInfo=()=>{
  ElMessageBox.prompt('请输入新的课程简介', '修改课程简介', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(({ value }) => {
    updateCourse(route.params.id,value).then(res=>{
      ElMessage(res.description);
    }).catch(err=>{
      ElMessage(err);
    })
  }).catch(() => {
    ElMessage({
      type: 'info',
      message: '取消修改'
    });
  });
}
const removeCourse=()=>{
  ElMessageBox.confirm('你是否确认删除课程？', '删除请求确认', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteCourse(route.params.id)
      .then(res => {
        if (res.data.code === 0) {
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
const getStudents=()=>{
  getAllStudents(route.params.id)
    .then(res=>{
      if (res.data.code===0){
        courseDetail.value.students=res.data.data;
      }else {
        ElMessage(res.description);
      }
    })
    .catch(err=>{ElMessage(err);})
}
const getLessonQuestion=(lessonId)=>{
  getLessonQuestions(lessonId)
      .then(res=>{
        console.log(res);
        lessonDetail.value.lessonQuestions=res;
        dialogQuestionVisible.value=true;
      }).catch(err=>{{
        ElMessage(err);
  }})
}
const createLessonQuestion=(lessonId)=>{
  createLessonQuestions(lessonId)
      .then(res=>{
        lessonDetail.value.lessonQuestions=res.data;
        ElMessage(res.data);
        dialogQuestionVisible.value=true;
      }).catch(err=>{{
    ElMessage(err);
  }})
}

onMounted(()=>{
  getLesson();
  getCourseByID();
  getStudents();
})
</script>

<template>
  <el-container class="class-container">
    <el-header class="class-header">
      <el-button type="info" @click="showView=0">课程信息</el-button>
      <el-button type="primary" @click="showView=1">课时管理</el-button>
      <el-button type="success" @click="showView=2">学生管理</el-button>
      <el-button type="danger" @click="removeCourse">删除课程</el-button>
      <el-button type="warning" @click="dialogQuestionVisible=true">测试</el-button>
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
          <el-button type="primary" @click="changeCourseInfo">修改课程简介</el-button>
          <el-button type="warning" @click="">查看课程大纲</el-button>
          <el-button type="success" @click="dialogCourseOutlineVisible=true">创建课程大纲</el-button>
        </template>
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
              <el-button v-if="haveLessonQuestion(scope.row.lessonId)===1" size="default" @click="getLessonQuestion(scope.row.lessonId)">查看测试</el-button>
              <el-button v-if="haveLessonQuestion(scope.row.lessonId)===0" size="default" @click="createLessonQuestion(scope.row.lessonId)">创建测试</el-button>
              <el-button v-if="haveLessonQuestion(scope.row.lessonId)===1" size="default" @click="">删除测试</el-button>
              <el-button v-if="haveLessonQuestion(scope.row.lessonId)===1" size="default" type="danger" @click="">查看测试完成情况</el-button>
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
        <el-table :data="courseDetail.students" border style="width: 100%">
          <el-table-column type="selection" width="55" />
          <el-table-column property="id" label="ID" v-if="false"></el-table-column>
          <el-table-column property="username" label="学生姓名" width="120"></el-table-column>
          <el-table-column property="gender" label="学生性别" width="120"></el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button size="small" @click="">编辑</el-button>
              <el-button size="small" type="danger" @click="">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
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
      </template>
    </el-card>
    <el-button type="success">上传课时测试</el-button>
  </el-dialog>
  <el-dialog v-model="dialogCourseOutlineVisible" title="创建课程大纲">
    <FileUp/>
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
