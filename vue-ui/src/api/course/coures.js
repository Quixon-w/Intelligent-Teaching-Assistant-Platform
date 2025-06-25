import request from '@/utils/request.js'
export function getCourses(pageNum,pageSize,courseName,teacherName){
  console.log(pageNum,pageSize,courseName,teacherName)
  return request.get('/api/course/listPage',{
    params:{
      "pageNum":pageNum,
      "pageSize":pageSize,
      "courseName":courseName,
      "teacherName":teacherName
    },
  }).then(res=>{
    console.log(res);
    return res;
  }).catch(err=>{
    console.log(err);
    return err;
  })
}
export function deleteCourse(courseId){
  return request.post('/api/course/delete',null,{
    params:{
      courseId:courseId
    }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
export function findCourseByID(courseId){
  return request.get('/api/course/findOne',{
    params:{
      courseId:courseId
    }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
export function updateCourse(courseId,comment){
  return request.post('/api/course/edit',null,{
    params:{
      courseId:courseId,
      comment:comment
    }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
export function getAllStudents(courseId){
  return request.get('/api/enroll/list/course',{
    params:{
      courseId:courseId
    }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
export function getLessonQuestions(lessonId){
  return request.get('/api/map/list',{
    params:{
      lessonId:lessonId
    }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}

export const enrollCourse = (courseId) => {
  return request.get('/api/enroll', {
    params: {
      courseId:courseId }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}

export const dismissCourse = (studentId,courseId) => {
  return request.get('/api/enroll/dismiss', {
    params: {
      studentId:studentId,
      courseId:courseId}
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
