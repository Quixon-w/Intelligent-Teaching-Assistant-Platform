import request from '@/utils/request.js'
export function getLessons(courseId) {
  return request.get('http://192.168.240.226:8080/lesson/list',{
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
  return request.post('http://192.168.240.226:8080/lesson/add',null,{
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
