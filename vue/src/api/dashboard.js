import request from '@/utils/request.js'
export function onExit(){
  return request.post('/api/user/logout')
    .then(res =>{
      return res;
    })
    .catch(err =>{
      return err;
    })
}
