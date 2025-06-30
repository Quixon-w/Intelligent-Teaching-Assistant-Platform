# -*- coding: utf-8 -*-
"""
统一的RAG服务，支持多种任务类型
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from .retriever import HybridRetriever
from .context_manager import ContextManager
from .prompt_templates import PromptTemplates
from ..llm.rwkv_service import RWKVService


class RAGService:
    """统一的RAG服务，支持多种任务类型"""
    
    def __init__(self):
        self.retriever = HybridRetriever()
        self.context_manager = ContextManager()
        self.llm_service = RWKVService()
        self.prompt_templates = PromptTemplates()
    
    async def process_qa(self, query: str, user_id: str, session_id: str, 
                        course_id: Optional[str] = None, lesson_num: Optional[str] = None,
                        search_mode: str = "existing", top_k: int = 3, 
                        use_context: bool = True, **kwargs) -> Dict[str, Any]:
        """知识库问答"""
        try:
            # 1. 获取上下文
            context = None
            if use_context:
                context = self.context_manager.get_context(session_id)
            
            # 2. 混合检索
            retrieved_docs = await self.retriever.retrieve(
                query=query,
                user_id=user_id,
                course_id=course_id,
                lesson_num=lesson_num,
                search_mode=search_mode,
                context=context,
                task_type="qa",
                top_k=top_k,
                **kwargs
            )
            
            if not retrieved_docs:
                return {
                    "success": True,
                    "answer": "抱歉，我在当前知识库中没有找到与您问题相关的信息。请尝试重新表述您的问题，或者检查是否选择了正确的课程和课时。",
                    "context": "未找到相关内容",
                    "has_context": False,
                    "use_context": use_context
                }
            
            # 3. 构建Prompt
            prompt = self.prompt_templates.qa_prompt(query, retrieved_docs, context)
            
            # 4. 生成回答
            answer = await self.llm_service.generate(prompt, **kwargs)
            
            # 5. 更新上下文
            if use_context:
                self.context_manager.update_context(session_id, query, answer, retrieved_docs)
            
            return {
                "success": True,
                "answer": answer,
                "context": retrieved_docs,
                "has_context": True,
                "use_context": use_context
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": "抱歉，处理您的问题时出现了错误，请稍后重试。"
            }
    
    async def process_exercise(self, user_id: str, course_id: str, lesson_num: str,
                              question_count: int = 5, difficulty: str = "medium",
                              is_teacher: bool = False, **kwargs) -> Dict[str, Any]:
        """习题生成"""
        try:
            # 1. 获取课程内容
            content = await self.retriever.get_lesson_content(
                user_id, course_id, lesson_num, is_teacher
            )
            
            if not content:
                return {
                    "success": False,
                    "error": "未找到课程内容",
                    "data": None
                }
            
            # 2. 内容增强
            enhanced_content = await self.retriever.enhance_content(content)
            
            # 3. 构建习题生成Prompt
            prompt = self.prompt_templates.exercise_prompt(
                enhanced_content, difficulty, question_count
            )
            
            # 4. 生成习题
            exercises = await self.llm_service.generate(prompt, **kwargs)
            
            return {
                "success": True,
                "data": exercises,
                "total_count": question_count,
                "difficulty": difficulty
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def process_outline(self, user_id: str, course_id: str, lesson_num: str,
                             max_words: int = 1000, is_teacher: bool = False,
                             **kwargs) -> Dict[str, Any]:
        """大纲生成"""
        try:
            # 1. 获取课程内容
            content = await self.retriever.get_lesson_content(
                user_id, course_id, lesson_num, is_teacher
            )
            
            if not content:
                return {
                    "success": False,
                    "error": "未找到课程内容",
                    "outline": None
                }
            
            # 2. 内容结构化
            structured_content = await self.retriever.structure_content(content)
            
            # 3. 构建大纲生成Prompt
            prompt = self.prompt_templates.outline_prompt(
                structured_content, max_words
            )
            
            # 4. 生成大纲
            outline = await self.llm_service.generate(prompt, **kwargs)
            
            return {
                "success": True,
                "outline": outline,
                "max_words": max_words
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "outline": None
            }
    
    async def process_chat(self, query: str, user_id: str, session_id: str,
                          use_context: bool = True, **kwargs) -> Dict[str, Any]:
        """普通对话（不使用知识库）"""
        try:
            # 1. 获取上下文
            context = None
            if use_context:
                context = self.context_manager.get_context(session_id)
            
            # 2. 构建对话Prompt
            prompt = self.prompt_templates.chat_prompt(query, context)
            
            # 3. 生成回答
            answer = await self.llm_service.generate(prompt, **kwargs)
            
            # 4. 更新上下文
            if use_context:
                self.context_manager.update_context(session_id, query, answer, [])
            
            return {
                "success": True,
                "answer": answer,
                "use_context": use_context
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": "抱歉，处理您的问题时出现了错误，请稍后重试。"
            } 