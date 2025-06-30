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
import re
import time

from utils.rwkv import *
import global_var
from config.settings import get_settings
from core.rag.service import RAGService

router = APIRouter()

# 全局锁，用于控制并发请求
exercise_lock = Lock()

# 初始化RAG服务
rag_service = RAGService()


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
        return None


def get_lesson_content(user_id: str, course_id: str, lesson_num: str, is_teacher: bool):
    """
    获取课时内容，优先从FAISS向量数据库获取，如果失败则从文件获取
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
    lesson_folder = os.path.join(user_path, course_id, lesson_num)
    
    if not os.path.exists(lesson_folder):
        print(f"课时文件夹不存在: {lesson_folder}")
        return None
    
    return read_files_as_blocks(lesson_folder)


def get_lesson_content_whole(user_id: str, course_id: str, lesson_num: str, is_teacher: bool) -> str:
    """
    获取课时完整内容（用于整体生成模式）
    """
    text_blocks = get_lesson_content(user_id, course_id, lesson_num, is_teacher)
    if text_blocks:
        return "\n\n".join(text_blocks)
    return None


def read_files_as_blocks(folder_path: str) -> List[str]:
    """
    读取文件夹中的所有文件内容，按文件分割成块
    """
    text_blocks = []
    
    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        return text_blocks
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                    if content:
                        text_blocks.append(content)
                        print(f"读取文件 {filename}: {content[:100]}...")
            except Exception as e:
                print(f"读取文件 {filename} 时出错: {e}")
                continue
    
    return text_blocks


def generate_exercise_prompt_for_block(content: str, block_index: int, difficulty: str) -> str:
    """
    为单个文本块生成习题提示词
    """
    prompt = f"""基于以下教学内容，生成一道{difficulty}难度的选择题：

教学内容：
{content}

请生成一道选择题，包含：
1. 题干
2. 4个选项（A、B、C、D）
3. 正确答案
4. 详细解析
5. 涉及的知识点

格式要求：
题目：[题干内容]
A. [选项A]
B. [选项B]
C. [选项C]
D. [选项D]
正确答案：[A/B/C/D]
解析：[详细解析]
知识点：[涉及的知识点]

请确保题目与教学内容紧密相关，难度适中，选项合理。"""
    
    return prompt


async def generate_exercises_for_blocks(text_blocks: List[str], request: Request, max_tokens: int, temperature: float, difficulty: str) -> List[str]:
    """
    为多个文本块生成习题
    """
    exercises = []
    
    for i, block in enumerate(text_blocks):
        if not block.strip():
            continue
            
        prompt = generate_exercise_prompt_for_block(block, i, difficulty)
        try:
            exercise = await generate_exercises_with_rwkv(prompt, request, max_tokens, temperature)
            if exercise:
                exercises.append(exercise)
        except Exception as e:
            print(f"生成第{i+1}个文本块的习题时出错: {e}")
            continue
    
    return exercises


def generate_exercise_prompt(content: str, question_count: int, difficulty: str) -> str:
    """
    生成习题提示词（整体内容模式）
    """
    prompt = f"""基于以下教学内容，生成{question_count}道{difficulty}难度的选择题：

教学内容：
{content}

请生成{question_count}道选择题，每道题包含：
1. 题干
2. 4个选项（A、B、C、D）
3. 正确答案
4. 详细解析
5. 涉及的知识点

格式要求：
题目1：[题干内容]
A. [选项A]
B. [选项B]
C. [选项C]
D. [选项D]
正确答案：[A/B/C/D]
解析：[详细解析]
知识点：[涉及的知识点]

题目2：[题干内容]
A. [选项A]
B. [选项B]
C. [选项C]
D. [选项D]
正确答案：[A/B/C/D]
解析：[详细解析]
知识点：[涉及的知识点]

...（继续生成{question_count}道题）

