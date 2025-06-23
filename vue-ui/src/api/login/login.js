import request from '@/utils/request.js'
export function login(username, password) {
  return request.post('/user/login', {
        "userAccount": username,
        "userPassword": password,
  },{
  }).then(res => {
    console.log(res);
    return res;
  }).catch(err => {
    return err;
  });
}
