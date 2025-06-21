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

from utils.rwkv import *
import global_var

router = APIRouter()

# 全局锁，用于控制并发请求
create_lock = Lock()


class CreateOutlineBody(BaseModel):
    session_id: str = Field(..., description="会话ID")
    courseID: str = Field(..., description="课程ID")
    lessonNum: Optional[str] = Field(None, description="课时号，可选，如果不提供则生成整个课程的大纲")
    outline_type: str = Field("course", description="大纲类型：course(课程大纲) 或 lesson(课时大纲)")
    # 教学大纲字数控制：课程大纲控制在2000-3000字，课时大纲控制在800-1200字
    max_words: int = Field(2500, description="最大字数限制，课程大纲建议2500字，课时大纲建议1000字", ge=500, le=5000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "teacher123",
                "courseID": "math101",
                "lessonNum": "lesson01",
                "outline_type": "lesson",
                "max_words": 1000
            }
        }
    }


def extract_text_from_faiss_db(db_path: str) -> str:
    """
    从FAISS向量数据库中提取文本内容
    参考analyze_faiss_db.py的实现
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


def get_file_content(session_id: str, courseID: str, lessonNum: Optional[str] = None):
    """
    获取课程内容，优先从FAISS向量数据库获取，如果失败则从文件获取
    """
    print(f"正在获取课程内容: session_id={session_id}, courseID={courseID}, lessonNum={lessonNum}")
    
    # 首先尝试从FAISS向量数据库获取内容
    if lessonNum:
        # 搜索特定课时的向量数据库
        vector_db_path = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{session_id}/{courseID}/{lessonNum}/vector_kb"
        print(f"尝试从向量数据库获取课时内容: {vector_db_path}")
        
        content = extract_text_from_faiss_db(vector_db_path)
        if content:
            print("成功从向量数据库获取课时内容")
            return content
    else:
        # 搜索整个课程的向量数据库（需要遍历所有课时）
        base_folder = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{session_id}/{courseID}"
        if not os.path.exists(base_folder):
            print(f"课程目录不存在: {base_folder}")
            return None
        
        # 获取所有课时目录
        lesson_dirs = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
        if not lesson_dirs:
            print(f"课程目录下没有课时文件夹: {base_folder}")
            return None
        
        # 合并所有课时的向量数据库内容
        all_content = []
        for lesson_dir in sorted(lesson_dirs):
            vector_db_path = os.path.join(base_folder, lesson_dir, "vector_kb")
            print(f"尝试从向量数据库获取课时 {lesson_dir} 内容: {vector_db_path}")
            
            lesson_content = extract_text_from_faiss_db(vector_db_path)
            if lesson_content:
                all_content.append(f"=== 课时 {lesson_dir} ===\n{lesson_content}")
        
        if all_content:
            combined_content = "\n\n".join(all_content)
            print("成功从向量数据库获取课程内容")
            return combined_content
    
    # 如果向量数据库获取失败，回退到文件读取方式
    print("向量数据库获取失败，回退到文件读取方式")
    
    # 根据是否提供lessonNum决定搜索路径
    if lessonNum:
        # 搜索特定课时的内容
        lesson_folder = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{session_id}/{courseID}/{lessonNum}"
    else:
        # 搜索整个课程的内容（需要遍历所有课时）
        base_folder = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{session_id}/{courseID}"
        if not os.path.exists(base_folder):
            print(f"课程目录不存在: {base_folder}")
            return None
        
        # 获取所有课时目录
        lesson_dirs = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
        if not lesson_dirs:
            print(f"课程目录下没有课时文件夹: {base_folder}")
            return None
        
        # 合并所有课时的内容
        all_content = []
        for lesson_dir in sorted(lesson_dirs):
            lesson_folder = os.path.join(base_folder, lesson_dir)
            lesson_content = read_files_in_folder(lesson_folder)
            if lesson_content:
                all_content.append(f"=== 课时 {lesson_dir} ===\n{lesson_content}")
        
        if not all_content:
            print("没有找到任何课程内容")
            return None
        
        return "\n\n".join(all_content)
    
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
        return ""
    
    all_content = []
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_type = filename.split('.')[-1].lower()
            
            try:
                if file_type in ['txt', 'md']:
                    # 读取文本文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    all_content.append(f"=== {filename} ===\n{content}")
                    
                elif file_type == 'pdf':
                    # 读取PDF文件
                    import fitz
                    doc = fitz.open(file_path)
                    content = ""
                    for page in doc:
                        page_text = page.get_text()
                        if isinstance(page_text, bytes):
                            try:
                                page_text = page_text.decode('utf-8')
                            except UnicodeDecodeError:
                                page_text = page_text.decode('utf-8', errors='ignore')
                        content += page_text
                    doc.close()
                    all_content.append(f"=== {filename} ===\n{content}")
                    
                elif file_type == 'docx':
                    # 读取DOCX文件
                    import docx
                    doc = docx.Document(file_path)
                    content = []
                    for paragraph in doc.paragraphs:
                        content.append(paragraph.text)
                    all_content.append(f"=== {filename} ===\n" + '\n'.join(content))
                    
            except Exception as e:
                print(f"读取文件 {filename} 时出错: {e}")
                continue
    
    return "\n\n".join(all_content)


def generate_outline_prompt(content: str, outline_type: str, max_words: int) -> str:
    """
    生成教学大纲的提示词
    """
    # 确保content是字符串格式
    if isinstance(content, bytes):
        try:
            content = content.decode('utf-8')
        except UnicodeDecodeError:
            content = content.decode('utf-8', errors='ignore')
    
    if outline_type == "course":
        # 课程大纲生成提示词
        prompt = "请根据以下课程内容，生成一份详细的教学大纲。\n\n"
        prompt += "要求：\n"
        prompt += "1. 大纲结构清晰，层次分明\n"
        prompt += "2. 包含课程目标、教学内容、教学重点、难点分析\n"
        prompt += f"3. 字数控制在{max_words}字以内\n"
        prompt += "4. 按照教学逻辑组织内容\n"
        prompt += "5. 适合教师教学使用\n\n"
        prompt += "课程内容：\n"
        prompt += content + "\n\n"
        prompt += "请生成教学大纲："
    else:
        # 课时大纲生成提示词
        prompt = "请根据以下课时内容，生成一份详细的课时教学大纲。\n\n"
        prompt += "要求：\n"
        prompt += "1. 大纲结构清晰，包含教学目标、教学内容、教学步骤\n"
        prompt += f"2. 字数控制在{max_words}字以内\n"
        prompt += "3. 突出教学重点和难点\n"
        prompt += "4. 包含教学建议和注意事项\n"
        prompt += "5. 适合单次课时教学使用\n\n"
        prompt += "课时内容：\n"
        prompt += content + "\n\n"
        prompt += "请生成课时教学大纲："
    
    return prompt


async def generate_outline_with_rwkv(prompt: str, request: Request):
    """
    使用RWKV模型生成教学大纲
    """
    model: AbstractRWKV = global_var.get(global_var.Model)
    if model is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "模型未加载")
    
    # 设置生成参数 - 使用更大的max_tokens让模型能够生成完整内容
    from utils.rwkv import ModelConfigBody, set_rwkv_config
    body = ModelConfigBody(
        max_tokens=4000,  # 增加最大token数，让模型有足够空间生成完整内容
        temperature=0.7,
        top_p=0.9,
        presence_penalty=0,
        frequency_penalty=0.1
    )
    
    try:
        # 设置模型配置
        set_rwkv_config(model, body)
        
        # 使用模型的generate方法进行非流式生成
        # 让模型自然结束，而不是强制截断
        generated_text = ""
        for response, delta, prompt_tokens, completion_tokens in model.generate(prompt):
            generated_text = response
            # 如果模型生成了结束标记或自然停止，就跳出循环
            if not delta:  # delta为空表示生成结束
                break
        
        return generated_text.strip()
        
    except Exception as e:
        print(f"生成大纲时出错: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"生成大纲失败: {str(e)}")


@router.post("/v1/create/outline", tags=["Create"])
@router.post("/create/outline", tags=["Create"])
async def create_outline(body: CreateOutlineBody, request: Request):
    """
    生成教学大纲
    """
    # 验证参数
    if body.outline_type not in ["course", "lesson"]:
        raise HTTPException(
            status_code=400,
            detail="outline_type必须是course或lesson"
        )
    
    # 获取课程内容
    content = get_file_content(body.session_id, body.courseID, body.lessonNum)
    
    if content is None:
        raise HTTPException(
            status_code=404,
            detail="未找到课程内容，请先上传相关文档"
        )
    
    # 生成提示词
    prompt = generate_outline_prompt(content, body.outline_type, body.max_words)
    
    print("=" * 50)
    print("生成的提示词:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)
    
    # 使用RWKV模型生成大纲
    try:
        outline_content = await generate_outline_with_rwkv(prompt, request)
        
        print("=" * 50)
        print("生成的教学大纲:")
        print("=" * 50)
        print(outline_content)
        print("=" * 50)
        
        return {
            "session_id": body.session_id,
            "courseID": body.courseID,
            "lessonNum": body.lessonNum,
            "outline_type": body.outline_type,
            "max_words": body.max_words,
            "content_length": len(content),
            "outline": outline_content,
            "message": "教学大纲生成成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成教学大纲失败: {str(e)}"
        )


@router.get("/v1/create/outline/status", tags=["Create"])
async def get_outline_status(session_id: str, courseID: str, lessonNum: Optional[str] = None):
    """
    获取大纲生成状态和可用内容信息
    """
    # 检查课程目录是否存在
    base_folder = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{session_id}/{courseID}"
    
    if not os.path.exists(base_folder):
        return {
            "status": "not_found",
            "message": "课程目录不存在",
            "session_id": session_id,
            "courseID": courseID,
            "lessonNum": lessonNum
        }
    
    if lessonNum:
        # 检查特定课时
        lesson_folder = f"{base_folder}/{lessonNum}"
        vector_db_path = f"{lesson_folder}/vector_kb"
        
        if not os.path.exists(lesson_folder):
            return {
                "status": "lesson_not_found",
                "message": "课时目录不存在",
                "session_id": session_id,
                "courseID": courseID,
                "lessonNum": lessonNum
            }
        
        # 优先检查向量数据库
        if os.path.exists(vector_db_path):
            return {
                "status": "ready",
                "message": "课时向量数据库已准备就绪，可以生成大纲",
                "session_id": session_id,
                "courseID": courseID,
                "lessonNum": lessonNum,
                "data_source": "vector_db"
            }
        
        # 检查是否有文件
        files = [f for f in os.listdir(lesson_folder) if os.path.isfile(os.path.join(lesson_folder, f))]
        if not files:
            return {
                "status": "no_content",
                "message": "课时目录下没有文件，请先上传文档",
                "session_id": session_id,
                "courseID": courseID,
                "lessonNum": lessonNum
            }
        
        return {
            "status": "ready",
            "message": "课时内容已准备就绪，可以生成大纲",
            "session_id": session_id,
            "courseID": courseID,
            "lessonNum": lessonNum,
            "files": files,
            "data_source": "files"
        }
    else:
        # 检查整个课程
        lesson_dirs = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
        
        if not lesson_dirs:
            return {
                "status": "no_lessons",
                "message": "课程下没有课时目录",
                "session_id": session_id,
                "courseID": courseID,
                "available_lessons": []
            }
        
        available_lessons = []
        for lesson_dir in lesson_dirs:
            lesson_folder = f"{base_folder}/{lesson_dir}"
            vector_db_path = f"{lesson_folder}/vector_kb"
            
            if os.path.exists(vector_db_path):
                available_lessons.append({
                    "lesson": lesson_dir,
                    "data_source": "vector_db"
                })
            else:
                files = [f for f in os.listdir(lesson_folder) if os.path.isfile(os.path.join(lesson_folder, f))]
                if files:
                    available_lessons.append({
                        "lesson": lesson_dir,
                        "files": files,
                        "data_source": "files"
                    })
        
        if not available_lessons:
            return {
                "status": "no_content",
                "message": "课程下没有可用的文件内容",
                "session_id": session_id,
                "courseID": courseID,
                "available_lessons": []
            }
        
        return {
            "status": "ready",
            "message": f"课程内容已准备就绪，共有{len(available_lessons)}个课时",
            "session_id": session_id,
            "courseID": courseID,
            "available_lessons": available_lessons
        } 