请确保：
1. 题目与教学内容紧密相关
2. 难度适中，符合{difficulty}级别
3. 选项合理，避免明显错误选项
4. 解析详细，帮助学生理解
5. 知识点标注准确"""
    
    return prompt


def save_exercises_to_file(user_id: str, course_id: str, lesson_num: str, exercises: List[Dict], is_teacher: bool) -> dict:
    """
    保存习题到文件
    """
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 创建习题保存目录
    exercise_dir = os.path.join(user_path, course_id, lesson_num, "exercise")
    os.makedirs(exercise_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exercise_{timestamp}.json"
    file_path = os.path.join(exercise_dir, filename)
    
    # 保存习题数据
    exercise_data = {
        "user_id": user_id,
        "course_id": course_id,
        "lesson_num": lesson_num,
        "is_teacher": is_teacher,
        "created_time": datetime.now().isoformat(),
        "total_count": len(exercises),
        "exercises": exercises
    }
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(exercise_data, f, ensure_ascii=False, indent=2)
        
        print(f"习题已保存到文件: {file_path}")
        
        return {
            "success": True,
            "filename": filename,
            "file_path": file_path,
            "total_count": len(exercises)
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
    try:
        # 使用RAG服务生成
        response = await rag_service.generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            task_type="exercise_generation"
        )
        
        if response and response.get("success"):
            return response.get("content", "")
        else:
            print(f"RAG服务生成失败: {response}")
            return None
            
    except Exception as e:
        print(f"生成习题时出错: {e}")
        return None


def clean_generated_content(content: str) -> str:
    """
    清理生成的内容
    """
    if not content:
        return ""
    
    # 移除多余的空白字符
    content = re.sub(r'\n\s*\n', '\n\n', content)
    content = content.strip()
    
    # 确保句子完整性
    if content and not content.endswith(('.', '!', '?', '。', '！', '？')):
        # 找到最后一个完整的句子
        sentences = re.split(r'[.!?。！？]', content)
        if len(sentences) > 1:
            content = '.'.join(sentences[:-1]) + '.'
    
    return content


async def generate_with_rwkv_retry(prompt: str, request: Request, max_tokens: int, model, generation_config):
    """
    带重试机制的RWKV生成
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 使用RAG服务生成
            response = await rag_service.generate_response(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=generation_config.get("temperature", 0.7),
                task_type="exercise_generation"
            )
            
            if response and response.get("success"):
                return response.get("content", "")
            else:
                print(f"RAG服务生成失败 (尝试 {attempt + 1}/{max_retries}): {response}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                return None
                
        except Exception as e:
            print(f"生成失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            return None
    
    return None


def parse_exercises_from_response(response_text: str) -> List[Dict]:
    """
    从响应文本中解析习题
    """
    if not response_text:
        return []
    
    exercises = []
    current_exercise = {}
    
    # 按行分割
    lines = response_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检测新题目开始
        if line.startswith('题目') or line.startswith('Question'):
            if current_exercise:
                exercises.append(current_exercise)
            current_exercise = {
                'question_text': '',
                'options': [],
                'correct_answer': '',
                'explanation': '',
                'knowledge_point': ''
            }
            # 提取题干
            question_text = line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1]
            current_exercise['question_text'] = question_text.strip()
        
        # 检测选项
        elif line.startswith(('A.', 'B.', 'C.', 'D.')):
            option_text = line.split('.', 1)[-1].strip()
            current_exercise['options'].append(option_text)
        
        # 检测正确答案
        elif line.startswith('正确答案') or line.startswith('Correct Answer'):
            answer = line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1]
            current_exercise['correct_answer'] = answer.strip()
        
        # 检测解析
        elif line.startswith('解析') or line.startswith('Explanation'):
            explanation = line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1]
            current_exercise['explanation'] = explanation.strip()
        
        # 检测知识点
        elif line.startswith('知识点') or line.startswith('Knowledge Point'):
            knowledge = line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1]
            current_exercise['knowledge_point'] = knowledge.strip()
    
    # 添加最后一个习题
    if current_exercise:
        exercises.append(current_exercise)
    
    return exercises


