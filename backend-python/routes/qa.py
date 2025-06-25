# -*- coding: utf-8 -*-
import os
import pickle
import numpy as np
import faiss
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Union, Optional
from sentence_transformers import SentenceTransformer
import asyncio
from threading import Lock

from utils.rwkv import *
import global_var

router = APIRouter()

# 全局锁，用于控制并发请求
qa_lock = Lock()


def get_user_path(user_id: str, is_teacher: bool) -> str:
    """根据userID和isTeacher确定用户路径"""
    user_type = "Teachers" if is_teacher else "Students"
    return os.path.join("/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge", user_type, user_id)


class QABody(BaseModel):
    query: str = Field(..., description="用户问题")
    userID: str = Field(..., description="用户ID，用于确定存储路径")
    sessionId: str = Field(..., description="会话ID")
    isTeacher: bool = Field(False, description="是否为教师模式")
    courseId: Union[str, None] = Field(None, description="课程ID，已有文件查询模式下必填")
    lessonNum: Union[str, None] = Field(None, description="课时号，已有文件查询模式下必填")
    topK: int = Field(3, description="搜索返回结果数量", ge=1, le=10)
    searchMode: str = Field("existing", description="搜索模式：existing(已有文件查询) 或 uploaded(用户上传文件查询)")
    maxTokens: int = Field(1000, description="生成回答的最大token数", ge=100, le=2000)
    temperature: float = Field(0.7, description="生成温度", ge=0.1, le=1.0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "什么是进程？",
                "userID": "teacher123",
                "sessionId": "session456",
                "isTeacher": True,
                "courseId": "MATH101",
                "lessonNum": "lesson01",
                "topK": 3,
                "searchMode": "existing",
                "maxTokens": 1000,
                "temperature": 0.7
            }
        }
    }


def load_embeddings_model():
    """
    加载文本嵌入模型
    """
    try:
        model = SentenceTransformer("/data-extend/wangqianxu/wqxspace/ITAP/model/m3e-base")
        return model
    except Exception as e:
        print(f"加载嵌入模型失败: {e}")
        return None


