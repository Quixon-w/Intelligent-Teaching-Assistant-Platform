import os
from fastapi import APIRouter, HTTPException, File, Form, UploadFile, status
from typing import Optional
from utils.knowledge import update_knowledge_db

router = APIRouter()

@router.post("/v1/upload")
async def upload_file(
    file: UploadFile = File(...), 
    session_id: str = Form(...), 
    isTeacher: bool = Form(False),
    courseID: Optional[str] = Form(None),
    lessonNum: Optional[str] = Form(None),
    file_encoding: Optional[str] = Form("utf-8")
):
    """
    上传文件并保存至服务器指定的路径
    :param file: 上传的文件
    :param session_id: 会话 ID，用于创建会话文件夹
    :param isTeacher: 是否为教师，决定存储路径
    :param courseID: 课程ID，教师模式下必填
    :param lessonNum: 课时号，教师模式下必填
    :param file_encoding: 可选，指定文件编码，默认 utf-8
    :return: 返回上传结果消息
    """
    # 验证参数
    if isTeacher and not courseID:
        raise HTTPException(
            status_code=400, 
            detail="教师模式下courseID不能为空"
        )
    
    if isTeacher and courseID and not lessonNum:
        raise HTTPException(
            status_code=400, 
            detail="教师模式下lessonNum不能为空"
        )
    
    # 根据isTeacher决定存储路径
    if isTeacher:
        # 教师模式：存储在Teachers目录下的session_id/courseID/lessonNum文件夹中
        base_folder = "/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers"
        session_folder = f"{base_folder}/{session_id}/{courseID}/{lessonNum}"
    else:
        # 学生模式：存储在Students目录下的session_id文件夹中
        base_folder = "/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Students"
        session_folder = f"{base_folder}/{session_id}"
    
    # 创建目录结构
    os.makedirs(session_folder, exist_ok=True)

    # 保存文件至会话文件夹中
    file_location = f"{session_folder}/{file.filename}"
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # 确认文件是否成功上传并存在
        if os.path.exists(file_location):
            # 更新知识库
            try:
                update_knowledge_db(session_id, isTeacher, courseID, lessonNum)
                knowledge_status = "知识库更新成功"
            except Exception as e:
                knowledge_status = f"知识库更新失败: {str(e)}"
            
            return {
                "message": f"文件已成功上传",
                "isTeacher": isTeacher,
                "courseID": courseID,
                "lessonNum": lessonNum,
                "file_path": file_location,
                "knowledge_status": knowledge_status
            }
        else:
            raise Exception("文件上传失败，目标文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
