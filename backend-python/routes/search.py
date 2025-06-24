import os
import pickle
import numpy as np
import faiss
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Union, Optional
from sentence_transformers import SentenceTransformer

router = APIRouter()


def get_user_path(user_id: str, is_teacher: bool) -> str:
    """根据userID和isTeacher确定用户路径"""
    user_type = "Teachers" if is_teacher else "Students"
    return os.path.join("/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge", user_type, user_id)


class SearchBody(BaseModel):
    query: str = Field(..., description="查询内容")
    userID: str = Field(..., description="用户ID，用于确定存储路径")
    sessionId: str = Field(..., description="会话ID")
    isTeacher: bool = Field(False, description="是否为教师模式")
    courseId: Union[str, None] = Field(None, description="课程ID，已有文件查询模式下必填")
    lessonNum: Union[str, None] = Field(None, description="课时号，已有文件查询模式下必填")
    topK: int = Field(2, description="返回结果数量", ge=1, le=10)
    searchMode: str = Field("existing", description="搜索模式：existing(已有文件查询) 或 uploaded(用户上传文件查询)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "什么是微积分？",
                "userID": "teacher123",
                "sessionId": "session456",
                "isTeacher": True,
                "courseId": "MATH101",
                "lessonNum": "lesson01",
                "topK": 2,
                "searchMode": "existing"
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


def search_knowledge_db(user_id, session_id, query, is_teacher=False, course_id=None, lesson_num=None, top_k=2, search_mode="existing"):
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


@router.post("/v1/search", tags=["Search"])
@router.post("/search", tags=["Search"])
async def search_knowledge(body: SearchBody):
    """
    搜索知识库内容
    
    支持两种搜索模式：
    1. existing: 已有文件查询 - 根据课程和课时号查找对应的知识库
    2. uploaded: 用户上传文件查询 - 查找用户上传到ask文件夹的文件对应的知识库
    """
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
    
    # 执行搜索
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
    
    return {
        "success": True,
        "query": body.query,
        "userID": body.userID,
        "sessionId": body.sessionId,
        "isTeacher": body.isTeacher,
        "courseId": body.courseId,
        "lessonNum": body.lessonNum,
        "searchMode": body.searchMode,
        "result": search_result
    } 