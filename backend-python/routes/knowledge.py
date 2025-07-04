from fastapi import APIRouter, HTTPException, Form, Query
from typing import Optional, List
from pydantic import BaseModel
from utils.knowledge import load_vector_db, search_knowledge_db, ChromaDBManager
from config.settings import get_settings

router = APIRouter()

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str
    user_id: str
    is_teacher: bool = False
    course_id: Optional[str] = None
    lesson_num: Optional[str] = None
    is_ask: bool = False
    top_k: int = 5
    use_rerank: bool = True

class SearchResponse(BaseModel):
    """搜索响应模型"""
    query: str
    results: List[dict]
    total_results: int
    collection_name: str
    use_rerank: bool

@router.post("/v1/knowledge/search")
async def search_knowledge(request: SearchRequest):
    """
    搜索知识库
    :param request: 搜索请求参数
    :return: 搜索结果
    """
    try:
        # 加载向量数据库
        chroma_manager = load_vector_db(
            userId=request.user_id,
            isTeacher=request.is_teacher,
            courseID=request.course_id,
            lessonNum=request.lesson_num,
            isAsk=request.is_ask
        )
        
        if not chroma_manager:
            raise HTTPException(
                status_code=404,
                detail="知识库不存在，请先上传文件构建知识库"
            )
        
        # 生成collection名称
        collection_name = f"kb_{request.user_id}_{request.course_id or 'student'}_{request.lesson_num or 'default'}"
        if request.is_ask:
            collection_name += "_ask"
        
        # 搜索知识库
        results = search_knowledge_db(
            query=request.query,
            chroma_manager=chroma_manager,
            collection_name=collection_name,
            top_k=request.top_k,
            use_rerank=request.use_rerank
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            collection_name=collection_name,
            use_rerank=request.use_rerank
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索知识库失败: {str(e)}"
        )

@router.get("/v1/knowledge/collections")
async def list_collections(
    user_id: str = Query(...),
    is_teacher: bool = Query(False)
):
    """
    列出用户的知识库collections
    :param user_id: 用户ID
    :param is_teacher: 是否为教师
    :return: collections列表
    """
    try:
        settings = get_settings()
        
        # 初始化ChromaDB管理器
        chroma_manager = ChromaDBManager(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT
        )
        
        # 获取所有collections
        collections = chroma_manager.list_collections()
        
        # 过滤出属于该用户的collections
        user_collections = []
        for collection in collections:
            if collection.name.startswith(f"kb_{user_id}_"):
                user_collections.append({
                    "name": collection.name,
                    "metadata": collection.metadata
                })
        
        return {
            "user_id": user_id,
            "is_teacher": is_teacher,
            "collections": user_collections,
            "total_count": len(user_collections)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取collections失败: {str(e)}"
        )

@router.delete("/v1/knowledge/collection")
async def delete_collection(
    collection_name: str = Query(...)
):
    """
    删除指定的collection
    :param collection_name: collection名称
    :return: 删除结果
    """
    try:
        settings = get_settings()
        
        # 初始化ChromaDB管理器
        chroma_manager = ChromaDBManager(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT
        )
        
        # 删除collection
        chroma_manager.delete_collection(collection_name)
        
        return {
            "message": f"成功删除collection: {collection_name}",
            "collection_name": collection_name
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除collection失败: {str(e)}"
        )

@router.get("/v1/knowledge/status")
async def get_knowledge_status():
    """
    获取知识库系统状态
    :return: 系统状态信息
    """
    try:
        settings = get_settings()
        
        # 检查ChromaDB连接
        chroma_manager = ChromaDBManager(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT
        )
        
        # 获取collections数量
        collections = chroma_manager.list_collections()
        
        return {
            "status": "healthy",
            "chromadb": {
                "host": settings.CHROMADB_HOST,
                "port": settings.CHROMADB_PORT,
                "connected": True,
                "collections_count": len(collections)
            },
            "models": {
                "bgem3_path": str(settings.BGEM3_MODEL_PATH),
                "reranker_path": str(settings.BGE_RERANKER_MODEL_PATH)
            },
            "config": {
                "chunk_size": settings.VECTOR_DB_CHUNK_SIZE,
                "chunk_overlap": settings.VECTOR_DB_CHUNK_OVERLAP
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "chromadb": {
                "host": settings.CHROMADB_HOST,
                "port": settings.CHROMADB_PORT,
                "connected": False
            }
        } 