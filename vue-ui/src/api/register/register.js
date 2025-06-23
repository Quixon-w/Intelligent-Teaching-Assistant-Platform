import request from '@/utils/request.js'
export function register(username,password,checkpassword){
  return request.post('/user/register',{
      "userAccount":username,
      "userPassword":password,
      "checkPassword":checkpassword,
  }).then( res=>{
    return res;
  }).catch(err =>{
    return err;
  })
}
