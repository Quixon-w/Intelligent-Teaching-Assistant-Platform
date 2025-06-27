# -*- coding: utf-8 -*-
import os
import pickle
import numpy as np
import faiss
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Union, Optional, List, Dict, Any
from sentence_transformers import SentenceTransformer
import asyncio
from threading import Lock

from utils.rwkv import *
from utils.session_manager import session_manager
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
    user_id: str = Field(..., description="用户ID，用于确定存储路径")
    session_id: str = Field(..., description="会话ID")
    is_teacher: bool = Field(False, description="是否为教师模式")
    course_id: Union[str, None] = Field(None, description="课程ID，已有文件查询模式下必填")
    lesson_num: Union[str, None] = Field(None, description="课时号，已有文件查询模式下必填")
    top_k: int = Field(3, description="搜索返回结果数量", ge=1, le=10)
    search_mode: str = Field("existing", description="搜索模式：existing(已有文件查询) 或 uploaded(用户上传文件查询)")
    max_tokens: int = Field(1000, description="生成回答的最大token数", ge=100, le=2000)
    temperature: float = Field(0.7, description="生成温度", ge=0.1, le=1.0)
    use_context: bool = Field(True, description="是否使用历史上下文")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "什么是进程？",
                "user_id": "teacher123",
                "session_id": "session456",
                "is_teacher": True,
                "course_id": "MATH101",
                "lesson_num": "lesson01",
                "top_k": 3,
                "search_mode": "existing",
                "max_tokens": 1000,
                "temperature": 0.7,
                "use_context": True
            }
        }
    }


def load_embeddings_model():
    """
    加载文本嵌入模型
    """
    try:
        model = SentenceTransformer("/data-extend/wangqianxu/wqxspace/ITAP/model/m3e-base")
        # 确保模型使用归一化
        model.encode("测试", normalize_embeddings=True)
        print("嵌入模型加载成功，已启用归一化")
        return model
    except Exception as e:
        print(f"加载嵌入模型失败: {e}")
        return None


