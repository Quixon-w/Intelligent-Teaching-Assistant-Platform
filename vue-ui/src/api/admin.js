import request from '@/utils/request.js'

// 获取用户列表（分页）
export function getUsersList(pageNum, pageSize, username = '', userAccount = '') {
  const params = {
    pageNum: pageNum,
    pageSize: pageSize
  }
  
  // 只有当搜索条件不为空时才添加到参数中
  if (username) {
    params.username = username
  }
  if (userAccount) {
    params.userAccount = userAccount
  }
  
  console.log('API调用参数:', params)
  
  return request.get('/api/user/searchPage', { params })
}

// 获取已封禁用户列表
export function getDeletedUsers() {
  console.log('调用获取已封禁用户API: /api/user/listDeleted')
  return request.get('/api/user/listDeleted')
}

// 恢复用户
export function recoverUser(id) {
  return request.post('/api/user/recover', null, {
    params: {
      id: id
    }
  }).then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 删除用户
export function deleteUser(id) {
  return request.post('/api/user/delete', null, {
    params: {
      id: id
    }
  }).then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 重置用户密码
export function resetUserPassword(id) {
  return request.post('/api/user/password', {
    "userId": id,
    "oldPassword": "11111111",
    "newPassword": "12345678",
    "checkPassword": "12345678"
  }).then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 修改用户角色
export function updateUserRole(id, role) {
  return request.post('/api/user/updateRole', null, {
    params: {
      id: id,
      role: role
    }
  }).then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 获取学生数量
export function getStudentNum() {
  return request.get('/api/user/getStudentNum').then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 获取老师数量
export function getTeacherNum() {
  return request.get('/api/user/getTeacherNum').then(res => {
    return res
  }).catch(err => {
    return err
  })
}

// 获取课程数量
export function getCourseNum() {
  return request.get('/api/course/count').then(res => {
    return res
  }).catch(err => {
    return err
  })
} 