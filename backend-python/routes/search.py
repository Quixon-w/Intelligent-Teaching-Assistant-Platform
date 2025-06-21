import os
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Union, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

router = APIRouter()


class SearchBody(BaseModel):
    query: str = Field(..., description="查询内容")
    session_id: str = Field(..., description="会话ID")
    isTeacher: bool = Field(False, description="是否为教师模式")
    courseID: Union[str, None] = Field(None, description="课程ID，教师模式下必填")
    lessonNum: Union[str, None] = Field(None, description="课时号，教师模式下必填")
    top_k: int = Field(2, description="返回结果数量", ge=1, le=10)

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "什么是微积分？",
                "session_id": "session123",
                "isTeacher": False,
                "courseID": None,
                "lessonNum": None,
                "top_k": 2
            }
        }
    }


def search_knowledge_db(session_id, query, isTeacher=False, courseID=None, lessonNum=None, top_k=2):
    """
    从知识库中搜索相关内容
    """
    # 根据isTeacher决定知识库路径
    if isTeacher:
        # 教师模式：从Teachers目录下的session_id/courseID/lessonNum文件夹中搜索
        if not courseID:
            print("教师模式下courseID不能为空")
            return None
        if not lessonNum:
            print("教师模式下lessonNum不能为空")
            return None
        vector_kb_folder = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/{session_id}/{courseID}/{lessonNum}/vector_kb"
    else:
        # 学生模式：从Students目录下的session_id文件夹中搜索
        vector_kb_folder = f"/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Students/{session_id}/vector_kb"
    
    if not os.path.exists(vector_kb_folder):
        print(f"知识库路径不存在: {vector_kb_folder}")
        return None
    
    try:
        embeddings = HuggingFaceEmbeddings(model_name="/data-extend/wangqianxu/wqxspace/RWKV/model/m3e-base")
        vectordb = FAISS.load_local(vector_kb_folder, embeddings)
        
        # 搜索
        print(f"正在从知识库检索: {query}")
        search_results_with_scores = vectordb.similarity_search_with_score(query, k=top_k)
        
        if search_results_with_scores:
            # 将检索结果整合成一个文本块，处理编码问题
            retrieved_contents = []
            for result, _ in search_results_with_scores:
                content = result.page_content
                if isinstance(content, bytes):
                    try:
                        content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            content = content.decode('gbk')
                        except UnicodeDecodeError:
                            content = content.decode('utf-8', errors='ignore')
                retrieved_contents.append(content)
            return "\n".join(retrieved_contents)
        else:
            return ""
    except Exception as e:
        print(f"搜索失败: {e}")
        return ""


@router.post("/v1/search", tags=["Search"])
@router.post("/search", tags=["Search"])
async def search_knowledge(body: SearchBody):
    """
    搜索知识库内容
    """
    # 验证教师模式下的courseID和lessonNum
    if body.isTeacher and not body.courseID:
        raise HTTPException(
            status_code=400, 
            detail="教师模式下courseID不能为空"
        )
    
    if body.isTeacher and body.courseID and not body.lessonNum:
        raise HTTPException(
            status_code=400, 
            detail="教师模式下lessonNum不能为空"
        )
    
    # 执行搜索
    search_result = search_knowledge_db(
        body.session_id, 
        body.query, 
        body.isTeacher, 
        body.courseID, 
        body.lessonNum, 
        body.top_k
    )
    
    if search_result is None:
        raise HTTPException(
            status_code=404,
            detail="知识库不存在或courseID/lessonNum无效"
        )
    
    return {
        "query": body.query,
        "session_id": body.session_id,
        "isTeacher": body.isTeacher,
        "courseID": body.courseID,
        "lessonNum": body.lessonNum,
        "result": search_result if search_result else "未找到相关内容"
    } 