def parse_single_exercise(block: str, question_id: int) -> Optional[Dict]:
    """
    解析单个习题块
    """
    if not block:
        return None
    
    exercise = {
        'question_id': f"q{question_id}",
        'question_text': '',
        'options': [],
        'correct_answer': '',
        'explanation': '',
        'knowledge_point': '',
        'difficulty': 'medium'
    }
    
    lines = block.split('\n')
    current_field = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('题目') or line.startswith('Question'):
            question_text = line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1]
            exercise['question_text'] = question_text.strip()
            current_field = 'question'
        
        elif line.startswith(('A.', 'B.', 'C.', 'D.')):
            option_text = line.split('.', 1)[-1].strip()
            exercise['options'].append(option_text)
            current_field = 'options'
        
        elif line.startswith('正确答案') or line.startswith('Correct Answer'):
            answer = line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1]
            exercise['correct_answer'] = answer.strip()
            current_field = 'answer'
        
        elif line.startswith('解析') or line.startswith('Explanation'):
            explanation = line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1]
            exercise['explanation'] = explanation.strip()
            current_field = 'explanation'
        
        elif line.startswith('知识点') or line.startswith('Knowledge Point'):
            knowledge = line.split('：', 1)[-1] if '：' in line else line.split(':', 1)[-1]
            exercise['knowledge_point'] = knowledge.strip()
            current_field = 'knowledge'
        
        else:
            # 继续当前字段的内容
            if current_field == 'question' and exercise['question_text']:
                exercise['question_text'] += ' ' + line
            elif current_field == 'explanation' and exercise['explanation']:
                exercise['explanation'] += ' ' + line
            elif current_field == 'knowledge' and exercise['knowledge_point']:
                exercise['knowledge_point'] += ' ' + line
    
    # 验证习题完整性
    if (exercise['question_text'] and 
        len(exercise['options']) >= 2 and 
        exercise['correct_answer'] and 
        exercise['explanation']):
        return exercise
    
    return None


def clean_json_string(json_str: str) -> str:
    """
    清理JSON字符串
    """
    # 移除可能的markdown代码块标记
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'```\s*$', '', json_str)
    
    # 移除多余的空白字符
    json_str = json_str.strip()
    
    return json_str


