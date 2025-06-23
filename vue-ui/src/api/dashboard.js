import request from '@/utils/request.js'
export function onExit(){
  return request.post('http://192.168.240.226:8080/user/logout')
    .then(res =>{
      return res;
    })
    .catch(err =>{
      return err;
    })
}
