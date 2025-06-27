import request from '@/utils/request.js'
export function getLessons(courseId) {
  return request.get('/api/lesson/list',{
    params :{
      courseId:courseId
    },
  })
    .then(res =>{
      return res;
    })
    .catch(err =>{
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