import request from "@/utils/request.js";
const userId = sessionStorage.getItem('userId');
const role = sessionStorage.getItem('role');
export function previewFile(courseId,lessonId) {
  console.log(courseId,lessonId);
  // TODO: Replace with actual backend API endpoint
  return request.get('/ai/v1/create/outline/status',{
      params:{
      user_id : sessionStorage.getItem('userId'),
      course_id : courseId,
      lesson_num : lessonId,
      is_teacher: sessionStorage.getItem('role')=='teacher',
  },}).then(res=>{
      return res;
  }).catch(err=>{
      return err;
  });
}
export function downloadFile(courseId,lessonId){
    const link = document.createElement('a')
    link.href = '/ai/v1/download/outline/'+userId+'/'+courseId+'/'+lessonId+'/outline_20250628_162728.docx'
    link.download = 'filename.pdf' // 设置下载文件名
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    // 发起 HTTP 请求到后端 API 端点
}
