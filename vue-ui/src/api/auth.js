import request from '@/utils/request.js'

// 用户登录
export function login(username, password) {
  return request.post('/api/user/login', {
    userAccount: username,
    userPassword: password
  }).then(res => {
    console.log('登录响应:', res)
    return res
  }).catch(err => {
    console.error('登录失败:', err)
    return err
  })
}

// 用户注册
export function register(username, password, checkPassword) {
  return request.post('/api/user/register', {
    userAccount: username,
    userPassword: password,
    checkPassword: checkPassword
  }).then(res => {
    console.log('注册响应:', res)
    return res
  }).catch(err => {
    console.error('注册失败:', err)
    return err
  })
}

// 用户登出
export function logout() {
  return request.post('/api/user/logout').then(res => {
    console.log('登出响应:', res)
    return res
  }).catch(err => {
    console.error('登出失败:', err)
    return err
  })
}

// 获取用户信息
export function getUserInfo() {
  return request.get('/api/user/get/login').then(res => {
    console.log('用户信息:', res)
    return res
  }).catch(err => {
    console.error('获取用户信息失败:', err)
    return err
  })
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return request({
    url: '/api/user/current',
    method: 'get'
  })
}

// 修改密码
export const changePassword = (oldPassword, newPassword) => {
  return request({
    url: '/api/user/password',
    method: 'put',
    data: {
      oldPassword,
      newPassword
    }
  })
} 