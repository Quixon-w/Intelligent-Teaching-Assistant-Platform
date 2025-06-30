# -*- coding: utf-8 -*-
"""
智能上下文管理
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class ContextManager:
    """智能上下文管理"""
    
    def __init__(self, max_context_length: int = 2000, max_history_turns: int = 5):
        self.contexts = {}  # session_id -> context
        self.max_context_length = max_context_length
        self.max_history_turns = max_history_turns
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """获取会话上下文"""
        if session_id not in self.contexts:
            self.contexts[session_id] = {
                'conversation_history': [],
                'retrieved_docs': [],
                'current_topic': None,
                'last_update': datetime.now().isoformat()
            }
        return self.contexts[session_id]
    
    def update_context(self, session_id: str, query: str, answer: str, 
                      retrieved_docs: List[str] = None):
        """更新上下文"""
        context = self.get_context(session_id)
        
        # 1. 添加对话历史
        conversation_entry = {
            'query': query,
            'answer': answer,
            'timestamp': datetime.now().isoformat(),
            'retrieved_docs': retrieved_docs or []
        }
        
        context['conversation_history'].append(conversation_entry)
        
        # 2. 更新检索文档
        if retrieved_docs:
            context['retrieved_docs'].extend(retrieved_docs)
        
        # 3. 智能压缩上下文
        self._compress_context(context)
        
        # 4. 更新最后修改时间
        context['last_update'] = datetime.now().isoformat()
    
    def _compress_context(self, context: Dict[str, Any]):
        """智能压缩上下文，避免token浪费"""
        # 1. 限制对话历史长度
        if len(context['conversation_history']) > self.max_history_turns:
            # 保留最近的对话
            context['conversation_history'] = context['conversation_history'][-self.max_history_turns:]
        
        # 2. 限制检索文档数量
        if len(context['retrieved_docs']) > 10:
            # 保留最近的检索文档
            context['retrieved_docs'] = context['retrieved_docs'][-10:]
        
        # 3. 计算上下文总长度
        total_length = self._calculate_context_length(context)
        
        # 4. 如果超过最大长度，进行压缩
        if total_length > self.max_context_length:
            self._compress_context_content(context)
    
    def _calculate_context_length(self, context: Dict[str, Any]) -> int:
        """计算上下文总长度"""
        total_length = 0
        
        # 计算对话历史长度
        for conv in context['conversation_history']:
            total_length += len(conv.get('query', ''))
            total_length += len(conv.get('answer', ''))
        
        # 计算检索文档长度
        for doc in context['retrieved_docs']:
            total_length += len(doc)
        
        return total_length
    
    def _compress_context_content(self, context: Dict[str, Any]):
        """压缩上下文内容"""
        # 1. 压缩对话历史
        for conv in context['conversation_history']:
            if len(conv.get('query', '')) > 200:
                conv['query'] = conv['query'][:200] + "..."
            if len(conv.get('answer', '')) > 500:
                conv['answer'] = conv['answer'][:500] + "..."
        
        # 2. 压缩检索文档
        compressed_docs = []
        for doc in context['retrieved_docs']:
            if len(doc) > 300:
                compressed_docs.append(doc[:300] + "...")
            else:
                compressed_docs.append(doc)
        
        context['retrieved_docs'] = compressed_docs
    
    def get_relevant_context(self, session_id: str, current_query: str = None) -> Dict[str, Any]:
        """获取相关上下文"""
        context = self.get_context(session_id)
        
        # 如果没有当前查询，返回完整上下文
        if not current_query:
            return context
        
        # 基于当前查询筛选相关上下文
        relevant_context = {
            'conversation_history': [],
            'retrieved_docs': [],
            'current_topic': context.get('current_topic'),
            'last_update': context.get('last_update')
        }
        
        # 筛选相关的对话历史
        for conv in context['conversation_history']:
            if self._is_relevant(current_query, conv.get('query', '')):
                relevant_context['conversation_history'].append(conv)
        
        # 筛选相关的检索文档
        for doc in context['retrieved_docs']:
            if self._is_relevant(current_query, doc):
                relevant_context['retrieved_docs'].append(doc)
        
        return relevant_context
    
    def _is_relevant(self, query: str, text: str) -> bool:
        """判断文本是否与查询相关"""
        try:
            query_words = set(query.lower().split())
            text_words = set(text.lower().split())
            
            if not query_words or not text_words:
                return False
            
            # 计算词汇重叠度
            overlap = len(query_words & text_words)
            overlap_ratio = overlap / len(query_words)
            
            return overlap_ratio > 0.3  # 30%的重叠度阈值
            
        except Exception:
            return False
    
    def clear_context(self, session_id: str):
        """清除会话上下文"""
        if session_id in self.contexts:
            del self.contexts[session_id]
    
    def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """获取上下文摘要"""
        context = self.get_context(session_id)
        
        return {
            'session_id': session_id,
            'conversation_count': len(context['conversation_history']),
            'doc_count': len(context['retrieved_docs']),
            'current_topic': context.get('current_topic'),
            'last_update': context.get('last_update'),
            'context_length': self._calculate_context_length(context)
        }
    
    def update_topic(self, session_id: str, topic: str):
        """更新当前话题"""
        context = self.get_context(session_id)
        context['current_topic'] = topic
        context['last_update'] = datetime.now().isoformat()
    
    def get_all_sessions(self) -> List[str]:
        """获取所有会话ID"""
        return list(self.contexts.keys())
    
    def cleanup_old_contexts(self, max_age_hours: int = 24):
        """清理过期的上下文"""
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, context in self.contexts.items():
            last_update = datetime.fromisoformat(context.get('last_update', '1970-01-01T00:00:00'))
            age_hours = (current_time - last_update).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self.clear_context(session_id)
        
        return len(sessions_to_remove) 