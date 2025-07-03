<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import {
  commitQuestion,
  deleteQuestion,
  getLessonQuestions,
  saveNewQuestion,
  saveQuestions
} from "@/api/course/lesson.js";
import {ElMessage} from "element-plus";
import QuestionsOfTeacher from "@/components/questions/QuestionsOfTeacher.vue";

const route = useRoute();
const questions = ref([]);
const currentquestion = ref({});
const dialogChangeQuestionVisible = ref(false);
const dialogCreateQuestionVisible = ref(false);
const dialogAddQuestionOfMine=ref(false);
const getQuestions = (lessonId) => {
  getLessonQuestions(lessonId).then(res => {
    console.log(res);
    questions.value = res;
  }).catch(err => {{
    console.log(err);
  }})
}
const createQuestion=()=>{
  currentquestion.value={
    questionId:questions.value.length+1,
    questionKonwledge:"",
    questionContent:"",
    questionExplanation:"",
    questionAnswer:["","","","",""],
  };
  dialogCreateQuestionVisible.value=true;
}
const saveQuestion=()=>{
  saveNewQuestion(currentquestion.value,route.params.lessonId).then(res=>{
    console.log(res);
    getQuestions(route.params.lessonId)
    dialogCreateQuestionVisible.value=false;
  }).catch(err=>{
    console.log(err);
  })
  //questions.value.push(currentquestion.value);
}
const removeQuestion=(questionId)=>{
  deleteQuestion(route.params.lessonId,questionId).then(res=>{
    getQuestions(route.params.lessonId)
    console.log(res);
  }).catch(err=>{
    console.log(err);
  })
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
const saveChange=()=>{
  for(let i=0;i<questions.value.length;i++){
    if(questions.value[i].questionId===currentquestion.value.questionId){
      questions.value[i] = currentquestion.value;
    }
  }
  dialogChangeQuestionVisible.value=false;
}
const save=()=>{
  saveQuestions(questions.value,route.params.lessonId).then(res=>{
    console.log(res);
  }).catch(err=>{
    console.log(err);
  })
}
const commitQuestions=()=>{
  commitQuestion(questions.value,route.params.lessonId).then(res=>{
    console.log(res);
  }).catch(err=>{
    console.log(err);
  })
}
const addQuestionOfMine=()=>{
  dialogAddQuestionOfMine.value=true;
}
const aiCreateQuestions=()=>{
}
onMounted(() => {
  getQuestions(route.params.lessonId)
})
</script>

<template>
  <el-button type="success" @click="aiCreateQuestions">生成测试</el-button>
  <el-button type="primary" @click="createQuestion">新建题目</el-button>
  <el-button type="primary" @click="addQuestionOfMine">从题库添加</el-button>
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
        <el-radio-button value="A" size="large" border>A、{{ question.questionAnswer[1] }}</el-radio-button>
        <el-radio-button value="B" size="large" border>B、{{ question.questionAnswer[2] }}</el-radio-button>
        <el-radio-button value="C" size="large" border>C、{{ question.questionAnswer[3] }}</el-radio-button>
        <el-radio-button value="D" size="large" border>D、{{ question.questionAnswer[4] }}</el-radio-button>
      </el-radio-group>
    </template>
  </el-card>
  <el-button type="primary" @click="commitQuestions">上传测试</el-button>

  <el-dialog v-model="dialogChangeQuestionVisible" title="修改题目">
    <el-form v-model="currentquestion">
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
        <span>A、</span><el-input v-model="currentquestion.questionAnswer[1]"></el-input>
        <span>B、</span><el-input v-model="currentquestion.questionAnswer[2]"></el-input>
        <span>C、</span><el-input v-model="currentquestion.questionAnswer[3]"></el-input>
        <span>D、</span><el-input v-model="currentquestion.questionAnswer[4]"></el-input>
      </el-form-item>
      <el-form-item label="题目答案">
        <el-select
            v-model="currentquestion.questionAnswer[0]"
            placeholder="Select"
            size="large"
            style="width: 240px"
        >
          <el-option
              key="A"
              label="A"
              value="A"
          />
          <el-option
              key="B"
              label="B"
              value="B"
          />
          <el-option
              key="C"
              label="C"
              value="C"
          />
          <el-option
              key="D"
              label="D"
              value="D"
          />
        </el-select>
      </el-form-item>
      <el-button type="primary" @click="saveChange">保存</el-button>
    </el-form>
  </el-dialog>

  <el-dialog v-model="dialogCreateQuestionVisible" title="新建题目">
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
        <span>A、</span><el-input v-model="currentquestion.questionAnswer[1]"></el-input>
        <span>B、</span><el-input v-model="currentquestion.questionAnswer[2]"></el-input>
        <span>C、</span><el-input v-model="currentquestion.questionAnswer[3]"></el-input>
        <span>D、</span><el-input v-model="currentquestion.questionAnswer[4]"></el-input>
      </el-form-item>
      <el-form-item label="题目答案">
        <el-select
            v-model="currentquestion.questionAnswer[0]"
            placeholder="Select"
            size="large"
            style="width: 240px"
        >
          <el-option
              key="A"
              label="A"
              value="A"
          />
          <el-option
              key="B"
              label="B"
              value="B"
          />
          <el-option
              key="C"
              label="C"
              value="C"
          />
          <el-option
              key="D"
              label="D"
              value="D"
          />
        </el-select>
      </el-form-item>
      <el-button type="primary" @click="saveQuestion">保存</el-button>
    </el-form>
  </el-dialog>
  <el-dialog v-model="dialogAddQuestionOfMine" title="从题库中添加">
    <QuestionsOfTeacher :action="'add'" :lessonId=route.params.lessonId />
  </el-dialog>
</template>

<style scoped>

</style>
