import request from '@/utils/request.js'
export function getCourses(pageNum,pageSize,courseName,teacherName){
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
export function getCoursesOfStu(studentId){
  console.log(studentId)
  return request.get('/api/enroll/list/student',{
    params:{
      "studentId":studentId,
    },
  }).then(res=>{
    console.log(res);
    return res;
  }).catch(err=>{
    console.log(err);
    return err;
  })
}
export function addCourse(courseName,courseDescription){
  return request.post('/api/course/add',null,{
    params:{
      courseName:courseName,
      comment:courseDescription,
    }
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
  }).then( res => {
    let data = [];
    for (let student of res.data.data) {
      getCourseScore(courseId,student.id).then(res=>{
        student.score=res;
      }).catch(err=>{
        console.log(err);
      });
      data.push(student);
    }
    return data;
  }).catch(err=>{
    return err;
  })
}

export function endCourses(courseId){
  return request.post('/api/course/over',null,{
    params:{
      courseId:courseId
    }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}
export const enrollCourse = (courseId) => {
  return request.post('/api/enroll',null, {
    params: {
      courseId:courseId }
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}

export const dismissCourse = (studentId,courseId) => {
  return request.post('/api/enroll/dismiss',null, {
    params: {
      studentId:studentId,
      courseId:courseId}
  }).then(res=>{
    return res;
  }).catch(err=>{
    return err;
  })
}

export const isMyCourse=(studentId,courseId)=>{
  return request.get('/api/enroll/list/student', {
    params: {
      studentId:studentId}
  }).then(res=>{
    if (res.code === 0 && res.data) {
      for(let i=0;i<res.data.length;i++){
        if(res.data[i].course.id==courseId){
          return true;
        }
      }
    }
    return false;
  }).catch(err=>{
    return err;
  })
}
export const scoreTrend = (courseId,studentId) => {
  return request.get('/api/course/scoreList', {
    params: {
      courseId:courseId,
      studentId:studentId}
  }).then(res=>{
    return res.data;
  }).catch(err=>{
    return err;
  })
}
export function getCourseScore(courseId,studentId){
  return request.get('/api/course/score',{
    params:{
      courseId:courseId,
      studentId:studentId
    }
  }).then(res=>{
    return res.data.data;
  }).catch(err=>{
    return err;
  })
}
export function getHotCourses(){
  return request.get('/api/enroll/list/hot',null).then(res=>{
    console.log(res);
    return res.data.data;
  }).catch(err=>{
      return err;
  })
}
