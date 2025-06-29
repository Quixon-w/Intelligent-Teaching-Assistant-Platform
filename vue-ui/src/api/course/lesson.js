import request from '@/utils/request.js'
import {lessonOutlineDownload, lessonOutlineStatus} from "@/api/ai/ai.js";
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
      })
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
        questionAnswer:[adata.answer,'A、  '+options.A,'B、  '+options.B,'C、  '+options.C,'D、  '+options.D],
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
export function createLessonQuestions(lessonId){
  return true;
}
