import os
from fastapi import APIRouter, HTTPException, File, Form, UploadFile, status
from typing import Optional
from utils.knowledge import update_knowledge_db

router = APIRouter()

@router.post("/v1/upload")
async def upload_file(
    file: UploadFile = File(...), 
    sessionId: str = Form(...),
    userId: str = Form(...),
    isTeacher: bool = Form(False),
    courseId: Optional[str] = Form(None),
    lessonNum: Optional[str] = Form(None),
    fileEncoding: Optional[str] = Form("utf-8"),
    isResource: bool = Form(False),
    isOutline: bool = Form(False),
    isAsk: bool = Form(False)
):
    """
    上传文件并保存至服务器指定的路径
    :param file: 上传的文件
    :param sessionId: 会话 ID，用于会话标识
    :param userId: 用户ID，用于确定存储路径
    :param isTeacher: 是否为教师，决定存储路径
    :param courseId: 课程ID，教师模式下必填（非ask文件时）
    :param lessonNum: 课时号，教师模式下必填（大纲与习题生成参考文件时）
    :param fileEncoding: 可选，指定文件编码，默认 utf-8
    :param isResource: 是否为学习资料
    :param isOutline: 是否为各个课时的大纲与习题生成参考文件
    :param isAsk: 是否为自己上传的可提问文件
    :return: 返回上传结果消息
    """
    # 检查文件类型，只允许pdf和docx
    allowed_extensions = ['.pdf', '.docx']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_extension}。只支持 PDF 和 DOCX 格式"
        )
    
    # 验证参数
    if isTeacher and not isAsk and not courseId:
        raise HTTPException(
            status_code=400, 
            detail="教师模式下非ask文件时courseId不能为空"
        )
    
    if isTeacher and isOutline and not lessonNum:
        raise HTTPException(
            status_code=400, 
            detail="教师模式下大纲与习题生成参考文件时lessonNum不能为空"
        )
    
    # 根据isTeacher和文件类型决定存储路径，使用userId作为主目录
    if isTeacher:
        # 教师模式
        base_folder = "/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge/Teachers"
        if isResource:
            # 学习资料：保存到courseId级别
            session_folder = f"{base_folder}/{userId}/{courseId}"
        elif isOutline:
            # 大纲与习题生成参考文件：保存到lessonNum级别
            session_folder = f"{base_folder}/{userId}/{courseId}/{lessonNum}"
        elif isAsk:
            # 可对文件进行提问的文件：保存在ask文件夹
            session_folder = f"{base_folder}/{userId}/ask"
        else:
            # 默认情况（兼容旧版本）
            session_folder = f"{base_folder}/{userId}/{courseId}/{lessonNum}"
    else:
        # 学生模式：存储在Students目录下的userId文件夹中
        base_folder = "/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge/Students"
        if isAsk:
            # 学生上传的可提问文件：保存在ask文件夹
            session_folder = f"{base_folder}/{userId}/ask"
        else:
            # 其他文件：保存在userId文件夹
            session_folder = f"{base_folder}/{userId}"
    
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
            knowledge_status = "知识库更新成功"
            knowledge_error = None
            try:
                update_knowledge_db(sessionId, isTeacher, courseId, lessonNum)
            except Exception as e:
                knowledge_status = "知识库更新失败"
                knowledge_error = str(e)
            
            # 生成下载URL（仅对学习资料生成）
            download_url = None
            if isResource and isTeacher:
                download_url = f"/v1/download/resource/{userId}/{courseId}/{file.filename}"
            
            response_data = {
                "message": f"文件已成功上传",
                "sessionId": sessionId,
                "userId": userId,
                "isTeacher": isTeacher,
                "courseId": courseId,
                "lessonNum": lessonNum,
                "isResource": isResource,
                "isOutline": isOutline,
                "isAsk": isAsk,
                "filePath": file_location,
                "downloadUrl": download_url,
                "knowledgeStatus": knowledge_status
            }
            
            # 如果知识库更新失败，添加错误信息
            if knowledge_error:
                response_data["knowledgeError"] = knowledge_error
            
            return response_data
        else:
            raise Exception("文件上传失败，目标文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

# 注意：下载相关的路由已移至 routes/download.py
# 包括：
# - /v1/download/resource/{userId}/{courseId}/{filename}
# - /v1/download/outline/{userId}/{courseId}/{lessonNum}/{filename}
# - /v1/list/resources/{userId}/{courseId}
# - /v1/list/outlines/{userId}/{courseId}/{lessonNum}
