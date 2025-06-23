import request from '@/utils/request.js';

// 获取当前用户的 ID
export function getCurrentUserId() {
    return request.get('/user/current'
    ).then(res => {
        console.log(res.data);
        return res.data;
    }).catch(err => {
        return err;
    });
}

// 根据用户 ID 获取用户详细信息
export function getUserInfoById(userId) {
    return request.post('/user/getUser', {
        params:{
            id: userId
        }
    }).then(res => {
        console.log(res.data);
        return res.data;
    }).catch(err => {
        return err;
    });
}

// 更新用户信息
export function updateUserInfo(userData) {
  return request.post('/user/update', userData)
    .then(res => {
      console.log('更新成功:', res.data);
      return res.data;
    })
    .catch(err => {
      console.error('更新失败:', err);
      return err;
    });
}
// 修改密码
export function changePassword(data) {
  return request.post('/user/password', data)
    .then(res => {
      console.log('密码修改结果:', res.data);
      return res.data;
    })
    .catch(err => {
      console.error('密码修改失败:', err);
      return err;
    });
}


