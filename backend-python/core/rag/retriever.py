# -*- coding: utf-8 -*-
"""
混合检索策略：向量检索 + 关键词检索 + 重排序
"""
import os
import asyncio
from typing import List, Dict, Any, Optional
import numpy as np
from cachetools import TTLCache

from config.settings import get_settings


class HybridRetriever:
    """混合检索策略：向量检索 + 关键词检索 + 重排序"""
    
    def __init__(self):
        # 缓存设置
        self.embedding_cache = TTLCache(maxsize=1000, ttl=3600)  # 1小时缓存
        self.retrieval_cache = TTLCache(maxsize=500, ttl=1800)   # 30分钟缓存
        
        self.settings = get_settings()
    
    async def retrieve(self, query: str, user_id: str, course_id: Optional[str] = None,
                      lesson_num: Optional[str] = None, search_mode: str = "existing",
                      context: Optional[Dict] = None, task_type: str = "qa",
                      top_k: int = 3, use_keyword: bool = True, **kwargs) -> List[str]:
        """主检索方法"""
        cache_key = self._generate_cache_key(query, user_id, course_id, lesson_num, search_mode, task_type)
        
        # 1. 检查缓存
        if cached_result := self.retrieval_cache.get(cache_key):
            return cached_result
        
        try:
            # 2. 向量检索
            vector_results = await self._vector_search(
                query, user_id, course_id, lesson_num, search_mode, top_k=10
            )
            
            # 3. 关键词检索（可选）
            keyword_results = []
            if use_keyword and vector_results:
                keyword_results = await self._keyword_search(
                    query, vector_results, top_k=5
                )
            
            # 4. 结果融合
            combined_results = self._merge_results(vector_results, keyword_results)
            
            # 5. 重排序
            final_results = await self._rerank(query, combined_results, top_k=top_k)
            
            # 6. 缓存结果
            self.retrieval_cache[cache_key] = final_results
            
            return final_results
            
        except Exception as e:
            print(f"检索失败: {e}")
            return []
    
    async def _vector_search(self, query: str, user_id: str, course_id: Optional[str],
                           lesson_num: Optional[str], search_mode: str, top_k: int) -> List[str]:
        """向量检索"""
        try:
            # 获取用户路径
            user_path = self._get_user_path(user_id, search_mode == "uploaded")
            
            # 根据搜索模式决定知识库路径
            if search_mode == "uploaded":
                vector_kb_folder = os.path.join(user_path, "ask", "vector_kb")
            else:
                if not course_id or not lesson_num:
                    return []
                vector_kb_folder = os.path.join(user_path, course_id, lesson_num, "vector_kb")
            
            if not os.path.exists(vector_kb_folder):
                return []
            
            # 使用现有的FAISS检索逻辑（临时方案）
            return await self._faiss_search(query, vector_kb_folder, top_k)
            
        except Exception as e:
            print(f"向量检索失败: {e}")
            return []
    
    async def _faiss_search(self, query: str, vector_kb_folder: str, top_k: int) -> List[str]:
        """FAISS检索（临时方案，后续会替换为ChromaDB）"""
        try:
            import faiss
            import pickle
            
            # 加载FAISS索引
            index_path = os.path.join(vector_kb_folder, "index.faiss")
            metadata_path = os.path.join(vector_kb_folder, "index.pkl")
            
            if not os.path.exists(index_path) or not os.path.exists(metadata_path):
                return []
            
            # 读取FAISS索引
            index = faiss.read_index(index_path)
            
            # 读取元数据
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            # 获取嵌入模型
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(str(self.settings.EMBEDDING_MODEL_PATH))
            
            # 对查询文本进行编码
            query_embedding = model.encode([query], normalize_embeddings=True)
            
            # 执行向量搜索
            distances, indices = index.search(query_embedding, k=min(top_k, index.ntotal))
            
            # 提取搜索结果
            retrieved_contents = []
            
            if isinstance(metadata, tuple) and len(metadata) >= 2:
                docstore = metadata[0]
                id_to_uuid = metadata[1]
                
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
                                    content = content.decode('utf-8', errors='ignore')
                            
                            # 计算余弦相似度
                            cosine_similarity = 1.0 - distance / 2.0
                            
                            # 只返回相似度较高的内容
                            if cosine_similarity > 0.5:
                                retrieved_contents.append(content)
            
            return retrieved_contents
            
        except Exception as e:
            print(f"FAISS检索失败: {e}")
            return []
    
    async def _keyword_search(self, query: str, candidate_docs: List[str], top_k: int) -> List[str]:
        """关键词检索（基于TF-IDF或BM25）"""
        try:
            # 简单的关键词匹配
            query_keywords = set(query.lower().split())
            scored_docs = []
            
            for doc in candidate_docs:
                doc_keywords = set(doc.lower().split())
                overlap = len(query_keywords & doc_keywords)
                if overlap > 0:
                    score = overlap / len(query_keywords)
                    scored_docs.append((score, doc))
            
            # 按分数排序
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            
            return [doc for score, doc in scored_docs[:top_k]]
            
        except Exception as e:
            print(f"关键词检索失败: {e}")
            return []
    
    def _merge_results(self, vector_results: List[str], keyword_results: List[str]) -> List[str]:
        """结果融合"""
        # 简单的去重和排序
        all_results = vector_results + keyword_results
        unique_results = []
        seen = set()
        
        for result in all_results:
            if result not in seen:
                unique_results.append(result)
                seen.add(result)
        
        return unique_results
    
    async def _rerank(self, query: str, documents: List[str], top_k: int) -> List[str]:
        """重排序（简化版本）"""
        try:
            # 这里可以实现更复杂的重排序逻辑
            # 例如：使用交叉编码器进行精确排序
            
            # 临时使用简单的相似度重排序
            scored_docs = []
            for doc in documents:
                # 计算简单的文本相似度
                similarity = self._calculate_similarity(query, doc)
                scored_docs.append((similarity, doc))
            
            # 按相似度排序
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            
            return [doc for score, doc in scored_docs[:top_k]]
            
        except Exception as e:
            print(f"重排序失败: {e}")
            return documents[:top_k]
    
    def _calculate_similarity(self, query: str, document: str) -> float:
        """计算简单的文本相似度"""
        try:
            query_words = set(query.lower().split())
            doc_words = set(document.lower().split())
            
            if not query_words or not doc_words:
                return 0.0
            
            intersection = len(query_words & doc_words)
            union = len(query_words | doc_words)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _get_collection_name(self, user_id: str, course_id: Optional[str],
                           lesson_num: Optional[str], search_mode: str) -> str:
        """获取集合名称"""
        if search_mode == "uploaded":
            return f"user_{user_id}_uploaded"
        else:
            return f"user_{user_id}_course_{course_id}_lesson_{lesson_num}"
    
    def _generate_cache_key(self, query: str, user_id: str, course_id: Optional[str],
                          lesson_num: Optional[str], search_mode: str, task_type: str) -> str:
        """生成缓存键"""
        return f"{hash(query)}_{user_id}_{course_id}_{lesson_num}_{search_mode}_{task_type}"
    
    async def get_lesson_content(self, user_id: str, course_id: str, lesson_num: str,
                                is_teacher: bool) -> Optional[str]:
        """获取课程内容"""
        try:
            # 获取用户路径
            user_path = self._get_user_path(user_id, is_teacher)
            
            # 尝试从向量数据库获取内容
            vector_db_path = os.path.join(user_path, course_id, lesson_num, "vector_kb")
            
            # 获取所有文档
            all_docs = await self._faiss_search("", vector_db_path, 100)  # 获取所有文档
            
            if all_docs:
                return "\n\n".join(all_docs)
            
            # 如果向量数据库没有内容，尝试从文件读取
            return self._read_files_from_folder(vector_db_path)
            
        except Exception as e:
            print(f"获取课程内容失败: {e}")
            return None
    
    async def enhance_content(self, content: str) -> str:
        """内容增强：基于知识库补充内容"""
        # 这里可以实现更复杂的内容增强逻辑
        # 例如：添加相关概念、补充背景知识等
        return content
    
    async def structure_content(self, content: str) -> str:
        """内容结构化：提取关键信息"""
        # 这里可以实现内容结构化逻辑
        # 例如：提取标题、重点、知识点等
        return content
    
    def _get_user_path(self, user_id: str, is_teacher: bool = False) -> str:
        """根据userID和isTeacher确定用户路径"""
        if is_teacher:
            base_dir = self.settings.TEACHERS_DIR
        else:
            base_dir = self.settings.STUDENTS_DIR
        return os.path.join(str(base_dir), user_id)
    
    def _read_files_from_folder(self, folder_path: str) -> Optional[str]:
        """从文件夹读取文件内容"""
        try:
            if not os.path.exists(folder_path):
                return None
            
            content_parts = []
            for filename in os.listdir(folder_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content_parts.append(f.read())
            
            return "\n\n".join(content_parts) if content_parts else None
            
        except Exception as e:
            print(f"读取文件失败: {e}")
            return None 