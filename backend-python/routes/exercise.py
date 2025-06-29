# -*- coding: utf-8 -*-
import os
import json
import pickle
import faiss
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Union, Optional, List, Dict, Any
import asyncio
from threading import Lock
from datetime import datetime
import random

from utils.rwkv import *
import global_var
from config.settings import get_settings

router = APIRouter()

# 全局锁，用于控制并发请求
exercise_lock = Lock()


class ExerciseBody(BaseModel):
    user_id: str = Field(..., description="用户ID，用于确定存储路径")
    session_id: str = Field(..., description="会话ID")
    course_id: str = Field(..., description="课程ID")
    lesson_num: str = Field(..., description="课时号，必填")
    is_teacher: bool = Field(False, description="是否为教师用户")
    question_count: int = Field(5, description="生成题目数量", ge=1, le=20)
    difficulty: str = Field("medium", description="题目难度：easy(简单)、medium(中等)、hard(困难)")
    max_tokens: int = Field(2000, description="生成回答的最大token数", ge=500, le=4000)
    temperature: float = Field(0.7, description="生成温度", ge=0.1, le=1.0)
    generation_mode: str = Field("block", description="生成模式：block(按文本块生成)、whole(整体内容生成)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "teacher123",
                "session_id": "session456",
                "course_id": "math101",
                "lesson_num": "lesson01",
                "is_teacher": True,
                "question_count": 5,
                "difficulty": "medium",
                "max_tokens": 2000,
                "temperature": 0.7,
                "generation_mode": "block"
            }
        }
    }


class ExerciseQuestion(BaseModel):
    question_id: str = Field(..., description="题目ID")
    question_text: str = Field(..., description="题干")
    options: List[str] = Field(..., description="选项列表")
    correct_answer: str = Field(..., description="正确答案")
    explanation: str = Field(..., description="解析")
    knowledge_point: str = Field(..., description="所属知识点")
    difficulty: str = Field(..., description="难度等级")


class ExerciseResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[str] = Field(None, description="生成的习题原始文本")
    total_count: int = Field(0, description="生成的题目总数")
    generation_time: float = Field(0.0, description="生成耗时(秒)")


def get_user_path(user_id: str, is_teacher: bool) -> str:
    """根据userID和isTeacher确定用户路径"""
    settings = get_settings()
    if is_teacher:
        base_dir = settings.TEACHERS_DIR
    else:
        base_dir = settings.STUDENTS_DIR
    return os.path.join(str(base_dir), user_id)


