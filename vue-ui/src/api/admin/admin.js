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
