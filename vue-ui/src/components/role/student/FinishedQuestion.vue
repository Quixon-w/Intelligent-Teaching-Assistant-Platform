<script setup>
import {onMounted, ref} from "vue";
import {useRoute} from "vue-router";
import {getLessonRecords, getLessonQuestionsList} from "@/api/course/lesson.js";
import UserRoleMap from "@/utils/userrole.js";
const route = useRoute();
const finishedQuestions = ref([]);
const getData = async () => {
  try {
    const studentId = sessionStorage.getItem('userId')
    
    // 获取测试记录
    const recordsRes = await getLessonRecords(route.params.lessonId, studentId)
    
    if (recordsRes.code === 0 && recordsRes.data) {
      // 获取题目详情
      const questionsRes = await getLessonQuestionsList(route.params.lessonId)
      
      if (questionsRes.code === 0 && questionsRes.data) {
        // 将记录和题目详情合并
        const mergedRecords = recordsRes.data.map(record => {
          const question = questionsRes.data.find(q => q.questionId === record.questionId)
          return {
            ...record,
            questions: question || null
          }
        })
        
        finishedQuestions.value = mergedRecords
      } else {
        finishedQuestions.value = recordsRes.data
      }
    } else {
      finishedQuestions.value = []
    }
  } catch (e) {
    console.log(e)
    finishedQuestions.value = []
  }
}
onMounted(()=>{
  getData();
})
</script>

<template>
  <el-table :data="finishedQuestions" border style="width: 100%">
    <el-table-column prop="id" v-if="false"></el-table-column>
    <el-table-column label="问题ID" prop="questionId"></el-table-column>
    <el-table-column label="问题内容" prop="questions.question"></el-table-column>
    <el-table-column label="知识范围" prop="questions.knowledge"></el-table-column>
    <el-table-column label="问题选项A" prop="questions.options.A"></el-table-column>
    <el-table-column label="问题选项B" prop="questions.options.B"></el-table-column>
    <el-table-column label="问题选项C" prop="questions.options.C"></el-table-column>
    <el-table-column label="问题选项D" prop="questions.options.D"></el-table-column>
    <el-table-column label="正确答案" prop="questions.answer"></el-table-column>
    <el-table-column label="解析" prop="questions.explanation"></el-table-column>
    <el-table-column label="你的回答" prop="selectedOption"></el-table-column>
    <el-table-column label="提交时间" prop="submitTime"></el-table-column>
  </el-table>
</template>

<style scoped>

</style>