def search_knowledge_db(user_id, session_id, query, is_teacher=False, course_id=None, lesson_num=None, top_k=3, search_mode="existing"):
    """
    从知识库中搜索相关内容 - 使用归一化嵌入和余弦相似度
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
        print(f"FAISS索引加载成功，包含 {index.ntotal} 个向量")
        
        # 读取元数据
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        # 提取文档存储和ID映射
        if isinstance(metadata, tuple) and len(metadata) >= 2:
            docstore = metadata[0]
            id_to_uuid = metadata[1]
            print(f"元数据加载成功，文档数量: {len(id_to_uuid)}")
        else:
            print("元数据格式不正确")
            return None
        
        # 对查询文本进行编码，使用归一化
        query_embedding = model.encode([query], normalize_embeddings=True)
        print(f"查询向量编码完成，维度: {query_embedding.shape}")
        
        # 执行向量搜索
        print(f"正在从知识库检索: {query}")
        print(f"搜索模式: {search_mode}, 路径: {vector_kb_folder}")
        
        # 搜索最相似的向量
        distances, indices = index.search(query_embedding, k=min(top_k, index.ntotal))
        
        # 打印原始距离信息
        print(f"原始距离: {distances[0]}")
        print(f"原始索引: {indices[0]}")
        
        # 提取搜索结果
        retrieved_contents = []
        print(f"\n=== 找到的最相近的{min(top_k, index.ntotal)}段内容 ===")
        
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(id_to_uuid):
                doc_id = id_to_uuid[idx]
                
                # 从文档存储中获取内容
                if hasattr(docstore, '_dict') and doc_id in docstore._dict:
                    doc = docstore._dict[doc_id]
                elif hasattr(docstore, 'docstore') and doc_id in docstore.docstore:
                    doc = docstore.docstore[doc_id]
                else:
                    print(f"无法找到文档ID: {doc_id}")
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
                    
                    # 计算余弦相似度 - 使用归一化向量
                    # 由于向量已经归一化，余弦相似度 = 1 - 距离/2
                    cosine_similarity = 1.0 - distance / 2.0
                    
                    # 打印调试信息
                    print(f"\n--- 第{i+1}段内容 ---")
                    print(f"原始距离: {distance:.6f}")
                    print(f"余弦相似度: {cosine_similarity:.6f}")
                    print(f"内容: {content[:200]}{'...' if len(content) > 200 else ''}")
                    
                    # 只返回相似度较高的内容（相似度 > 0.5）
                    if cosine_similarity > 0.5:
                        # 返回内容时不包含相似度标记，只在调试信息中显示
                        retrieved_contents.append(content)
                    else:
                        print(f"相似度过低，跳过此内容")
        
        print("=== 搜索结果结束 ===\n")
        
        if retrieved_contents:
            print(f"最终返回 {len(retrieved_contents)} 段相关内容")
            return "\n\n".join(retrieved_contents)
        else:
            print("没有找到相似度足够高的内容")
            return "未找到相关内容"
            
    except Exception as e:
        print(f"搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return f"搜索过程中出现错误: {str(e)}"


async def generate_answer_with_rwkv(prompt: str, request: Request, temperature: float):
    """
    使用RWKV模型生成回答 - 改进的生成逻辑
    """
    model: TextRWKV = global_var.get(global_var.Model)
    if model is None:
        raise Exception("模型未加载")
    
    try:
        # 设置生成参数
        model.temperature = temperature
        model.top_p = 0.9
        
        # 生成回答内容
        answer_content = ""
        token_count = 0
        last_complete_sentence = ""
        
        print("开始生成智能回答...")
        
        # 改进的停止条件，避免在句子中间截断
        stop_sequences = [
            "\n\n用户:", "\n\nUser:", "\n\n问题:", "\n\nQuestion:", 
            "\n\nQ:", "\n\nHuman:", "\n\n---", "\n\n###"
        ]
        
        for response, delta, _, _ in model.generate(prompt, stop=stop_sequences):
            answer_content += delta
            token_count += 1
            
            # 检查是否形成了完整的句子
            if delta in ['。', '！', '？', '；', '.', '!', '?', ';']:
                last_complete_sentence = answer_content
            
            # 检查请求是否断开
            if await request.is_disconnected():
                print("请求已断开")
                break
        
        # 如果最后没有完整句子，尝试找到最后一个完整句子
        if not last_complete_sentence and answer_content:
            # 查找最后一个句号、感叹号或问号
            for end_char in ['。', '！', '？', '；', '.', '!', '?', ';']:
                last_pos = answer_content.rfind(end_char)
                if last_pos != -1:
                    last_complete_sentence = answer_content[:last_pos + 1]
                    break
        
        # 使用最后一个完整句子，如果没有则使用全部内容
        final_answer = last_complete_sentence if last_complete_sentence else answer_content
        
        print(f"回答生成完成，生成长度: {len(final_answer)} 字符")
        
        return final_answer.strip()
        
    except Exception as e:
        print(f"生成回答时出错: {e}")
        raise Exception(f"生成回答失败: {str(e)}")


def build_qa_prompt(query: str, context: str, qa_history: List[Dict[str, Any]] = None) -> str:
    """
    构建问答提示词，支持历史上下文
    """
    # 清理context中的相似度标记
    cleaned_context = context
    if "[相似度:" in context:
        # 移除所有相似度标记
        import re
        cleaned_context = re.sub(r'\[相似度: [0-9.]+ \]', '', context)
        # 清理多余的空行
        cleaned_context = re.sub(r'\n\s*\n', '\n\n', cleaned_context).strip()
    
    prompt = f"""你是一个专业的教学助手。请基于以下知识内容，准确、完整地回答用户的问题。

知识内容：
{cleaned_context}

用户问题：{query}

请基于上述知识内容，给出准确、完整、易于理解的回答。要求：
1. 回答要条理清晰，重点突出
2. 如果知识内容中没有相关信息，请明确说明
3. 不要直接复制知识内容，要用自己的话重新组织
4. 回答要简洁明了，避免冗余

回答："""
    
    # 如果有历史问答记录，添加到提示词中
    if qa_history and len(qa_history) > 0:
        history_text = "\n\n历史问答记录：\n"
        for i, qa in enumerate(qa_history[-3:]):  # 只使用最近3个问答对
            history_text += f"问题{i+1}: {qa['query']}\n"
            history_text += f"回答{i+1}: {qa['answer'][:200]}...\n\n"
        
        # 在知识内容之前插入历史记录
        prompt = f"""你是一个专业的教学助手。请基于以下知识内容和历史问答记录，准确、完整地回答用户的问题。

{history_text}知识内容：
{cleaned_context}

用户问题：{query}

请基于上述知识内容和历史问答记录，给出准确、完整、易于理解的回答。要求：
1. 回答要条理清晰，重点突出
2. 如果知识内容中没有相关信息，请明确说明
3. 不要直接复制知识内容，要用自己的话重新组织
4. 回答要简洁明了，避免冗余