def extract_text_blocks_from_faiss_db(db_path: str) -> List[str]:
    """
    从FAISS向量数据库中提取文本块列表
    """
    print(f"正在从FAISS数据库提取文本块: {db_path}")
    
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
        
        # 提取文本块
        text_blocks = []
        
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
                            try:
                                content = doc.page_content
                                if isinstance(content, bytes):
                                    content = content.decode('utf-8', errors='ignore')
                                if content.strip():
                                    text_blocks.append(content)
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
                                if content.strip():
                                    text_blocks.append(content)
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
                                                if content.strip():
                                                    text_blocks.append(content)
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
        
        if text_blocks:
            print(f"成功提取 {len(text_blocks)} 个文本块")
            return text_blocks
        else:
            print("未找到可提取的文本内容")
            return None
            
    except Exception as e:
        print(f"从FAISS数据库提取文本时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_lesson_content(user_id: str, course_id: str, lesson_num: str, is_teacher: bool):
    """
    获取课时内容，优先从FAISS向量数据库获取，如果失败则从文件获取
    返回文本块列表而不是合并的文本
    """
    print(f"正在获取课时内容: userID={user_id}, courseId={course_id}, lessonNum={lesson_num}, isTeacher={is_teacher}")
    
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 首先尝试从FAISS向量数据库获取内容
    vector_db_path = os.path.join(user_path, course_id, lesson_num, "vector_kb")
    print(f"尝试从向量数据库获取课时内容: {vector_db_path}")
    
    text_blocks = extract_text_blocks_from_faiss_db(vector_db_path)
    if text_blocks:
        print("成功从向量数据库获取课时内容")
        return text_blocks
    
    # 如果向量数据库获取失败，回退到文件读取方式
    print("向量数据库获取失败，回退到文件读取方式")
    
    # 构建文件路径
    lesson_path = os.path.join(user_path, course_id, lesson_num)
    if not os.path.exists(lesson_path):
        print(f"课时路径不存在: {lesson_path}")
        return None
    
    # 读取课时文件夹中的所有文件
    text_blocks = read_files_as_blocks(lesson_path)
    if text_blocks:
        print("成功从文件获取课时内容")
        return text_blocks
    
    print("无法获取课时内容")
    return None


def get_lesson_content_whole(user_id: str, course_id: str, lesson_num: str, is_teacher: bool) -> str:
    """
    获取课时内容，返回合并的文本内容
    """
    print(f"正在获取课时内容: userID={user_id}, courseId={course_id}, lessonNum={lesson_num}, isTeacher={is_teacher}")
    
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 首先尝试从FAISS向量数据库获取内容
    vector_db_path = os.path.join(user_path, course_id, lesson_num, "vector_kb")
    print(f"尝试从向量数据库获取课时内容: {vector_db_path}")
    
    text_blocks = extract_text_blocks_from_faiss_db(vector_db_path)
    if text_blocks:
        print("成功从向量数据库获取课时内容")
        # 合并文本块
        combined_content = "\n\n".join(text_blocks)
        return combined_content
    
    # 如果向量数据库获取失败，回退到文件读取方式
    print("向量数据库获取失败，回退到文件读取方式")
    
    # 构建文件路径
    lesson_path = os.path.join(user_path, course_id, lesson_num)
    if not os.path.exists(lesson_path):
        print(f"课时路径不存在: {lesson_path}")
        return None
    
    # 读取课时文件夹中的所有文件
    text_blocks = read_files_as_blocks(lesson_path)
    if text_blocks:
        print("成功从文件获取课时内容")
        # 合并文本块
        combined_content = "\n\n".join(text_blocks)
        return combined_content
    
    print("无法获取课时内容")
    return None


def read_files_as_blocks(folder_path: str) -> List[str]:
    """
    读取文件夹中的所有文本文件内容，返回文本块列表
    """
    print(f"正在读取文件夹内容: {folder_path}")
    
    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        return None
    
    text_blocks = []
    supported_extensions = ['.txt', '.md', '.docx', '.pdf']
    
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # 跳过目录和隐藏文件
            if os.path.isdir(file_path) or filename.startswith('.'):
                continue
            
            # 检查文件扩展名
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in supported_extensions:
                continue
            
            try:
                if file_ext == '.txt' or file_ext == '.md':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            # 按段落分割文本块
                            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                            text_blocks.extend(paragraphs)
                            print(f"成功读取文件: {filename}，分割为 {len(paragraphs)} 个文本块")
                # 对于其他格式的文件，可以添加相应的处理逻辑
                
            except Exception as e:
                print(f"读取文件 {filename} 时出错: {e}")
                continue
        
        if text_blocks:
            print(f"成功读取 {len(text_blocks)} 个文本块")
            return text_blocks
        else:
            print("未找到可读取的文本文件")
            return None
            
    except Exception as e:
        print(f"读取文件夹时出错: {e}")
        return None


def generate_exercise_prompt_for_block(content: str, block_index: int, difficulty: str) -> str:
    """
    为单个文本块生成习题的提示词
    """
    difficulty_map = {
        "easy": "简单",
        "medium": "中等", 
        "hard": "困难"
    }
    
    difficulty_text = difficulty_map.get(difficulty, "中等")
    
    prompt = f"""基于以下内容生成一道{difficulty_text}难度的单选题：

{content}

严格按照以下格式生成，不要添加任何其他内容：

题目：
题干：[题干内容]
A. [选项A]
B. [选项B] 
C. [选项C]
D. [选项D]
正确答案：[A/B/C/D]
解析：[详细解析为什么选择正确答案]
所属知识点：[所属知识点]"""

    return prompt


async def generate_exercises_for_blocks(text_blocks: List[str], request: Request, max_tokens: int, temperature: float, difficulty: str) -> List[str]:
    """
    为每个文本块生成一道习题
    """
    print(f"开始为 {len(text_blocks)} 个文本块生成习题...")
    
    exercises = []
    
    for i, block in enumerate(text_blocks):
        print(f"正在为文本块 {i+1}/{len(text_blocks)} 生成习题...")
        
        try:
            # 为当前文本块生成提示词
            prompt = generate_exercise_prompt_for_block(block, i, difficulty)
            
            # 生成习题
            exercise = await generate_exercises_with_rwkv(
                prompt, 
                request, 
                max_tokens, 
                temperature
            )
            
            exercises.append(exercise)
            print(f"文本块 {i+1} 习题生成完成")
            
        except Exception as e:
            print(f"为文本块 {i+1} 生成习题时出错: {e}")
            # 如果某个文本块生成失败，添加错误信息
            exercises.append(f"题目{i+1}生成失败: {str(e)}")
    
    return exercises


def generate_exercise_prompt(content: str, question_count: int, difficulty: str) -> str:
    """
    生成习题的提示词
    """
    difficulty_map = {
        "easy": "简单",
        "medium": "中等", 
        "hard": "困难"
    }
    
    difficulty_text = difficulty_map.get(difficulty, "中等")
    
    prompt = f"""基于以下内容生成{question_count}道{difficulty_text}难度的单选题：

{content}

严格按照以下格式生成，不要添加任何其他内容：

题目1：
题干：[题干内容]
A. [选项A]
B. [选项B] 
C. [选项C]
D. [选项D]
正确答案：[A/B/C/D]
解析：[详细解析为什么选择正确答案]
所属知识点：[所属知识点]

题目2：
题干：[题干内容]
A. [选项A]
B. [选项B]
C. [选项C]
D. [选项D]
正确答案：[A/B/C/D]
解析：[详细解析为什么选择正确答案]
所属知识点：[所属知识点]

[继续生成剩余题目，必须生成{question_count}道题目，每道题都要完整包含题干、选项、正确答案、解析和知识点]"""

    return prompt


def save_exercises_to_file(user_id: str, course_id: str, lesson_num: str, exercises: List[Dict], is_teacher: bool) -> dict:
    """
    将生成的习题保存到文件
    """
    print(f"正在保存习题到文件: userID={user_id}, courseId={course_id}, lessonNum={lesson_num}")
    
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 构建保存路径
    lesson_path = os.path.join(user_path, course_id, lesson_num)
    exercises_dir = os.path.join(lesson_path, "exercises")
    
    # 创建习题目录
    os.makedirs(exercises_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exercises_{timestamp}.json"
    file_path = os.path.join(exercises_dir, filename)
    
    try:
        # 准备保存的数据
        save_data = {
            "metadata": {
                "user_id": user_id,
                "course_id": course_id,
                "lesson_num": lesson_num,
                "is_teacher": is_teacher,
                "generated_at": datetime.now().isoformat(),
                "total_questions": len(exercises),
                "difficulty": exercises[0]["difficulty"] if exercises else "medium"
            },
            "exercises": exercises
        }
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"习题已保存到: {file_path}")
        
        return {
            "success": True,
            "file_path": file_path,
            "filename": filename,
            "total_questions": len(exercises)
        }
        
    except Exception as e:
        print(f"保存习题文件时出错: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def generate_exercises_with_rwkv(prompt: str, request: Request, max_tokens: int, temperature: float):
    """
    使用RWKV模型生成习题
    """
    print("开始使用RWKV模型生成习题...")
    
    try:
        # 获取RWKV模型实例
        model = global_var.get(global_var.Model)
        if model is None:
            raise Exception("RWKV模型未初始化")
        
        # 设置生成参数
        model.temperature = temperature
        model.top_p = 0.9
        
        # 生成回答内容
        answer_content = ""
        token_count = 0
        
        print("开始生成习题...")
        print(f"提示词长度: {len(prompt)} 字符")
        print(f"最大token数: {max_tokens}")
        print(f"温度参数: {temperature}")
        
        # 移除所有停止条件，让模型完整生成
        stop_sequences = []
        
        print("开始生成循环...")
        for response, delta, _, _ in model.generate(prompt, stop=stop_sequences):
            answer_content += delta
            token_count += 1
            
            # 每100个token打印一次进度
            if token_count % 100 == 0:
                print(f"已生成 {token_count} tokens, 当前内容长度: {len(answer_content)} 字符")
            
            # 检查请求是否断开
            if await request.is_disconnected():
                print("请求已断开")
                break
            
            # 检查是否达到最大token数
            if token_count >= max_tokens:
                print(f"达到最大token数: {max_tokens}")
                break
        
        print(f"习题生成完成，生成长度: {len(answer_content)} 字符")
        print(f"实际生成token数: {token_count}")
        print(f"内容预览: {answer_content[:200]}...")
        
        # 清理生成的内容
        cleaned_content = clean_generated_content(answer_content)
        
        # 如果生成的内容太短，给出警告
        if len(cleaned_content) < 100:
            print("⚠️ 警告：生成的内容过短，可能存在问题")
        
        return cleaned_content
        
    except Exception as e:
        print(f"RWKV生成习题时出错: {e}")
        raise e


def clean_generated_content(content: str) -> str:
    """
    清理生成的内容，移除不相关的部分
    """
    print("开始清理生成内容...")
    
    # 移除常见的无关前缀
    prefixes_to_remove = [
        "好的，我会根据题目要求继续生成",
        "好的，我可以为您生成",
        "好的，我会为您生成",
        "Assistant:",
        "好的，",
        "我会",
        "我将",
        "请注意，",
        "这些题目需要涵盖",
        "基于以上内容，",
    ]
    
    cleaned = content.strip()
    
    # 移除前缀
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    
    # 查找第一个题目开始的位置
    import re
    
    # 查找题目编号模式
    question_patterns = [
        r'题目\d*：',
        r'\d+\.\s*\*\*',
        r'\d+\.\s*',
    ]
    
    start_pos = -1
    for pattern in question_patterns:
        match = re.search(pattern, cleaned)
        if match:
            start_pos = match.start()
            break
    
    if start_pos > 0:
        cleaned = cleaned[start_pos:]
    
    # 移除不相关的内容（如Question:, Answer:等）
    lines = cleaned.split('\n')
    filtered_lines = []
    skip_mode = False
    
    for line in lines:
        line = line.strip()
        
        # 跳过不相关的内容
        if any(keyword in line for keyword in ['Question:', 'Answer:', '##', '###', 'FIFO', 'SJF', '轮询调度器']):
            skip_mode = True
            continue
        
        # 如果遇到新的题目，停止跳过模式
        if re.match(r'题目\d*：', line) or re.match(r'\d+\.\s*\*\*', line):
            skip_mode = False
        
        if not skip_mode:
            filtered_lines.append(line)
    
    cleaned = '\n'.join(filtered_lines)
    
    print(f"清理后内容长度: {len(cleaned)} 字符")
    return cleaned.strip()


async def generate_with_rwkv_retry(prompt: str, request: Request, max_tokens: int, model, generation_config):
    """
    带重试机制的RWKV生成
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"RWKV生成尝试 {retry_count + 1}/{max_retries}")
            
            # 设置模型参数
            model.temperature = generation_config.get("temperature", 0.7)
            model.top_p = generation_config.get("top_p", 0.9)
            
            # 生成回答内容
            answer_content = ""
            token_count = 0
            
            # 停止条件
            stop_sequences = generation_config.get("stop", ["\n\n", "```", "---"])
            
            for response, delta, _, _ in model.generate(prompt, stop=stop_sequences):
                answer_content += delta
                token_count += 1
                
                # 检查请求是否断开
                if await request.is_disconnected():
                    print("请求已断开")
                    break
                
                # 检查是否达到最大token数
                if token_count >= max_tokens:
                    print(f"达到最大token数: {max_tokens}")
                    break
            
            # 尝试解析JSON
            try:
                # 查找JSON内容
                start_idx = answer_content.find('{')
                end_idx = answer_content.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = answer_content[start_idx:end_idx]
                    json.loads(json_str)  # 验证JSON格式
                    print("JSON格式验证成功")
                    return {"content": answer_content}
                else:
                    print("未找到有效的JSON内容")
                    raise Exception("JSON格式无效")
                    
            except json.JSONDecodeError as json_error:
                print(f"JSON解析失败: {json_error}")
                if retry_count < max_retries - 1:
                    retry_count += 1
                    continue
                else:
                    raise Exception(f"JSON格式错误: {json_error}")
            
        except Exception as e:
            print(f"RWKV生成出错: {e}")
            if retry_count < max_retries - 1:
                retry_count += 1
                await asyncio.sleep(1)  # 等待1秒后重试
                continue
            else:
                raise e
    
    raise Exception("RWKV生成失败，已达到最大重试次数")


def parse_exercises_from_response(response_text: str) -> List[Dict]:
    """
    从RWKV响应中解析习题数据
    """
    print("正在解析习题响应...")
    print(f"原始响应内容: {response_text}")
    
    try:
        # 查找JSON内容
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx <= start_idx:
            raise Exception("未找到有效的JSON内容")
        
        json_str = response_text[start_idx:end_idx]
        print(f"提取的JSON字符串: {json_str}")
        
        # 尝试清理JSON字符串
        json_str = clean_json_string(json_str)
        print(f"清理后的JSON字符串: {json_str}")
        
        data = json.loads(json_str)
        
        if "questions" not in data:
            raise Exception("响应中缺少questions字段")
        
        questions = data["questions"]
        if not isinstance(questions, list):
            raise Exception("questions字段不是列表格式")
        
        # 验证每个题目的格式
        parsed_questions = []
        for i, question in enumerate(questions):
            if not isinstance(question, dict):
                print(f"跳过无效题目 {i}: 不是字典格式")
                continue
            
            # 检查必需字段
            required_fields = ["question_text", "options", "correct_answer", "explanation", "knowledge_point"]
            missing_fields = [field for field in required_fields if field not in question]
            
            if missing_fields:
                print(f"跳过题目 {i}: 缺少字段 {missing_fields}")
                continue
            
            # 生成题目ID
            question_id = question.get("question_id", f"q{i+1}")
            
            # 验证选项格式
            options = question["options"]
            if not isinstance(options, list) or len(options) != 4:
                print(f"跳过题目 {i}: 选项格式不正确")
                continue
            
            # 验证正确答案
            correct_answer = question["correct_answer"]
            if correct_answer not in ["A", "B", "C", "D"]:
                print(f"跳过题目 {i}: 正确答案格式不正确")
                continue
            
            # 构建标准化的题目对象
            parsed_question = {
                "question_id": question_id,
                "question_text": question["question_text"],
                "options": options,
                "correct_answer": correct_answer,
                "explanation": question["explanation"],
                "knowledge_point": question["knowledge_point"],
                "difficulty": question.get("difficulty", "medium")
            }
            
            parsed_questions.append(parsed_question)
            print(f"成功解析题目 {i+1}: {question_id}")
        
        print(f"成功解析 {len(parsed_questions)} 道题目")
        return parsed_questions
        
    except Exception as e:
        print(f"解析习题响应时出错: {e}")
        raise e


def clean_json_string(json_str: str) -> str:
    """
    清理JSON字符串，修复常见的格式问题
    """
    # 移除可能的BOM标记和多余空白
    json_str = json_str.strip()
    
    # 修复可能的换行符问题
    json_str = json_str.replace('\n', '\\n').replace('\r', '\\r')
    
    # 修复可能的制表符问题
    json_str = json_str.replace('\t', '\\t')
    
    # 修复多余的逗号（在数组或对象结束前）
    json_str = json_str.replace(',}', '}').replace(',]', ']')
    
    return json_str


@router.post("/v1/exercise/generate", tags=["Exercise"], response_model=ExerciseResponse)
async def generate_exercises(body: ExerciseBody, request: Request):
    """
    根据课时知识库内容生成课后习题，支持两种生成模式
    """
    start_time = datetime.now()
    
    print(f"开始生成习题: userID={body.user_id}, courseId={body.course_id}, lessonNum={body.lesson_num}")
    print(f"参数: questionCount={body.question_count}, difficulty={body.difficulty}, generationMode={body.generation_mode}")
    
    # 检查并发锁
    if exercise_lock.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="系统繁忙，请稍后重试"
        )
    
    try:
        with exercise_lock:
            if body.generation_mode == "whole":
                # 整体内容生成模式
                print("使用整体内容生成模式")
                
                # 1. 获取合并的课时内容
                print("步骤1: 获取课时内容")
                lesson_content = get_lesson_content_whole(
                    body.user_id, 
                    body.course_id, 
                    body.lesson_num, 
                    body.is_teacher
                )
                
                if not lesson_content:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="无法获取课时内容，请确保课时已上传并处理完成"
                    )
                
                print(f"课时内容长度: {len(lesson_content)} 字符")
                
                # 2. 生成提示词
                print("步骤2: 生成提示词")
                prompt = generate_exercise_prompt(
                    lesson_content, 
                    body.question_count, 
                    body.difficulty
                )
                
                # 3. 使用RWKV生成习题
                print("步骤3: 使用RWKV生成习题")
                response_text = await generate_exercises_with_rwkv(
                    prompt, 
                    request, 
                    body.max_tokens, 
                    body.temperature
                )
                
                # 4. 返回结果
                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()
                
                response = ExerciseResponse(
                    success=True,
                    message=f"习题生成完成，共生成 {body.question_count} 道题目",
                    data=response_text,
                    total_count=body.question_count,
                    generation_time=generation_time
                )
                print(f"习题生成完成，耗时: {generation_time:.2f}秒")
                return response
                
            else:
                # 文本块生成模式（默认）
                print("使用文本块生成模式")
                
                # 1. 获取课时内容（文本块列表）
                print("步骤1: 获取课时内容")
                text_blocks = get_lesson_content(
                    body.user_id, 
                    body.course_id, 
                    body.lesson_num, 
                    body.is_teacher
                )
                
                if not text_blocks:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="无法获取课时内容，请确保课时已上传并处理完成"
                    )
                
                print(f"获取到 {len(text_blocks)} 个文本块")
                
                # 2. 限制文本块数量，避免生成过多题目
                max_blocks = min(body.question_count, len(text_blocks))
                selected_blocks = text_blocks[:max_blocks]
                
                print(f"将使用前 {max_blocks} 个文本块生成习题")
                
                # 3. 为每个文本块生成一道习题
                print("步骤2: 为每个文本块生成习题")
                exercises = await generate_exercises_for_blocks(
                    selected_blocks,
                    request,
                    body.max_tokens,
                    body.temperature,
                    body.difficulty
                )
                
                # 4. 合并所有习题
                combined_exercises = "\n\n" + "="*50 + "\n\n".join(exercises)
                
                # 5. 返回结果
                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()
                
                response = ExerciseResponse(
                    success=True,
                    message=f"习题生成完成，共生成 {len(exercises)} 道题目",
                    data=combined_exercises,
                    total_count=len(exercises),
                    generation_time=generation_time
                )
                print(f"习题生成完成，耗时: {generation_time:.2f}秒，生成 {len(exercises)} 道题目")
                return response
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"生成习题时出错: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成习题失败: {str(e)}"
        )


@router.get("/v1/exercise/list/{user_id}/{course_id}/{lesson_num}", tags=["Exercise"])
async def get_exercise_list(user_id: str, course_id: str, lesson_num: str, is_teacher: bool = False):
    """
    获取指定课时的习题列表
    """
    try:
        # 获取用户路径
        user_path = get_user_path(user_id, is_teacher)
        
        # 构建习题目录路径
        lesson_path = os.path.join(user_path, course_id, lesson_num)
        exercises_dir = os.path.join(lesson_path, "exercises")
        
        if not os.path.exists(exercises_dir):
            return {
                "success": True,
                "data": [],
                "total": 0,
                "message": "该课时暂无习题"
            }
        
        # 读取所有习题文件
        exercise_files = []
        for filename in os.listdir(exercises_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(exercises_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        exercise_files.append({
                            "filename": filename,
                            "file_path": file_path,
                            "metadata": data.get("metadata", {}),
                            "exercise_count": len(data.get("exercises", []))
                        })
                except Exception as e:
                    print(f"读取习题文件 {filename} 时出错: {e}")
                    continue
        
        # 按生成时间排序
        exercise_files.sort(key=lambda x: x["metadata"].get("generated_at", ""), reverse=True)
        
        return {
            "success": True,
            "data": exercise_files,
            "total": len(exercise_files),
            "message": f"找到 {len(exercise_files)} 个习题文件"
        }
        
    except Exception as e:
        print(f"获取习题列表时出错: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取习题列表失败: {str(e)}"
        )


@router.get("/v1/exercise/{user_id}/{course_id}/{lesson_num}/{filename}", tags=["Exercise"])
async def get_exercise_detail(user_id: str, course_id: str, lesson_num: str, filename: str, is_teacher: bool = False):
    """
    获取指定习题文件的详细内容
    """
    try:
        # 获取用户路径
        user_path = get_user_path(user_id, is_teacher)
        
        # 构建文件路径
        lesson_path = os.path.join(user_path, course_id, lesson_num)
        exercises_dir = os.path.join(lesson_path, "exercises")
        file_path = os.path.join(exercises_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="习题文件不存在"
            )
        
        # 读取习题文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "success": True,
            "data": data,
            "message": "获取习题详情成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取习题详情时出错: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取习题详情失败: {str(e)}"
        )


@router.delete("/v1/exercise/{user_id}/{course_id}/{lesson_num}/{filename}", tags=["Exercise"])
async def delete_exercise_file(user_id: str, course_id: str, lesson_num: str, filename: str, is_teacher: bool = False):
    """
    删除指定的习题文件
    """
    try:
        # 获取用户路径
        user_path = get_user_path(user_id, is_teacher)
        
        # 构建文件路径
        lesson_path = os.path.join(user_path, course_id, lesson_num)
        exercises_dir = os.path.join(lesson_path, "exercises")
        file_path = os.path.join(exercises_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="习题文件不存在"
            )
        
        # 删除文件
        os.remove(file_path)
        
        return {
            "success": True,
            "message": "习题文件删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除习题文件时出错: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除习题文件失败: {str(e)}"
        )


@router.get("/v1/exercise/status", tags=["Exercise"])
async def get_exercise_status():
    """
    获取习题生成服务状态
    """
    try:
        # 检查RWKV模型状态
        model = global_var.get(global_var.Model)
        model_status = "ready" if model is not None else "not_ready"
        
        return {
            "success": True,
            "data": {
                "service": "exercise_generation",
                "status": "running",
                "model_status": model_status,
                "timestamp": datetime.now().isoformat()
            },
            "message": "习题生成服务运行正常"
        }
        
    except Exception as e:
        print(f"获取服务状态时出错: {e}")
        return {
            "success": False,
            "data": {
                "service": "exercise_generation",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            "message": "习题生成服务异常"
        }
