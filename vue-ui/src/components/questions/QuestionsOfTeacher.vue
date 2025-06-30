<script setup>
import {onMounted, ref} from "vue";
import {
  addOneQuestion,
  addTeachersQuestion,
  getTeacherQuestions,
  saveChangedQuestion,
  searchFatherQuestion
} from "@/api/course/lesson.js";
const props = defineProps({
  action: {
  },
  lessonId: {
  }
})
const questions = ref([]);
const questionKnowledge=ref("");
const teacherId=sessionStorage.getItem("userId");
const currentquestion=ref({
  questionId:questions.value.length+1,
  questionKonwledge:"",
  questionContent:"",
  questionExplanation:"",
  questionAnswer:["","","","",""],
});
const dialogCreateVisible=ref(false);
const dialogChangeVisible=ref(false);
const getData=()=>{
  getTeacherQuestions(teacherId).then(res=>{
    questions.value=res;
  }).catch(err=>{
    console.log(err);
  })
}
const addQuestion=(questionId)=>{
  addOneQuestion(props.lessonId,questionId).then(res=>{
    console.log(res);
  }).catch(err=>{
    console.log(err);
  })
}
const createQuestion=()=>{
  addTeachersQuestion(currentquestion.value).then(res=>{
    console.log(res);
  }).catch(err=>{
    console.log(err);
  })
  getData();
  dialogCreateVisible.value=false;
}
const changeQuestion=(question)=>{
  currentquestion.value=question;
  dialogChangeVisible.value=true;
}
const saveChange=()=>{
  saveChangedQuestion(currentquestion.value).then(res=>{
    console.log(res);
  }).catch(err=>{
    console.log(err);
  });
  getData();
  dialogChangeVisible.value=false;
}
const searchQuestion=()=>{
  searchFatherQuestion(questionKnowledge.value).then(res=>{
    questions.value=res;
    console.log(res);
  }).catch(err=>{
    console.log(err);
  });
}
onMounted(()=>{
  getData();
})
</script>
<template>
  <el-form v-if="props.action!=='add'" style="display: flex;justify-content: space-between;gap: 2px">
    <el-form-item label="题目知识域">
      <el-input v-model="questionKnowledge" style="max-width: 600px"></el-input>
    </el-form-item>
    <el-button type="success" @click="searchQuestion">搜索题库</el-button>
    <el-button type="success" @click="dialogCreateVisible=true">新建题库</el-button>
  </el-form>
  <el-card v-for="question in questions">
    <template #header>
      <el-text>第{{ question.questionId }}题</el-text>
      <el-text>{{ question.questionKonwledge }}</el-text>
      <el-button type="primary" v-if="props.action==='add'" @click="addQuestion(question.questionId)">添加</el-button>
      <el-button type="success" @click="changeQuestion(question)" v-if="props.action!=='add'">修改题库</el-button>
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

  <el-dialog v-model="dialogCreateVisible" title="新建题库">
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
      <el-button type="primary" @click="createQuestion">保存</el-button>
    </el-form>
  </el-dialog>

  <el-dialog v-model="dialogChangeVisible" title="修改题库">
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
</template>

<style scoped>

</style>
