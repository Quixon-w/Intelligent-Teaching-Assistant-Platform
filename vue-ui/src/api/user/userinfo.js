import request from '@/utils/request.js';

export function getCurrentUser() {
    return request.get('/api/user/current')
        .then(res => {
            console.log('获取当前用户:', res.data);
            return res.data;
        })
        .catch(err => {
            console.error('获取当前用户失败:', err);
            return err;
        });
}
// 更新用户信息
export function updateUserInfo(id,
                               username,
                               userAccount,
                               avatarUrl,
                               gender,
                               phone,
                               email,
                               userRole) {

    return request.post('/api/user/update', {
        "id":id,
        "username":username,
        "userAccount":userAccount,
        "avatarUrl":avatarUrl,
        "gender":gender,
        "phone":phone,
        "email":email,
        "userRole":userRole,
    })
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
export function changePassword(userId, oldPassword, newPassword, checkPassword) {
  return request.post('/api/user/password',{
      "userId": userId,
      "oldPassword": oldPassword,
      "newPassword": newPassword,
      "checkPassword": checkPassword,
      }
  ).then(res => {
      console.log('密码修改结果:', res.data);
      return res.data;
    })
    .catch(err => {
      console.error('密码修改失败:', err);
      return err;
    });
}

export function deleteUser(userId){
    return request.post('/api/user/delete',null,{
        params:{
            userId:userId
        }
    }).then(res=>{
        return res;
    }).catch(err=>{
        return err;
    })
}
