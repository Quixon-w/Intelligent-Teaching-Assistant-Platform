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
        return res.data.sessions;
    }).catch(err=>{
        console.log(err);
        return null;
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
        if (res.data.context_messages.length===0){
            return null;
        }else{
            return res.data.context_messages;
        }
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
    return request.delete("/ai/v1/users/"+userId+"/sessions/"+sessionId+"/history",{
        user_id: userId,
        session_id: sessionId,
        is_teacher: isTeacher,
    }).then(res=>{
        return res;
    }).catch(err=>{
        return err;
    })
}
export function createLessonOutline(courseId,lessonId){
    return request.post('/ai/v1/create/outline',{
        user_id: userId,
        session_id: "testtest",
        course_id: courseId,
        lesson_num: lessonId,
        is_teacher: isTeacher,
    }).then(res=>{
        return res;
    }).catch(err=>{
        return err;
    })
}
export function lessonOutlineStatus(courseId,lessonId){
    return request.get('/ai/v1/create/outline/status',{
        params:{
            user_id: userId,
            course_id: courseId,
            lesson_num: lessonId,
            is_teacher: isTeacher,
        },
    }).then(res=>{
        return res.data.has_outline;
    }).catch(err=>{
        return err;
    })
}
export function lessonOutlineDownload(courseId,lessonId){
    return request.get("/ai/v1/list/outlines/"+userId+"/"+courseId+"/"+lessonId).then(res=>{
        let files=res.data.files;
        let urls=[];
        for(let file of files){
            urls.push(file.download_url);
        }
        return urls;
    }).catch(err=>{
        return err;
    })
}
export function askUploadFile(sessionId,query){
    return fetch('/ai//v1/qa',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "query": query,
            "user_id": userId,
            "session_id": sessionId,
            "is_teacher": isTeacher,
            "search_mode": "uploaded",
        })
    })
}
