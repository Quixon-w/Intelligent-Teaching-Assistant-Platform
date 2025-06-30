# -*- coding: utf-8 -*-
"""
针对不同任务的Prompt模板
"""
from typing import List, Dict, Any, Optional


class PromptTemplates:
    """针对不同任务的Prompt模板"""
    
    @staticmethod
    def qa_prompt(query: str, retrieved_docs: List[str], context: Optional[Dict] = None) -> str:
        """问答Prompt模板"""
        # 清理检索文档中的相似度标记
        cleaned_docs = []
        for doc in retrieved_docs:
            if "[相似度:" in doc:
                import re
                cleaned_doc = re.sub(r'\[相似度: [0-9.]+ \]', '', doc)
                cleaned_doc = re.sub(r'\n\s*\n', '\n\n', cleaned_doc).strip()
                cleaned_docs.append(cleaned_doc)
            else:
                cleaned_docs.append(doc)
        
        # 合并检索文档
        context_text = "\n\n".join(cleaned_docs) if cleaned_docs else "未找到相关内容"
        
        # 基础Prompt
        prompt = f"""你是一个专业的教学助手。请基于以下知识内容，准确、完整地回答用户的问题。

知识内容：
{context_text}

用户问题：{query}

请基于上述知识内容，给出准确、完整、易于理解的回答。要求：
1. 回答要条理清晰，重点突出
2. 如果知识内容中没有相关信息，请明确说明
3. 不要直接复制知识内容，要用自己的话重新组织
4. 回答要简洁明了，避免冗余
5. 如果涉及专业术语，请适当解释

回答："""
        
        # 如果有历史上下文，添加到Prompt中
        if context and context.get('conversation_history'):
            history_text = "\n\n历史对话：\n"
            for i, conv in enumerate(context['conversation_history'][-3:]):  # 只使用最近3个对话
                history_text += f"问题{i+1}: {conv.get('query', '')}\n"
                history_text += f"回答{i+1}: {conv.get('answer', '')[:200]}...\n\n"
            
            # 在知识内容之前插入历史记录
            prompt = f"""你是一个专业的教学助手。请基于以下知识内容和历史对话记录，准确、完整地回答用户的问题。

{history_text}知识内容：
{context_text}

用户问题：{query}

请基于上述知识内容和历史对话记录，给出准确、完整、易于理解的回答。要求：
1. 回答要条理清晰，重点突出
2. 如果知识内容中没有相关信息，请明确说明
3. 不要直接复制知识内容，要用自己的话重新组织
4. 回答要简洁明了，避免冗余
5. 如果涉及专业术语，请适当解释
6. 注意与历史对话的连贯性

回答："""
        
        return prompt
    
    @staticmethod
    def exercise_prompt(content: str, difficulty: str, count: int) -> str:
        """习题生成Prompt模板"""
        difficulty_map = {
            "easy": "简单",
            "medium": "中等", 
            "hard": "困难"
        }
        
        difficulty_text = difficulty_map.get(difficulty, "中等")
        
        return f"""请基于以下教学内容，生成{difficulty_text}难度的{count}道选择题。

教学内容：
{content[:3000]}  # 限制内容长度，避免token过多

要求：
1. 题目难度符合{difficulty_text}级别
2. 每道题包含4个选项，其中1个正确答案
3. 题目要覆盖教学内容的主要知识点
4. 提供详细的解析说明
5. 题目格式规范，便于理解
6. 选项要合理，避免明显错误选项

请按照以下格式生成{count}道选择题：

题目1：[题干]
A. [选项A]
B. [选项B] 
C. [选项C]
D. [选项D]
正确答案：[A/B/C/D]
解析：[详细解析]

题目2：[题干]
...

请生成{count}道选择题："""
    
    @staticmethod
    def outline_prompt(content: str, max_words: int) -> str:
        """大纲生成Prompt模板"""
        return f"""请根据以下教学内容，生成一个详细的教学大纲。

教学内容：
{content[:2000]}  # 限制内容长度，避免token过多

要求：
1. 结构清晰，层次分明，使用数字编号（如1.1、1.2、2.1等）
2. 包含主要知识点和重点内容
3. 适合教学使用，内容完整
4. 字数控制在{max_words}字左右
5. 确保每个部分都有完整的描述
6. 大纲应该包含：教学目标、重点难点、教学内容、教学方法等
7. 使用中文编写，语言简洁明了

请生成完整的教学大纲，确保内容完整且结构清晰：

教学大纲："""
    
    @staticmethod
    def chat_prompt(query: str, context: Optional[Dict] = None) -> str:
        """普通对话Prompt模板"""
        base_prompt = f"""你是一个友好的AI助手，请回答用户的问题。

用户问题：{query}

请给出准确、有帮助的回答。要求：
1. 回答要准确、有用
2. 语言要友好、自然
3. 如果不知道答案，请诚实说明
4. 回答要简洁明了

回答："""
        
        # 如果有历史上下文，添加到Prompt中
        if context and context.get('conversation_history'):
            history_text = "\n\n历史对话：\n"
            for i, conv in enumerate(context['conversation_history'][-3:]):  # 只使用最近3个对话
                history_text += f"用户{i+1}: {conv.get('query', '')}\n"
                history_text += f"助手{i+1}: {conv.get('answer', '')[:200]}...\n\n"
            
            base_prompt = f"""你是一个友好的AI助手，请基于历史对话记录回答用户的问题。

{history_text}用户问题：{query}

请基于历史对话记录，给出准确、有帮助的回答。要求：
1. 回答要准确、有用
2. 语言要友好、自然
3. 如果不知道答案，请诚实说明
4. 回答要简洁明了
5. 注意与历史对话的连贯性

回答："""
        
        return base_prompt
    
    @staticmethod
    def summary_prompt(content: str, max_length: int = 500) -> str:
        """内容总结Prompt模板"""
        return f"""请对以下内容进行总结。

内容：
{content[:1500]}  # 限制内容长度

要求：
1. 总结要准确、完整
2. 突出主要内容要点
3. 字数控制在{max_length}字以内
4. 语言简洁明了
5. 保持逻辑结构清晰

总结："""
    
    @staticmethod
    def keyword_extraction_prompt(content: str) -> str:
        """关键词提取Prompt模板"""
        return f"""请从以下内容中提取关键词。

内容：
{content[:1000]}  # 限制内容长度

要求：
1. 提取5-10个最重要的关键词
2. 关键词要准确反映内容主题
3. 包括专业术语和重要概念
4. 按重要性排序
5. 用逗号分隔

关键词："""
    
    @staticmethod
    def question_generation_prompt(content: str, question_type: str = "multiple_choice", count: int = 5) -> str:
        """问题生成Prompt模板"""
        type_map = {
            "multiple_choice": "选择题",
            "true_false": "判断题",
            "short_answer": "简答题",
            "essay": "论述题"
        }
        
        question_type_text = type_map.get(question_type, "选择题")
        
        return f"""请基于以下内容生成{count}道{question_type_text}。

内容：
{content[:2000]}  # 限制内容长度

要求：
1. 问题要覆盖内容的主要知识点
2. 问题要清晰、准确
3. 如果是选择题，提供4个选项
4. 如果是判断题，提供正确答案和解析
5. 如果是简答题或论述题，提供参考答案
6. 问题难度要适中

请生成{count}道{question_type_text}：""" 