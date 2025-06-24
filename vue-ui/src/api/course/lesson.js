import request from '@/utils/request.js'
export function getLessons(courseId) {
  return request.get('/api/lesson/list',{
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
