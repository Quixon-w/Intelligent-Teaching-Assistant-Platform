<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import {getLessonQuestions} from "@/api/course/lesson.js";

const route = useRoute();
const questions = ref([]);
const getQuestions = (lessonId) => {
  getLessonQuestions(lessonId).then(res => {
    console.log(res);
    questions.value = res;
  }).catch(err => {{
    console.log(err);
  }})
}
onMounted(() => {
  getQuestions(route.params.lessonId)
})
</script>

<template>
  <el-card v-for="question in questions">
    <template #header>
      <el-text>第{{ question.questionId }}题</el-text>
      <el-text>{{ question.questionKonwledge }}</el-text>
    </template>
    <el-text>{{ question.questionContent }}<</el-text>
    <el-text>{{ question.questionExplanation }}</el-text>
    <template #footer>
      <el-radio-group v-model="question.questionAnswer[0]" style="gap: 3px" disabled>
        <el-radio-button value="A" size="large" border>A、{{ question.questionAnswer[1] }}</el-radio-button>
        <el-radio-button value="B" size="large" border>B、{{ question.questionAnswer[2] }}</el-radio-button>
        <el-radio-button value="C" size="large" border>C、{{ question.questionAnswer[3] }}</el-radio-button>
        <el-radio-button value="D" size="large" border>D、{{ question.questionAnswer[4] }}</el-radio-button>
      </el-radio-group>
    </template>
  </el-card>
</template>

<style scoped>

</style>
