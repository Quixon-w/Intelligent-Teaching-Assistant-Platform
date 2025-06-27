import request from "@/utils/request.js";
const userId=sessionStorage.getItem('userId');
const isTeacher=sessionStorage.getItem('role')=='teacher';
export function getAllSessions(){
    return request.get("/ai/v1/users/"+userId+"/sessions",{
        params:{
            user_id:userId,
            is_teacher:isTeacher
        }
    }).then(res=>{
        return res.sessions;
    }).catch(err=>{
        return err;
    })
}
export function getSession(sessionId){
    return request.get("/ai/v1/users/"+userId+"/sessions/"+sessionId+"/context",{
        params:{
            user_id:userId,
            session_id:sessionId,
            is_teacher:isTeacher
        }
    }).then(res=>{
        return res;
    }).catch(err=>{
        return err;
    })
}
export function chat(sessionId,message){
    return fetch('/ai/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            messages: message,
            user_id: userId,
            session_id: sessionId,
            is_teacher: isTeacher,
            stream: false
        })
    })
}
export function clearChat(sessionId){
    return request.delete("/ai/v1/users/"+userId+"/sessions/"+sessionID+"/dialogues",{
        user_id: userId,
        session_id: sessionId,
        is_teacher: isTeacher,
    }).then(res=>{
        return res;
    }).catch(err=>{
        return err;
    })
}
