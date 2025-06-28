# -*- coding: utf-8 -*-
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

router = APIRouter()


def get_user_path(user_id: str, is_teacher: bool) -> str:
    """根据userID和isTeacher确定用户路径"""
    user_type = "Teachers" if is_teacher else "Students"
    return os.path.join("/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge", user_type, user_id)


@router.get("/v1/download/resource/{user_id}/{course_id}/{filename}")
async def download_resource_file(user_id: str, course_id: str, filename: str, is_teacher: bool = True):
    """
    下载学习资料文件
    :param user_id: 用户ID
    :param course_id: 课程ID
    :param filename: 文件名
    :param is_teacher: 是否为教师用户
    :return: 文件下载响应
    """
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 构建文件路径
    file_path = os.path.join(user_path, course_id, filename)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"文件不存在: {filename}"
        )
    
    # 检查文件是否为普通文件
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=400, 
            detail=f"路径不是文件: {filename}"
        )
    
    # 返回文件下载响应
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@router.get("/v1/download/outline/{user_id}/{course_id}/{lesson_num}/{filename}")
async def download_outline_file(user_id: str, course_id: str, lesson_num: str, filename: str, is_teacher: bool = True):
    """
    下载课时教学大纲文件
    :param user_id: 用户ID
    :param course_id: 课程ID
    :param lesson_num: 课时号
    :param filename: 文件名
    :param is_teacher: 是否为教师用户
    :return: 文件下载响应
    """
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 构建文件路径
    file_path = os.path.join(user_path, course_id, lesson_num, "outline", filename)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"大纲文件不存在: {filename}"
        )
    
    # 检查文件是否为普通文件
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=400, 
            detail=f"路径不是文件: {filename}"
        )
    
    # 返回文件下载响应
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='text/plain'
    )


@router.get("/v1/list/resources/{user_id}/{course_id}")
async def list_resource_files(user_id: str, course_id: str, is_teacher: bool = True):
    """
    列出指定课程的所有学习资料文件
    :param user_id: 用户ID
    :param course_id: 课程ID
    :param is_teacher: 是否为教师用户
    :return: 文件列表
    """
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 构建目录路径
    resource_folder = os.path.join(user_path, course_id)
    
    # 检查目录是否存在
    if not os.path.exists(resource_folder):
        return {"files": [], "message": "课程目录不存在"}
    
    try:
        # 获取目录中的所有文件
        files = []
        for filename in os.listdir(resource_folder):
            file_path = os.path.join(resource_folder, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                download_url = f"/v1/download/resource/{user_id}/{course_id}/{filename}"
                files.append({
                    "filename": filename,
                    "size": file_size,
                    "download_url": download_url
                })
        
        return {
            "files": files,
            "total_files": len(files),
            "course_id": course_id,
            "user_id": user_id,
            "is_teacher": is_teacher
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"获取文件列表失败: {str(e)}"
        )


@router.get("/v1/list/outlines/{user_id}/{course_id}/{lesson_num}")
async def list_outline_files(user_id: str, course_id: str, lesson_num: str, is_teacher: bool = True):
    """
    列出指定课时的所有教学大纲文件
    :param user_id: 用户ID
    :param course_id: 课程ID
    :param lesson_num: 课时号
    :param is_teacher: 是否为教师用户
    :return: 文件列表
    """
    from datetime import datetime
    
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 构建目录路径
    outline_folder = os.path.join(user_path, course_id, lesson_num, "outline")
    
    # 检查目录是否存在
    if not os.path.exists(outline_folder):
        return {"files": [], "message": "大纲目录不存在"}
    
    try:
        # 获取目录中的所有文件
        files = []
        for filename in os.listdir(outline_folder):
            file_path = os.path.join(outline_folder, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                download_url = f"/v1/download/outline/{user_id}/{course_id}/{lesson_num}/{filename}"
                files.append({
                    "filename": filename,
                    "size": file_size,
                    "download_url": download_url,
                    "created_time": datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 按创建时间倒序排列
        files.sort(key=lambda x: x['created_time'], reverse=True)
        
        return {
            "files": files,
            "total_files": len(files),
            "course_id": course_id,
            "lesson_num": lesson_num,
            "user_id": user_id,
            "is_teacher": is_teacher
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"获取大纲文件列表失败: {str(e)}"
        ) 