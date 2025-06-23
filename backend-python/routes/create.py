# -*- coding: utf-8 -*-
import os
import json
import pickle
import faiss
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Union, Optional
import asyncio
from threading import Lock
from datetime import datetime

from utils.rwkv import *
import global_var

router = APIRouter()

# 全局锁，用于控制并发请求
create_lock = Lock()


class CreateOutlineBody(BaseModel):
    sessionId: str = Field(..., description="会话ID")
    courseId: str = Field(..., description="课程ID")
    lessonNum: str = Field(..., description="课时号，必填")
    # 教学大纲字数控制：课时大纲控制在800-1200字
    maxWords: int = Field(1000, description="最大字数限制，课时大纲建议1000字", ge=500, le=2000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "sessionId": "teacher123",
                "courseId": "math101",
                "lessonNum": "lesson01",
                "maxWords": 1000
            }
        }
    }


def extract_text_from_faiss_db(db_path: str) -> str:
    """
    从FAISS向量数据库中提取文本内容
    """
    print(f"正在从FAISS数据库提取文本: {db_path}")
    
    # 检查数据库文件是否存在
    index_faiss_path = os.path.join(db_path, "index.faiss")
    index_pkl_path = os.path.join(db_path, "index.pkl")
    
    if not os.path.exists(index_faiss_path) or not os.path.exists(index_pkl_path):
        print(f"FAISS数据库文件不存在: {db_path}")
        return None
    
    try:
        # 读取FAISS索引
        index = faiss.read_index(index_faiss_path)
        print(f"FAISS索引信息: 向量数量={index.ntotal}, 维度={index.d}")
        
        # 读取元数据
        with open(index_pkl_path, 'rb') as f:
            metadata = pickle.load(f)
        
        print(f"元数据类型: {type(metadata)}")
        
        # 提取文本内容
        extracted_texts = []
        
        if isinstance(metadata, tuple) and len(metadata) >= 2:
            docstore = metadata[0]
            id_to_uuid = metadata[1]
            
            print(f"文档存储类型: {type(docstore)}")
            print(f"ID映射: {id_to_uuid}")
            
            # 尝试提取文档存储中的内容
            try:
                # 检查文档存储的属性
                if hasattr(docstore, '_dict'):
                    print(f"文档存储中的文档数量: {len(docstore._dict)}")
                    for doc_id, doc in docstore._dict.items():
                        if hasattr(doc, 'page_content'):
                            # UTF-8解码处理标记注释
                            # 如果遇到utf-8无法解码的情况，请直接跳过当前字节
                            try:
                                content = doc.page_content
                                if isinstance(content, bytes):
                                    content = content.decode('utf-8', errors='ignore')
                                extracted_texts.append(content)
                                print(f"提取文档 {doc_id}: {content[:100]}...")
                            except Exception as decode_error:
                                print(f"跳过文档 {doc_id} (解码错误): {decode_error}")
                                continue
                        
                        if hasattr(doc, 'metadata'):
                            print(f"文档 {doc_id} 元数据: {doc.metadata}")
                
                elif hasattr(docstore, 'docstore'):
                    print(f"文档存储中的文档数量: {len(docstore.docstore)}")
                    for doc_id, doc in docstore.docstore.items():
                        if hasattr(doc, 'page_content'):
                            try:
                                content = doc.page_content
                                if isinstance(content, bytes):
                                    content = content.decode('utf-8', errors='ignore')
                                extracted_texts.append(content)
                                print(f"提取文档 {doc_id}: {content[:100]}...")
                            except Exception as decode_error:
                                print(f"跳过文档 {doc_id} (解码错误): {decode_error}")
                                continue
                        
                        if hasattr(doc, 'metadata'):
                            print(f"文档 {doc_id} 元数据: {doc.metadata}")
                
                else:
                    # 尝试其他可能的属性
                    for attr in dir(docstore):
                        if not attr.startswith('_') and not callable(getattr(docstore, attr)):
                            try:
                                value = getattr(docstore, attr)
                                if isinstance(value, dict) and len(value) > 0:
                                    print(f"找到文档存储属性: {attr}")
                                    print(f"文档数量: {len(value)}")
                                    for doc_id, doc in value.items():
                                        if hasattr(doc, 'page_content'):
                                            try:
                                                content = doc.page_content
                                                if isinstance(content, bytes):
                                                    content = content.decode('utf-8', errors='ignore')
                                                extracted_texts.append(content)
                                                print(f"提取文档 {doc_id}: {content[:100]}...")
                                            except Exception as decode_error:
                                                print(f"跳过文档 {doc_id} (解码错误): {decode_error}")
                                                continue
                                        
                                        if hasattr(doc, 'metadata'):
                                            print(f"文档 {doc_id} 元数据: {doc.metadata}")
                                    break
                            except:
                                continue
                                
            except Exception as e:
                print(f"提取文档内容时出错: {e}")
                return None
        
        if extracted_texts:
            combined_text = "\n\n".join(extracted_texts)
            print(f"成功提取文本内容，总长度: {len(combined_text)} 字符")
            print("=" * 50)
            print("提取的文本内容:")
            print("=" * 50)
            print(combined_text[:500] + "..." if len(combined_text) > 500 else combined_text)
            print("=" * 50)
            return combined_text
        else:
            print("未找到可提取的文本内容")
            return None
            
    except Exception as e:
        print(f"从FAISS数据库提取文本时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_file_content(sessionId: str, courseId: str, lessonNum: str):
    """
    获取课时内容，优先从FAISS向量数据库获取，如果失败则从文件获取
    """
    print(f"正在获取课时内容: sessionId={sessionId}, courseId={courseId}, lessonNum={lessonNum}")
    
    # 首先尝试从FAISS向量数据库获取内容
    vector_db_path = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{sessionId}/{courseId}/{lessonNum}/vector_kb"
    print(f"尝试从向量数据库获取课时内容: {vector_db_path}")
    
    content = extract_text_from_faiss_db(vector_db_path)
    if content:
        print("成功从向量数据库获取课时内容")
        return content
    
    # 如果向量数据库获取失败，回退到文件读取方式
    print("向量数据库获取失败，回退到文件读取方式")
    
    # 搜索特定课时的内容
    lesson_folder = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{sessionId}/{courseId}/{lessonNum}"
    
    # 读取特定课时的文件内容
    if not os.path.exists(lesson_folder):
        print(f"课时目录不存在: {lesson_folder}")
        return None
    
    content = read_files_in_folder(lesson_folder)
    return content


def read_files_in_folder(folder_path: str) -> str:
    """
    读取文件夹中的所有支持的文件内容
    """
    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        return None
    
    content_parts = []
    
    try:
        # 遍历文件夹中的所有文件
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # 跳过目录和隐藏文件
            if os.path.isdir(file_path) or filename.startswith('.'):
                continue
            
            # 只处理支持的文件类型
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension not in ['.txt', '.md', '.pdf', '.docx']:
                continue
            
            try:
                if file_extension in ['.txt', '.md']:
                    # 读取文本文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        content_parts.append(f"文件: {filename}\n{file_content}")
                elif file_extension in ['.pdf', '.docx']:
                    # 对于PDF和DOCX文件，这里需要添加相应的解析逻辑
                    # 暂时跳过，或者可以调用外部工具进行解析
                    content_parts.append(f"文件: {filename} (PDF/DOCX文件，需要特殊处理)")
                    
            except Exception as e:
                print(f"读取文件 {filename} 时出错: {e}")
                continue
        
        if content_parts:
            return "\n\n".join(content_parts)
        else:
            print(f"文件夹 {folder_path} 中没有找到可读取的文件")
            return None
            
    except Exception as e:
        print(f"读取文件夹 {folder_path} 时出错: {e}")
        return None


def generate_outline_prompt(content: str, max_words: int) -> str:
    """
    根据内容生成大纲提示词
    """
    prompt = f"""请根据以下教学内容，生成一个详细的教学大纲。大纲应该：

1. 结构清晰，层次分明
2. 包含主要知识点和重点内容
3. 适合教学使用
4. 字数控制在{max_words}字左右

教学内容：
{content[:2000]}  # 限制内容长度，避免token过多

请生成教学大纲："""

    return prompt


def save_outline_to_file(sessionId: str, courseId: str, lessonNum: str, outline_content: str) -> dict:
    """
    将生成的大纲保存到文件
    """
    try:
        # 创建大纲保存目录
        outline_dir = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{sessionId}/{courseId}/{lessonNum}/outline"
        os.makedirs(outline_dir, exist_ok=True)
        
        # 生成文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outline_{timestamp}.txt"
        file_path = os.path.join(outline_dir, filename)
        
        # 保存大纲内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(outline_content)
        
        print(f"大纲已保存到: {file_path}")
        
        return {
            "success": True,
            "filePath": file_path,
            "filename": filename,
            "downloadUrl": f"/v1/download/outline/{sessionId}/{courseId}/{lessonNum}/{filename}"
        }
        
    except Exception as e:
        print(f"保存大纲文件时出错: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def generate_outline_with_rwkv(prompt: str, request: Request):
    """
    使用RWKV模型生成大纲
    """
    model: TextRWKV = global_var.get(global_var.Model)
    if model is None:
        raise Exception("模型未加载")
    
    try:
        # 设置生成参数
        generation_config = {
            "maxTokens": 2000,
            "temperature": 0.7,
            "topP": 0.9,
            "presencePenalty": 0.1,
            "frequencyPenalty": 0.1
        }
        
        # 生成大纲内容
        outline_content = ""
        token_count = 0
        max_tokens = generation_config["maxTokens"]
        
        print("开始生成教学大纲...")
        
        for response, delta, _, _ in model.generate(prompt, stop=["\n\n", "###", "---", "问题", "题目"]):
            outline_content += delta
            token_count += 1
            
            # 检查token数量限制
            if token_count > max_tokens:
                print(f"达到最大token限制 {max_tokens}")
                break
            
            # 检查请求是否断开
            if await request.is_disconnected():
                print("请求已断开")
                break
        
        print(f"大纲生成完成，生成长度: {len(outline_content)} 字符")
        
        return outline_content.strip()
        
    except Exception as e:
        print(f"生成大纲时出错: {e}")
        raise Exception(f"生成大纲失败: {str(e)}")


@router.post("/v1/create/outline", tags=["Create"])
@router.post("/create/outline", tags=["Create"])
async def create_outline(body: CreateOutlineBody, request: Request):
    """
    创建教学大纲
    """
    # 检查模型是否加载
    model: TextRWKV = global_var.get(global_var.Model)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="模型未加载"
        )
    
    # 检查是否已有生成任务在进行
    if create_lock.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="已有大纲生成任务在进行中，请稍后再试"
        )
    
    try:
        with create_lock:
            print(f"开始为课时 {body.lessonNum} 生成教学大纲")
            
            # 获取课时内容
            content = get_file_content(body.sessionId, body.courseId, body.lessonNum)
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"未找到课时 {body.lessonNum} 的内容，请先上传相关文件"
                )
            
            # 生成大纲提示词
            prompt = generate_outline_prompt(content, body.maxWords)
            
            # 使用RWKV模型生成大纲
            outline_content = await generate_outline_with_rwkv(prompt, request)
            
            # 保存大纲到文件
            save_result = save_outline_to_file(body.sessionId, body.courseId, body.lessonNum, outline_content)
            
            if save_result["success"]:
                return {
                    "success": True,
                    "message": "教学大纲生成成功",
                    "sessionId": body.sessionId,
                    "courseId": body.courseId,
                    "lessonNum": body.lessonNum,
                    "outlineContent": outline_content[:500] + "..." if len(outline_content) > 500 else outline_content,
                    "downloadUrl": save_result["downloadUrl"],
                    "filename": save_result["filename"]
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"保存大纲文件失败: {save_result['error']}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建大纲时出错: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建大纲失败: {str(e)}"
        )


@router.get("/v1/create/outline/status", tags=["Create"])
async def get_outline_status(sessionId: str, courseId: str, lessonNum: str):
    """
    获取大纲生成状态
    """
    try:
        # 检查大纲目录是否存在
        outline_dir = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{sessionId}/{courseId}/{lessonNum}/outline"
        
        if not os.path.exists(outline_dir):
            return {
                "hasOutline": False,
                "message": "大纲目录不存在"
            }
        
        # 检查是否有大纲文件
        outline_files = [f for f in os.listdir(outline_dir) if f.startswith('outline_') and f.endswith('.txt')]
        
        if outline_files:
            # 获取最新的大纲文件
            latest_file = max(outline_files, key=lambda x: os.path.getctime(os.path.join(outline_dir, x)))
            file_path = os.path.join(outline_dir, latest_file)
            
            return {
                "hasOutline": True,
                "message": "大纲已存在",
                "latestFile": latest_file,
                "downloadUrl": f"/v1/download/outline/{sessionId}/{courseId}/{lessonNum}/{latest_file}",
                "createdTime": datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {
                "hasOutline": False,
                "message": "大纲文件不存在"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取大纲状态失败: {str(e)}"
        ) 