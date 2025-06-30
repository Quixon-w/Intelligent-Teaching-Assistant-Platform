import request from '@/utils/request.js'
import {lessonOutlineDownload, lessonOutlineStatus} from "@/api/ai/ai.js";
import qs from "qs";
export function getLessons(courseId) {
  return request.get('/api/lesson/list',{
    params :{
      courseId:courseId
    },
  }).then(res =>{
    let lessons=res.data.data;
    for(let lesson of lessons){
      lessonOutlineStatus(courseId,lesson.lessonId).then(res=>{
        lesson.outlineStatus=res;
      }).catch(err=>{
        console.log(err);
      });
      lessonOutlineDownload(courseId,lesson.lessonId).then(res=>{
        lesson.outlineDownload=res;
      }).catch(err=>{
        console.log(err);
      });
      if(sessionStorage.getItem('role')==='student'){
        lessonQuestionIsFinished(lesson.lessonId,sessionStorage.getItem('userId')).then(res=>{
          lesson.isQuestionFinished = res.data.data !== null;
        }).catch(err=>{
          console.log(err);
        })
      }
    }
    console.log(lessons);
    return lessons;
  }).catch(err =>{
    return err;
  })
}
export function addLesson(courseId,lessonName){
  return request.post('/api/lesson/add',null,{
    params:{
      courseId:courseId,
      lessonName:lessonName,
    }
  }).then(res =>{
    console.log(res);
    return res;
  }).catch(err =>{
    return err;
  })
}
export function getLessonQuestions(lessonId){
  return request.get('/api/map/list',{
    params:{
      lessonId:lessonId
    }
  }).then(res=>{
    console.log(res);
    let data=[];
    for(let adata of res.data.data){
      let options=JSON.parse(adata.options);
      let aadata={
        questionId:adata.questionId,
        questionKonwledge:adata.knowledge,
        questionContent:adata.question,
        questionExplanation:adata.explanation,
        questionAnswer:[adata.answer,options.A,options.B,options.C,options.D],
      }
      data.push(aadata);
    }
    console.log(data);
    return data;
  }).catch(err=>{
    return err;
  })
}
export function getLessonCommittedQuestions(lessonId){
  return request.get('/api/map/listCommitted',{
    params:{
      lessonId:lessonId
    }
  }).then(res=>{
    console.log(res);
    let data=[];
    for(let adata of res.data.data){
      let options=JSON.parse(adata.options);
      let aadata={
        questionId:adata.questionId,
        questionKonwledge:adata.knowledge,
        questionContent:adata.question,
        questionExplanation:adata.explanation,
        questionAnswer:[null,'A、  '+options.A,'B、  '+options.B,'C、  '+options.C,'D、  '+options.D],
      }
      data.push(aadata);
    }
    console.log(data);
    return data;
  }).catch(err=>{
    return err;
  })
}
export function getLessonScores(lessonId) {
  return request.get('/api/lesson/getListScores',{
    params :{
      lessonId:lessonId
    },
  })
      .then(res =>{
        return res.data;
      })
      .catch(err =>{
        return err;
      })
}
export function saveQuestions(questions,lessonID){
  let tempQuestions=[];
  for(let question of questions){
    tempQuestions.push({
      "teacherId": sessionStorage.getItem("userId"),
      "knowledge": question.questionKonwledge,
      "question": question.questionContent,
      "options": {
        "A":question.questionAnswer[1],
        "B":question.questionAnswer[2],
        "C":question.questionAnswer[3],
        "D":question.questionAnswer[4]},
      "answer": question.questionAnswer[0],
      "explanation": question.questionExplanation,
    })
  }
  return request.post('/api/map/addByEntity', tempQuestions,{
    params:{
      lessonId:lessonID
    }
  }).then(res=>{
    console.log(res);
    return res;
  }).catch(err=>{
    return err;
  })
}
export function saveNewQuestion(question,lessonID){
  return request.post('/api/map/addByEntities', [{
    "teacherId": sessionStorage.getItem("userId"),
    "knowledge": question.questionKonwledge,
    "question": question.questionContent,
    "options": {
      "A":question.questionAnswer[1],
      "B":question.questionAnswer[2],
      "C":question.questionAnswer[3],
      "D":question.questionAnswer[4]},
    "answer": question.questionAnswer[0],
    "explanation": question.questionExplanation,
  }],{
    params:{
      lessonId:lessonID
    }
  }).then(res=>{
    console.log(res);
    return res;
  }).catch(err=>{
    return err;
  });
}
export function commitQuestion(questions,lessonID){
  let ids=[];
  for(let question of questions){
    ids.push(question.questionId);
  }
  console.log(ids)
  return request.post('/api/map/commit',null,{
    params:{
      lessonId:lessonID,
      questionIds:ids,
    },
    paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' })
  }).then(res=>{
      return res;
  }).catch(err =>{
      return err;
  })
}
export function deleteQuestion(lessonId,questionId){
  return request.post('/api/map/delete',null,{
    params:{
      lessonId:lessonId,
      questionId:questionId
    }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
export function getTeacherQuestions(teaccherId){
  return request.get('/api/question/listByTeacherId',{
    params:{
      teacherId:teaccherId
    }
  }).then(res=>{
    let data=[];
    for(let adata of res.data.data){
      let options=JSON.parse(adata.options);
      let aadata={
        questionId:adata.questionId,
        questionKonwledge:adata.knowledge,
        questionContent:adata.question,
        questionExplanation:adata.explanation,
        questionAnswer:[adata.answer,options.A,options.B,options.C,options.D],
      }
      data.push(aadata);
    }
    return data;
  }).catch(err=>{
      return err;
  })
}
export function addOneQuestion(lessonId,questionId){
  return request.post('/api/map/addByIds',null,{
    params:{
      lessonId:lessonId,
      questionIds:questionId
    }
  }).then(res=>{
      return res;
  }).catch(err=>{
     return err;
  })
}
export function saveChangedQuestion(question){
  return request.post('/api/map/update',{
    questionId:question.questionId,
    teacherId:sessionStorage.getItem("userId"),
    knowledge:question.questionKonwledge,
    question:question.questionContent,
    options:{
      "A":question.questionAnswer[1],
      "B":question.questionAnswer[2],
      "C":question.questionAnswer[3],
      "D":question.questionAnswer[4]},
    answer:question.questionAnswer[0],
    explanation:question.questionExplanation
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
export function addTeachersQuestion(question){
  return request.post('/api/question/addOne',{
    teacherId:sessionStorage.getItem("userId"),
    knowledge:question.questionKonwledge,
    question:question.questionContent,
    options:{
      "A":question.questionAnswer[1],
      "B":question.questionAnswer[2],
      "C":question.questionAnswer[3],
      "D":question.questionAnswer[4]},
    answer:question.questionAnswer[0],
    explanation:question.questionExplanation
  }).then(res=>{
      return res;
  }).catch(err=>{
      return err;
  })
}
export function searchFatherQuestion(questionKnowledge){
  return request.get('/api/question/selectByFather',{
    params:{
      father:questionKnowledge,
      teacherId:sessionStorage.getItem("userId")
    }
   }).then(res=>{
    let data=[];
    for(let adata of res.data.data){
      let options=JSON.parse(adata.options);
      let aadata={
        questionId:adata.questionId,
        questionKonwledge:adata.knowledge,
        questionContent:adata.question,
        questionExplanation:adata.explanation,
        questionAnswer:[adata.answer,options.A,options.B,options.C,options.D],
      }
      data.push(aadata);
    }
    return data;
  }).catch(err=>{
    return err;
  })
}
export function commitQuestionHistory(questions,lessonId){
  let questionAnswers=[];
  for(let question of questions){
    questionAnswers.push(question.questionAnswer[0]);
  }
  console.log(questionAnswers);
  return request.post('/api/records/add',null,{
    params:{
      lessonId:lessonId,
      answers:questionAnswers,
    },
    paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' })
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
export function lessonQuestionIsFinished(lessonId,studentId){
  return request.get('/api/records/getRecords',{
    params:{
      lessonId:lessonId,
      studentId:studentId
    }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
