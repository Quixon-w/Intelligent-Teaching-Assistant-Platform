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
    console.log(courseId,lessonId);

    // 发起 HTTP 请求到后端 API 端点
    return request.get(`/api/files/download/${courseId}`, { responseType: 'blob' })
        .then(response => {
            // 创建临时链接并触发下载
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', '工作日志_吴佳昊.pdf'); // 设置下载文件名
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        })
        .catch(error => {
            console.error('Error downloading file:', error);
        });
}
