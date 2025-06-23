# -*- coding: utf-8 -*-
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

router = APIRouter()


@router.get("/v1/download/resource/{sessionId}/{courseId}/{filename}")
async def download_resource_file(sessionId: str, courseId: str, filename: str):
    """
    下载学习资料文件
    :param sessionId: 会话ID
    :param courseId: 课程ID
    :param filename: 文件名
    :return: 文件下载响应
    """
    # 构建文件路径
    base_folder = "/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers"
    file_path = f"{base_folder}/{sessionId}/{courseId}/{filename}"
    
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


@router.get("/v1/download/outline/{sessionId}/{courseId}/{lessonNum}/{filename}")
async def download_outline_file(sessionId: str, courseId: str, lessonNum: str, filename: str):
    """
    下载课时教学大纲文件
    :param sessionId: 会话ID
    :param courseId: 课程ID
    :param lessonNum: 课时号
    :param filename: 文件名
    :return: 文件下载响应
    """
    # 构建文件路径
    file_path = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{sessionId}/{courseId}/{lessonNum}/outline/{filename}"
    
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


@router.get("/v1/list/resources/{sessionId}/{courseId}")
async def list_resource_files(sessionId: str, courseId: str):
    """
    列出指定课程的所有学习资料文件
    :param sessionId: 会话ID
    :param courseId: 课程ID
    :return: 文件列表
    """
    # 构建目录路径
    base_folder = "/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers"
    resource_folder = f"{base_folder}/{sessionId}/{courseId}"
    
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
                download_url = f"/v1/download/resource/{sessionId}/{courseId}/{filename}"
                files.append({
                    "filename": filename,
                    "size": file_size,
                    "downloadUrl": download_url
                })
        
        return {
            "files": files,
            "totalFiles": len(files),
            "courseId": courseId,
            "sessionId": sessionId
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"获取文件列表失败: {str(e)}"
        )


@router.get("/v1/list/outlines/{sessionId}/{courseId}/{lessonNum}")
async def list_outline_files(sessionId: str, courseId: str, lessonNum: str):
    """
    列出指定课时的所有教学大纲文件
    :param sessionId: 会话ID
    :param courseId: 课程ID
    :param lessonNum: 课时号
    :return: 文件列表
    """
    from datetime import datetime
    
    # 构建目录路径
    outline_folder = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{sessionId}/{courseId}/{lessonNum}/outline"
    
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
                download_url = f"/v1/download/outline/{sessionId}/{courseId}/{lessonNum}/{filename}"
                files.append({
                    "filename": filename,
                    "size": file_size,
                    "downloadUrl": download_url,
                    "createdTime": datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 按创建时间倒序排列
        files.sort(key=lambda x: x['createdTime'], reverse=True)
        
        return {
            "files": files,
            "totalFiles": len(files),
            "courseId": courseId,
            "lessonNum": lessonNum,
            "sessionId": sessionId
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"获取大纲文件列表失败: {str(e)}"
        ) 