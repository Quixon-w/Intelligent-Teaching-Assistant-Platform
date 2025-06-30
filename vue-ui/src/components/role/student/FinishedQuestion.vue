<script setup>
import {onMounted, ref} from "vue";
import {useRoute} from "vue-router";
import {lessonQuestionIsFinished} from "@/api/course/lesson.js";
import UserRoleMap from "@/utils/userrole.js";
const route = useRoute();
const finishedQuestions = ref([]);
const getData=()=>{
  lessonQuestionIsFinished(route.params.lessonId,sessionStorage.getItem('userId')).then(res=>{
    finishedQuestions.value=res.data.data;
  }).catch(e=>{
    console.log(e);
  })
}
onMounted(()=>{
  getData();
})
</script>

<template>
  <el-table :data="finishedQuestions" border style="width: 100%">
    <el-table-column prop="id" v-if="false"></el-table-column>
    <el-table-column label="问题ID" prop="questionId"></el-table-column>
    <el-table-column label="选项" prop="selectedOption"></el-table-column>
    <el-table-column label="是否正确" prop="isCorrect" :formatter="(row, column, cellValue) => cellValue?'是':'否'"></el-table-column>
    <el-table-column label="提交时间" prop="submitTime"></el-table-column>
  </el-table>
</template>

<style scoped>

</style>
