import request from '@/utils/request.js'
export function register(username, password, checkpassword, userRole = 0){
  return request.post('/api/user/register',{
      "userAccount": username,
      "userPassword": password,
      "checkPassword": checkpassword,
      "userRole": userRole
  },{
  }).then( res=>{
    return res;
  }).catch(err =>{
    return err;
  })
}