@router.post("/v1/exercise/generate", tags=["Exercise"], response_model=ExerciseResponse)
async def generate_exercises(body: ExerciseBody, request: Request):
    """
    生成习题接口
    """
    start_time = time.time()
    
    # 检查并发锁
    if exercise_lock.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="系统繁忙，请稍后重试"
        )
    
    try:
        with exercise_lock:
            print(f"开始生成习题: {body}")
            
            # 获取课时内容
            if body.generation_mode == "whole":
                # 整体内容模式
                content = get_lesson_content_whole(body.user_id, body.course_id, body.lesson_num, body.is_teacher)
                if not content:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="未找到课时内容，请先上传相关文件"
                    )
                
                # 生成提示词
                prompt = generate_exercise_prompt(content, body.question_count, body.difficulty)
                
                # 生成习题
                response_text = await generate_exercises_with_rwkv(prompt, request, body.max_tokens, body.temperature)
                
                if not response_text:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="习题生成失败"
                    )
                
                # 解析习题
                exercises = parse_exercises_from_response(response_text)
                
            else:
                # 按文本块生成模式
                text_blocks = get_lesson_content(body.user_id, body.course_id, body.lesson_num, body.is_teacher)
                if not text_blocks:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="未找到课时内容，请先上传相关文件"
                    )
                
                # 为每个文本块生成习题
                exercise_responses = await generate_exercises_for_blocks(
                    text_blocks, request, body.max_tokens, body.temperature, body.difficulty
                )
                
                # 解析所有习题
                exercises = []
                for i, response_text in enumerate(exercise_responses):
                    if response_text:
                        exercise = parse_single_exercise(response_text, i + 1)
                        if exercise:
                            exercises.append(exercise)
            
            # 保存习题到文件
            if exercises:
                save_result = save_exercises_to_file(
                    body.user_id, body.course_id, body.lesson_num, exercises, body.is_teacher
                )
                
                if not save_result.get("success"):
                    print(f"保存习题文件失败: {save_result.get('error')}")
            
            generation_time = time.time() - start_time
            
            return ExerciseResponse(
                success=True,
                message=f"成功生成 {len(exercises)} 道习题",
                data=response_text if body.generation_mode == "whole" else "\n\n".join(exercise_responses),
                total_count=len(exercises),
                generation_time=generation_time
            )
            
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
    获取习题列表
    """
    try:
        # 获取用户路径
        user_path = get_user_path(user_id, is_teacher)
        
        # 构建习题目录路径
        exercise_dir = os.path.join(user_path, course_id, lesson_num, "exercise")
        
        if not os.path.exists(exercise_dir):
            return {
                "files": [],
                "message": "习题目录不存在"
            }
        
        # 获取所有习题文件
        files = []
        for filename in os.listdir(exercise_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(exercise_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            exercise_data = json.load(f)
                        
                        file_size = os.path.getsize(file_path)
                        created_time = exercise_data.get('created_time', '')
                        total_count = exercise_data.get('total_count', 0)
                        
                        files.append({
                            "filename": filename,
                            "size": file_size,
                            "created_time": created_time,
                            "total_count": total_count,
                            "download_url": f"/v1/exercise/{user_id}/{course_id}/{lesson_num}/{filename}"
                        })
                    except Exception as e:
                        print(f"读取习题文件 {filename} 时出错: {e}")
                        continue
        
        # 按创建时间倒序排列
        files.sort(key=lambda x: x['created_time'], reverse=True)
        
        return {
            "files": files,
            "total_files": len(files),
            "course_id": course_id,
            "lesson_num": lesson_num,
            "user_id": user_id,
            "is_teacher": is_teacher
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取习题列表失败: {str(e)}"
        )


@router.get("/v1/exercise/{user_id}/{course_id}/{lesson_num}/{filename}", tags=["Exercise"])
async def get_exercise_detail(user_id: str, course_id: str, lesson_num: str, filename: str, is_teacher: bool = False):
    """
    获取习题详情
    """
    try:
        # 获取用户路径
        user_path = get_user_path(user_id, is_teacher)
        
        # 构建文件路径
        file_path = os.path.join(user_path, course_id, lesson_num, "exercise", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"习题文件不存在: {filename}"
            )
        
        # 读取习题文件
        with open(file_path, 'r', encoding='utf-8') as f:
            exercise_data = json.load(f)
        
        return exercise_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"读取习题文件失败: {str(e)}"
        )


@router.delete("/v1/exercise/{user_id}/{course_id}/{lesson_num}/{filename}", tags=["Exercise"])
async def delete_exercise_file(user_id: str, course_id: str, lesson_num: str, filename: str, is_teacher: bool = False):
    """
    删除习题文件
    """
    try:
        # 获取用户路径
        user_path = get_user_path(user_id, is_teacher)
        
        # 构建文件路径
        file_path = os.path.join(user_path, course_id, lesson_num, "exercise", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"习题文件不存在: {filename}"
            )
        
        # 删除文件
        os.remove(file_path)
        
        return {
            "success": True,
            "message": f"习题文件 {filename} 已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除习题文件失败: {str(e)}"
        )


@router.get("/v1/exercise/status", tags=["Exercise"])
async def get_exercise_status():
    """
    获取习题生成服务状态
    """
    return {
        "status": "running",
        "service": "exercise_generation",
        "timestamp": datetime.now().isoformat()
    }
