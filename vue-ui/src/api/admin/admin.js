import request from "@/utils/request.js";

export function getUsersList(pageNum,pageSize,username){
    return request.get('/api/user/searchPage',{
      params:{
        "pageNum":pageNum,
        "pageSize":pageSize,
        "username":username
      },
    }).then(res=>{
      return res;
    }).catch(err=>{
      return err;
    })
}
export function getDeletedUsers(){
    return request.get('/api/user/listDeleted').then(res=>{
      return res.data.data;
    }).catch(err=>{
      return err;
    })
}
export function recoverUser(id){
    return request.post('/api/user/recover',null,{
      params:{
        id:id
      }
    }).then(res=>{
      return res;
    }).catch(err=>{
      return err;
    })
}
