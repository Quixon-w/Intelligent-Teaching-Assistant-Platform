import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// 创建axios实例
const service = axios.create({
  // baseURL: 'http://localhost:8080', // 后端服务地址
  timeout: 10000,
  withCredentials: true
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 可以在这里添加token等认证信息
    const token = sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    console.log('原始响应:', response);
    const res = response.data
    
    // 检查响应数据是否存在
    if (!res) {
      console.error('响应数据为空');
      return Promise.reject(new Error('响应数据为空'));
    }
    
    console.log('响应数据:', res);
    
    // 根据后端返回的状态码判断请求是否成功
    if (res.code === 0) {
      return res
    } else {
      const errorMessage = res.description || res.message || '请求失败';
      console.error('业务错误:', errorMessage, 'code:', res.code);
      
      // 对于业务错误，抛出包含详细信息的错误
      const error = new Error(errorMessage);
      error.code = res.code;
      error.response = res;
      return Promise.reject(error);
    }
  },
  error => {
    console.error('网络错误:', error);
    
    // 处理常见的HTTP错误
    let message = '网络请求失败';
    if (error.response) {
      const status = error.response.status;
      switch (status) {
        case 401:
          message = '未授权，请重新登录';
          // 可以在这里清除token并跳转到登录页
          break;
        case 403:
          message = '权限不足';
          break;
        case 404:
          message = '请求的资源不存在';
          break;
        case 500:
          message = '服务器内部错误';
          break;
        default:
          message = `请求失败 (${status})`;
      }
    } else if (error.request) {
      message = '网络连接失败，请检查网络';
    }
    
    error.message = message;
    return Promise.reject(error);
  }
)

export default service