def search_knowledge_db(user_id, session_id, query, is_teacher=False, course_id=None, lesson_num=None, top_k=3, search_mode="existing"):
    """
    从知识库中搜索相关内容 - 使用直接的向量相似度查询
    """
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 根据搜索模式决定知识库路径
    if search_mode == "uploaded":
        # 用户上传文件查询模式 - 从用户路径下的ask/vector_kb中搜索
        vector_kb_folder = os.path.join(user_path, "ask", "vector_kb")
    else:
        # 已有文件查询模式 - 从用户路径下的课程/课时/vector_kb中搜索
        if not course_id:
            print("已有文件查询模式下courseId不能为空")
            return None
        if not lesson_num:
            print("已有文件查询模式下lessonNum不能为空")
            return None
        vector_kb_folder = os.path.join(user_path, course_id, lesson_num, "vector_kb")
    
    if not os.path.exists(vector_kb_folder):
        print(f"知识库路径不存在: {vector_kb_folder}")
        return None
    
    try:
        # 加载嵌入模型
        model = load_embeddings_model()
        if model is None:
            return "嵌入模型加载失败"
        
        # 加载FAISS索引
        index_path = os.path.join(vector_kb_folder, "index.faiss")
        metadata_path = os.path.join(vector_kb_folder, "index.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            print(f"FAISS索引文件不存在: {vector_kb_folder}")
            return None
        
        # 读取FAISS索引
        index = faiss.read_index(index_path)
        
        # 读取元数据
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        # 提取文档存储和ID映射
        if isinstance(metadata, tuple) and len(metadata) >= 2:
            docstore = metadata[0]
            id_to_uuid = metadata[1]
        else:
            print("元数据格式不正确")
            return None
        
        # 对查询文本进行编码
        query_embedding = model.encode([query])
        
        # 执行向量搜索
        print(f"正在从知识库检索: {query}")
        print(f"搜索模式: {search_mode}, 路径: {vector_kb_folder}")
        
        # 搜索最相似的向量
        distances, indices = index.search(query_embedding, k=min(top_k, index.ntotal))
        
        # 提取搜索结果
        retrieved_contents = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(id_to_uuid):
                doc_id = id_to_uuid[idx]
                
                # 从文档存储中获取内容
                if hasattr(docstore, '_dict') and doc_id in docstore._dict:
                    doc = docstore._dict[doc_id]
                elif hasattr(docstore, 'docstore') and doc_id in docstore.docstore:
                    doc = docstore.docstore[doc_id]
                else:
                    continue
                
                if hasattr(doc, 'page_content'):
                    content = doc.page_content
                    if isinstance(content, bytes):
                        try:
                            content = content.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                content = content.decode('gbk')
                            except UnicodeDecodeError:
                                content = content.decode('utf-8', errors='ignore')
                    
                    # 添加相似度分数信息（距离越小越相似）
                    similarity_score = 1.0 / (1.0 + distance)  # 将距离转换为相似度
                    content_with_score = f"[相似度: {similarity_score:.3f}] {content}"
                    retrieved_contents.append(content_with_score)
        
        if retrieved_contents:
            return "\n\n".join(retrieved_contents)
        else:
            return "未找到相关内容"
            
    except Exception as e:
        print(f"搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return f"搜索过程中出现错误: {str(e)}"


async def generate_answer_with_rwkv(prompt: str, request: Request, max_tokens: int, temperature: float):
    """
    使用RWKV模型生成回答
    """
    model: TextRWKV = global_var.get(global_var.Model)
    if model is None:
        raise Exception("模型未加载")
    
    try:
        # 设置生成参数
        model.max_tokens_per_generation = max_tokens
        model.temperature = temperature
        model.top_p = 0.9
        
        # 生成回答内容
        answer_content = ""
        token_count = 0
        
        print("开始生成智能回答...")
        
        for response, delta, _, _ in model.generate(prompt, stop=["\n\nUser", "\n\nQuestion", "\n\nQ", "\n\nHuman"]):
            answer_content += delta
            token_count += 1
            
            # 检查token数量限制
            if token_count > max_tokens:
                print(f"达到最大token限制 {max_tokens}")
                break
            
            # 检查请求是否断开
            if await request.is_disconnected():
                print("请求已断开")
                break
        
        print(f"回答生成完成，生成长度: {len(answer_content)} 字符")
        
        return answer_content.strip()
        
    except Exception as e:
        print(f"生成回答时出错: {e}")
        raise Exception(f"生成回答失败: {str(e)}")


def build_qa_prompt(query: str, context: str) -> str:
    """
    构建问答提示词
    """
    prompt = f"""你是一个专业的教学助手。请基于以下知识内容，准确、完整地回答用户的问题。

知识内容：
{context}

用户问题：{query}

请基于上述知识内容，给出准确、完整、易于理解的回答。如果知识内容中没有相关信息，请明确说明。回答要条理清晰，重点突出。

回答："""
    
    return prompt


@router.post("/v1/qa", tags=["QA"])
async def intelligent_qa(body: QABody, request: Request):
    """
    智能问答接口
    
    支持两种问答模式：
    1. existing: 已有文件问答 - 根据课程和课时号查找对应的知识库
    2. uploaded: 用户上传文件问答 - 查找用户上传到ask文件夹的文件对应的知识库
    """
    # 检查模型是否加载
    model: TextRWKV = global_var.get(global_var.Model)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="模型未加载"
        )
    
    # 检查是否已有问答任务在进行
    if qa_lock.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="已有问答任务在进行中，请稍后再试"
        )
    
    # 验证搜索模式
    if body.searchMode not in ["existing", "uploaded"]:
        raise HTTPException(
            status_code=400,
            detail="searchMode必须是 'existing' 或 'uploaded'"
        )
    
    # 验证已有文件查询模式下的必要参数
    if body.searchMode == "existing":
        if not body.courseId:
            raise HTTPException(
                status_code=400, 
                detail="已有文件查询模式下courseId不能为空"
            )
        
        if not body.lessonNum:
            raise HTTPException(
                status_code=400, 
                detail="已有文件查询模式下lessonNum不能为空"
            )
    
    try:
        with qa_lock:
            print(f"开始处理用户问题: {body.query}")
            
            # 1. 从知识库搜索相关内容
            search_result = search_knowledge_db(
                body.userID,
                body.sessionId, 
                body.query, 
                body.isTeacher, 
                body.courseId, 
                body.lessonNum, 
                body.topK,
                body.searchMode
            )
            
            if search_result is None:
                raise HTTPException(
                    status_code=404,
                    detail="知识库不存在或搜索失败"
                )
            
            if search_result == "未找到相关内容":
                # 如果没有找到相关内容，返回提示信息
                return {
                    "success": True,
                    "query": body.query,
                    "userID": body.userID,
                    "sessionId": body.sessionId,
                    "isTeacher": body.isTeacher,
                    "courseId": body.courseId,
                    "lessonNum": body.lessonNum,
                    "searchMode": body.searchMode,
                    "answer": "抱歉，我在当前知识库中没有找到与您问题相关的信息。请尝试重新表述您的问题，或者检查是否选择了正确的课程和课时。",
                    "context": "未找到相关内容",
                    "hasContext": False
                }
            
            # 2. 构建问答提示词
            prompt = build_qa_prompt(body.query, search_result)
            
            # 3. 使用RWKV模型生成回答
            answer = await generate_answer_with_rwkv(prompt, request, body.maxTokens, body.temperature)
            
            return {
                "success": True,
                "query": body.query,
                "userID": body.userID,
                "sessionId": body.sessionId,
                "isTeacher": body.isTeacher,
                "courseId": body.courseId,
                "lessonNum": body.lessonNum,
                "searchMode": body.searchMode,
                "answer": answer,
                "context": search_result,
                "hasContext": True
            }
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"智能问答时出错: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能问答失败: {str(e)}"
        )


@router.get("/v1/qa/status", tags=["QA"])
async def get_qa_status():
    """
    获取问答服务状态
    """
    model: TextRWKV = global_var.get(global_var.Model)
    return {
        "service": "智能问答服务",
        "status": "运行中" if model is not None else "模型未加载",
        "model": model.name if model is not None else "无",
        "lockStatus": "忙碌中" if qa_lock.locked() else "空闲"
    } 