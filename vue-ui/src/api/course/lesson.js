import request from '@/utils/request.js'
export function getLessons(courseId) {
  return request.get('/lesson/list',{
    params :{
      courseId:courseId
    },
  })
    .then(res =>{
      console.log(res);
      return res;
    })
    .catch(err =>{
      return err;
    })
}
export function addLesson(courseId,lessonName){
  return request.post('/lesson/add',null,{
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
