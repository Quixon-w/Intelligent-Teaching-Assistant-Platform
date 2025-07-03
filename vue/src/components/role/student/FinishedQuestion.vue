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
    for(let i=0;i<finishedQuestions.value.length;i++){
      finishedQuestions.value[i].questions.options=JSON.parse(finishedQuestions.value[i].questions.options);
    }
    /*finishedQuestions.value=res.data.data;*/
    console.log(finishedQuestions.value);
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
    <el-table-column prop="questionRecords.id" v-if="false"></el-table-column>
    <el-table-column label="问题ID" prop="questions.questionId"></el-table-column>
    <el-table-column label="问题内容" prop="questions.question"></el-table-column>
    <el-table-column label="知识范围" prop="questions.knowledge"></el-table-column>
    <el-table-column label="问题选项A" prop="questions.options.A"></el-table-column>
    <el-table-column label="问题选项B" prop="questions.options.B"></el-table-column>
    <el-table-column label="问题选项C" prop="questions.options.C"></el-table-column>
    <el-table-column label="问题选项D" prop="questions.options.D"></el-table-column>
    <el-table-column label="正确答案" prop="questions.answer"></el-table-column>
    <el-table-column label="解析" prop="questions.explanation"></el-table-column>
    <el-table-column label="你的回答" prop="questionRecords.selectedOption"></el-table-column>
    <el-table-column label="提交时间" prop="questionRecords.submitTime"></el-table-column>
  </el-table>
</template>

<style scoped>

</style>