回答："""
    
    return prompt


@router.post("/v1/qa", tags=["QA"])
async def intelligent_qa(body: QABody, request: Request):
    """
    智能问答接口
    
    支持两种问答模式：
    1. existing: 已有文件问答 - 根据课程和课时号查找对应的知识库
    2. uploaded: 用户上传文件问答 - 查找用户上传到ask文件夹的文件对应的知识库
    
    支持历史上下文记忆功能
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
    if body.search_mode not in ["existing", "uploaded"]:
        raise HTTPException(
            status_code=400,
            detail="search_mode必须是 'existing' 或 'uploaded'"
        )
    
    # 验证已有文件查询模式下的必要参数
    if body.search_mode == "existing":
        if not body.course_id:
            raise HTTPException(
                status_code=400, 
                detail="已有文件查询模式下course_id不能为空"
            )
        
        if not body.lesson_num:
            raise HTTPException(
                status_code=400, 
                detail="已有文件查询模式下lesson_num不能为空"
            )
    
    try:
        with qa_lock:
            print(f"开始处理用户问题: {body.query}")
            
            # 获取历史问答记录（如果启用上下文）
            qa_history = []
            if body.use_context:
                # 从会话管理器获取历史消息
                context_messages = session_manager.get_context_messages(
                    body.user_id, body.session_id, max_messages=20, is_teacher=body.is_teacher
                )
                
                # 将历史消息转换为问答对格式
                qa_history = []
                for i in range(0, len(context_messages) - 1, 2):
                    if i + 1 < len(context_messages):
                        qa_history.append({
                            "query": context_messages[i]["content"],
                            "answer": context_messages[i + 1]["content"]
                        })
                
                print(f"获取到 {len(qa_history)} 条历史问答记录")
            
            # 1. 从知识库搜索相关内容
            search_result = search_knowledge_db(
                body.user_id,
                body.session_id, 
                body.query, 
                body.is_teacher, 
                body.course_id, 
                body.lesson_num, 
                body.top_k,
                body.search_mode
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
                    "user_id": body.user_id,
                    "session_id": body.session_id,
                    "is_teacher": body.is_teacher,
                    "course_id": body.course_id,
                    "lesson_num": body.lesson_num,
                    "search_mode": body.search_mode,
                    "answer": "抱歉，我在当前知识库中没有找到与您问题相关的信息。请尝试重新表述您的问题，或者检查是否选择了正确的课程和课时。",
                    "context": "未找到相关内容",
                    "has_context": False,
                    "use_context": body.use_context,
                    "history_count": len(qa_history)
                }
            
            # 2. 构建问答提示词（包含历史上下文）
            prompt = build_qa_prompt(body.query, search_result, qa_history if body.use_context else None)
            
            # 3. 使用RWKV模型生成回答
            answer = await generate_answer_with_rwkv(prompt, request, body.temperature)
            
            # 4. 保存问答历史记录到会话管理器
            messages = [
                {"role": "user", "content": body.query},
                {"role": "assistant", "content": answer}
            ]
            
            # 保存当前对话
            session_manager.save_dialogue(
                body.user_id,
                body.session_id,
                messages,
                answer,
                body.is_teacher
            )
            
            return {
                "success": True,
                "query": body.query,
                "user_id": body.user_id,
                "session_id": body.session_id,
                "is_teacher": body.is_teacher,
                "course_id": body.course_id,
                "lesson_num": body.lesson_num,
                "search_mode": body.search_mode,
                "answer": answer,
                "context": search_result,
                "has_context": True,
                "use_context": body.use_context,
                "history_count": len(qa_history)
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
        "lock_status": "忙碌中" if qa_lock.locked() else "空闲"
    }


# 新增的会话管理API
@router.get("/v1/qa/sessions/{user_id}/{session_id}/history", tags=["QA Session Management"])
async def get_qa_history(user_id: str, session_id: str, limit: int = 10, is_teacher: bool = False):
    """获取指定会话的问答历史记录"""
    try:
        dialogues = session_manager.get_session_dialogues(user_id, session_id, limit=limit, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "dialogues": dialogues,
            "count": len(dialogues)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving QA history: {str(e)}"
        )


@router.get("/v1/qa/sessions/{user_id}/{session_id}/context", tags=["QA Session Management"])
async def get_qa_context(user_id: str, session_id: str, max_messages: int = 20, is_teacher: bool = False):
    """获取指定会话的上下文消息"""
    try:
        context_messages = session_manager.get_context_messages(user_id, session_id, max_messages=max_messages, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "context_messages": context_messages,
            "count": len(context_messages)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving QA context: {str(e)}"
        )


@router.delete("/v1/qa/sessions/{user_id}/{session_id}/history", tags=["QA Session Management"])
async def clear_qa_history(user_id: str, session_id: str, is_teacher: bool = False):
    """清除指定会话的所有问答历史"""
    try:
        deleted_count = session_manager.clear_session_dialogues(user_id, session_id, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} dialogue files"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing QA history: {str(e)}"
        )


@router.get("/v1/qa/sessions/{user_id}", tags=["QA Session Management"])
async def get_user_qa_sessions(user_id: str, is_teacher: bool = False):
    """获取用户的所有问答会话ID"""
    try:
        sessions = session_manager.get_user_sessions(user_id, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "is_teacher": is_teacher,
            "qa_sessions": sessions,
            "session_count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user QA sessions: {str(e)}"
        ) 