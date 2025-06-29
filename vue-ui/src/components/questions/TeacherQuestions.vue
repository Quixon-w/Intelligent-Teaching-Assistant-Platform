<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { getLessonQuestions } from "@/api/course/lesson.js";

const route = useRoute();
const questions = ref([]);
const currentquestion = ref({});
const dialogChangeQuestionVisible = ref(false);
const getQuestions = (lessonId) => {
  getLessonQuestions(lessonId).then(res => {
    console.log(res);
    questions.value = res;
  }).catch(err => {{
    console.log(err);
  }})
}
const createQuestion=()=>{

}
const removeQuestion=(questionId)=>{
  for(let i=0;i<questions.value.length;i++){
    if(questions.value[i].questionId===questionId){
      questions.value.splice(i,1);
    }
  }
  console.log(questions.value);
}
const changeQuestion=(questionId)=>{
  for(let i=0;i<questions.value.length;i++){
    if(questions.value[i].questionId===questionId){
      currentquestion.value = questions.value[i];
    }
  }
  console.log(currentquestion.value);
  dialogChangeQuestionVisible.value=true;
}
onMounted(() => {
  getQuestions(route.params.lessonId)
})
</script>

<template>
  <el-button type="success">生成测试</el-button>
  <el-button type="primary">新建题目</el-button>
  <el-button type="primary">保存</el-button>
  <el-card v-for="question in questions">
    <template #header>
      <el-text>第{{ question.questionId }}题</el-text>
      <el-text>{{ question.questionKonwledge }}</el-text>
      <el-button type="primary" @click="changeQuestion(question.questionId)">修改</el-button>
      <el-button type="danger" @click="removeQuestion(question.questionId)">删除</el-button>
    </template>
    <el-text>{{ question.questionContent }}<</el-text>
    <el-text>{{ question.questionExplanation }}</el-text>
    <template #footer>
      <el-radio-group v-model="question.questionAnswer[0]" style="gap: 3px" disabled>
        <el-radio-button value="A" size="large" border>{{ question.questionAnswer[1] }}</el-radio-button>
        <el-radio-button value="B" size="large" border>{{ question.questionAnswer[2] }}</el-radio-button>
        <el-radio-button value="C" size="large" border>{{ question.questionAnswer[3] }}</el-radio-button>
        <el-radio-button value="D" size="large" border>{{ question.questionAnswer[4] }}</el-radio-button>
      </el-radio-group>
    </template>
  </el-card>
  <el-button type="primary">上传测试</el-button>

  <el-dialog v-model="dialogChangeQuestionVisible" title="修改题目">
    <el-form v-model="currentquestion">
      <el-text>第{{ currentquestion.questionId }}题</el-text>
      <el-form-item label="题目知识点">
        <el-input v-model="currentquestion.questionKonwledge"></el-input>
      </el-form-item>
      <el-form-item label="题目内容">
        <el-input v-model="currentquestion.questionContent"></el-input>
      </el-form-item>
      <el-form-item label="题目解析">
        <el-input v-model="currentquestion.questionExplanation"></el-input>
      </el-form-item>
      <el-form-item label="题目选项">
        <el-input v-model="currentquestion.questionAnswer[1]"></el-input>
        <el-input v-model="currentquestion.questionAnswer[2]"></el-input>
        <el-input v-model="currentquestion.questionAnswer[3]"></el-input>
        <el-input v-model="currentquestion.questionAnswer[4]"></el-input>
      </el-form-item>
      <el-form-item label="题目答案">
        <el-input v-model="currentquestion.questionAnswer[0]"></el-input>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<style scoped>

</style>
