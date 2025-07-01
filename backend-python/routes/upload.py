import os
from fastapi import APIRouter, HTTPException, File, Form, UploadFile, status
from typing import Optional
from utils.knowledge import update_knowledge_db
from config.settings import get_settings

router = APIRouter()

@router.post("/v1/upload")
async def upload_file(
    file: UploadFile = File(...), 
    session_id: str = Form(...),
    user_id: str = Form(...),
    is_teacher: bool = Form(False),
    course_id: Optional[str] = Form(None),
    lesson_num: Optional[str] = Form(None),
    file_encoding: Optional[str] = Form("utf-8"),
    is_resource: bool = Form(False),
    is_ask: bool = Form(False)
):
    """
    上传文件并保存至服务器指定的路径，同时构建知识库
    :param file: 上传的文件
    :param session_id: 会话 ID，用于会话标识
    :param user_id: 用户ID，用于确定存储路径
    :param is_teacher: 是否为教师，决定存储路径
    :param course_id: 课程ID，教师模式下非ask文件时必填
    :param lesson_num: 课时号，教师模式下非ask文件时必填
    :param file_encoding: 可选，指定文件编码，默认 utf-8
    :param is_resource: 是否为学习资料
    :param is_ask: 是否为自己上传的可提问文件
    :return: 返回上传结果消息和知识库构建状态
    """
    # 检查文件类型，只允许pdf、docx、md和txt
    allowed_extensions = ['.pdf', '.docx', '.md', '.txt']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_extension}。只支持 PDF、DOCX、MD 和 TXT 格式"
        )
    
    # 验证参数
    if is_teacher and not is_ask and not course_id:
        raise HTTPException(
            status_code=400, 
            detail="教师模式下非ask文件时course_id不能为空"
        )
    
    if is_teacher and not is_ask and not is_resource and not lesson_num:
        raise HTTPException(
            status_code=400, 
            detail="教师模式下大纲参考文件时lesson_num不能为空"
        )
    
    # 使用配置管理系统获取路径
    settings = get_settings()
    
    # 根据is_teacher和文件类型决定存储路径，使用user_id作为主目录
    if is_teacher:
        # 教师模式
        base_folder = str(settings.TEACHERS_DIR)
        if is_resource:
            # 学习资料：保存到course_id级别
            session_folder = f"{base_folder}/{user_id}/{course_id}"
        elif is_ask:
            # 可对文件进行提问的文件：保存在ask文件夹
            session_folder = f"{base_folder}/{user_id}/ask"
        else:
            # 大纲与习题生成参考文件：保存到lesson_num级别
            session_folder = f"{base_folder}/{user_id}/{course_id}/{lesson_num}"
    else:
        # 学生模式：存储在Students目录下的user_id文件夹中
        base_folder = str(settings.STUDENTS_DIR)
        if is_ask:
            # 学生上传的可提问文件：保存在ask文件夹
            session_folder = f"{base_folder}/{user_id}/ask"
        else:
            # 其他文件：保存在user_id文件夹
            session_folder = f"{base_folder}/{user_id}"
    
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
            chroma_manager = None
            collection_name = None
            
            try:
                # 调用重构后的知识库更新函数
                chroma_manager = update_knowledge_db(
                    userId=user_id, 
                    isTeacher=is_teacher, 
                    courseID=course_id, 
                    lessonNum=lesson_num, 
                    isResource=is_resource, 
                    isAsk=is_ask
                )
                
                if chroma_manager:
                    # 生成collection名称
                    collection_name = f"kb_{user_id}_{course_id or 'student'}_{lesson_num or 'default'}"
                    if is_ask:
                        collection_name += "_ask"
                    
                    knowledge_status = f"知识库更新成功，Collection: {collection_name}"
                else:
                    knowledge_status = "知识库更新失败：没有找到可处理的文档"
                    knowledge_error = "文档加载或处理失败"
                    
            except Exception as e:
                knowledge_status = "知识库更新失败"
                knowledge_error = str(e)
                print(f"知识库更新错误: {e}")
            
            # 生成下载URL（仅对学习资料生成）
            download_url = None
            if is_resource and is_teacher:
                download_url = f"/v1/download/resource/{user_id}/{course_id}/{file.filename}"
            
            response_data = {
                "message": f"文件已成功上传",
                "session_id": session_id,
                "user_id": user_id,
                "is_teacher": is_teacher,
                "course_id": course_id,
                "lesson_num": lesson_num,
                "is_resource": is_resource,
                "is_ask": is_ask,
                "file_path": file_location,
                "download_url": download_url,
                "knowledge_status": knowledge_status,
                "collection_name": collection_name,
                "chromadb_host": settings.CHROMADB_HOST,
                "chromadb_port": settings.CHROMADB_PORT
            }
            
            # 如果知识库更新失败，添加错误信息
            if knowledge_error:
                response_data["knowledge_error"] = knowledge_error
            
            return response_data
        else:
            raise Exception("文件上传失败，目标文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

