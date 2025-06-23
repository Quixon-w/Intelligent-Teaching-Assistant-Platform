import request from '@/utils/request.js'
export function getCourses(pageNum,pageSize,courseName,teacherName){
  console.log(pageNum,pageSize,courseName,teacherName)
  return request.get('course/listPage',{
    params:{
      "pageNum":pageNum,
      "pageSize":pageSize,
      "courseName":courseName,
      "teacherName":teacherName
    }
  }).then(res=>{
    console.log(res);
    return res;
  }).catch(err=>{
    console.log(err);
    return err;
  })
}
