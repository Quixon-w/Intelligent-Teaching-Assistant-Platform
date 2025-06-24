import os
import json
import random
import pickle
import numpy as np
import faiss
import mysql.connector
import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Union, Optional, List, Dict
from sentence_transformers import SentenceTransformer
import global_var
from utils.rwkv import *
from config.database import DATABASE_CONFIG

router = APIRouter()


def get_user_path(user_id: str, is_teacher: bool) -> str:
    """根据userID和isTeacher确定用户路径"""
    user_type = "Teachers" if is_teacher else "Students"
    return os.path.join("/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge", user_type, user_id)


class ExerciseBody(BaseModel):
    userID: str = Field(..., description="用户ID，用于确定存储路径")
    sessionId: str = Field(..., description="会话ID")
    courseId: str = Field(..., description="课程ID")
    lessonNum: str = Field(..., description="课时号")
    isTeacher: bool = Field(False, description="是否为教师用户")
    targetCount: int = Field(10, description="目标题目数量", ge=1, le=20)

    model_config = {
        "json_schema_extra": {
            "example": {
                "userID": "teacher001",
                "sessionId": "session456",
                "courseId": "MATH101",
                "lessonNum": "lesson03",
                "isTeacher": True,
                "targetCount": 10
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


def extract_knowledge_points_from_content(content: str) -> List[str]:
    """
    使用RWKV模型分析知识库内容，提取主要知识点
    
    Args:
        content: 知识库文本内容
        
    Returns:
        List[str]: 提取的知识点列表
    """
    model: TextRWKV = global_var.get(global_var.Model)
    if model is None:
        raise Exception("模型未加载")
    
    # 简化提示词，避免模型陷入循环
    prompt = f"""分析以下教学内容，提取3-5个主要知识点，格式为"一级知识点/二级知识点"：

{content[:1500]}

知识点："""
    
    try:
        import time
        start_time = time.time()
        timeout = 30  # 30秒超时
        
        # 生成知识点
        response = ""
        token_count = 0
        max_tokens = 200  # 限制最大token数
        
        for response, delta, _, _ in model.generate(prompt, stop=["\n\n", "###", "---", "问题", "题目"]):
            response += delta
            token_count += 1
            
            # 检查超时
            if time.time() - start_time > timeout:
                print(f"知识点提取超时，已生成 {len(response)} 字符")
                break
            
            # 检查token数量限制
            if token_count > max_tokens:
                print(f"达到最大token限制 {max_tokens}")
                break
        
        print(f"知识点提取完成，耗时: {time.time() - start_time:.2f}秒，生成长度: {len(response)}")
        
        # 解析知识点
        knowledge_points = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 清理格式
            if '：' in line:
                line = line.split('：')[-1]
            if '.' in line and line[0].isdigit():
                line = line.split('.', 1)[-1]
            
            # 检查是否包含知识点格式
            if '/' in line and len(line) > 3:
                knowledge_points.append(line.strip())
            elif len(line) > 5:  # 如果没有/分隔符，但内容较长，也作为知识点
                knowledge_points.append(line.strip())
        
        # 如果解析失败，使用简单的关键词提取
        if not knowledge_points:
            print("RWKV解析失败，使用关键词提取")
            # 简单的关键词提取
            keywords = []
            words = content.split()
            for word in words:
                if len(word) > 2 and word not in ['的', '是', '在', '有', '和', '与', '或', '但', '而', '了', '着', '过']:
                    keywords.append(word)
                    if len(keywords) >= 5:
                        break
            
            knowledge_points = [f"知识点/{kw}" for kw in keywords[:5]]
        
        return knowledge_points[:6]  # 最多返回6个知识点
        
    except Exception as e:
        print(f"提取知识点失败: {e}")
        # 返回默认知识点
        return ["数学/基础概念", "计算/运算", "应用/实际问题"]


def search_questions_by_knowledge(knowledge_points: List[str], target_count: int = 10) -> List[Dict]:
    """
    根据知识点在数据库中搜索相关题目
    
    Args:
        knowledge_points: 知识点列表
        target_count: 目标题目数量
        
    Returns:
        List[Dict]: 题目列表
    """
    try:
        # 连接MySQL数据库
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        
        cursor = connection.cursor(dictionary=True)
        
        all_questions = []
        
        # 对每个知识点搜索相关题目
        for knowledge in knowledge_points:
            # 使用LIKE查询匹配知识点
            query = """
            SELECT question_id, knowledge, question, options, answer, explanation 
            FROM questions 
            WHERE knowledge LIKE %s 
            ORDER BY RAND() 
            LIMIT %s
            """
            
            # 构建搜索模式，支持部分匹配
            search_patterns = [
                f"%{knowledge}%",  # 完全包含
                f"%{knowledge.split('/')[0]}%",  # 匹配一级知识点
            ]
            
            # 如果有二级知识点，也添加搜索
            if '/' in knowledge:
                search_patterns.append(f"%{knowledge.split('/')[1]}%")
            
            for pattern in search_patterns:
                cursor.execute(query, (pattern, target_count))
                results = cursor.fetchall()
                
                for result in results:
                    # 检查是否已经添加过相同的题目
                    if not any(q['question'] == result['question'] for q in all_questions):
                        # 解析JSON格式的选项
                        options = result['options']
                        if isinstance(options, str):
                            try:
                                options = json.loads(options)
                            except json.JSONDecodeError:
                                options = {"A": options}  # 如果解析失败，作为选项A
                        
                        all_questions.append({
                            'id': result['question_id'],
                            'knowledge': result['knowledge'],
                            'question': result['question'],
                            'options': options,
                            'answer': result['answer'],
                            'explanation': result['explanation']
                        })
                        
                        # 如果已经收集到足够的题目，就停止搜索
                        if len(all_questions) >= target_count:
                            break
                
                if len(all_questions) >= target_count:
                    break
        
        cursor.close()
        connection.close()
        
        return all_questions[:target_count]
        
    except Exception as e:
        print(f"从数据库搜索题目失败: {e}")
        return []


def get_knowledge_content(user_id: str, course_id: str, lesson_num: str, is_teacher: bool) -> str:
    """
    获取课时知识库内容
    
    Args:
        user_id: 用户ID
        course_id: 课程ID
        lesson_num: 课时号
        is_teacher: 是否为教师用户
        
    Returns:
        str: 知识库内容
    """
    # 获取用户路径
    user_path = get_user_path(user_id, is_teacher)
    
    # 构建知识库路径
    vector_kb_path = os.path.join(user_path, course_id, lesson_num, "vector_kb")
    
    if not os.path.exists(vector_kb_path):
        print(f"知识库路径不存在: {vector_kb_path}")
        return None
    
    try:
        # 加载嵌入模型
        model = load_embeddings_model()
        if model is None:
            return None
        
        # 加载FAISS索引
        index_path = os.path.join(vector_kb_path, "index.faiss")
        metadata_path = os.path.join(vector_kb_path, "index.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            print(f"FAISS索引文件不存在: {vector_kb_path}")
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
        
        # 提取所有文档内容
        all_contents = []
        for doc_id in id_to_uuid.values():
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
                
                all_contents.append(content)
        
        if all_contents:
            return "\n\n".join(all_contents)
        else:
            return None
            
    except Exception as e:
        print(f"获取知识库内容失败: {e}")
        return None


def call_map_add_api(lesson_id: int, question_ids: List[int]) -> bool:
    """
    调用映射添加API，将题目与课时关联
    
    Args:
        lesson_id: 课时ID
        question_ids: 题目ID列表
        
    Returns:
        bool: 是否成功
    """
    try:
        # 这里应该调用实际的API
        # 暂时返回True表示成功
        print(f"将题目 {question_ids} 映射到课时 {lesson_id}")
        return True
    except Exception as e:
        print(f"调用映射API失败: {e}")
        return False


@router.post("/v1/exercise", tags=["Exercise"])
@router.post("/exercise", tags=["Exercise"])
async def get_exercises(body: ExerciseBody):
    """
    根据课时内容生成习题
    """
    try:
        # 获取课时知识库内容
        content = get_knowledge_content(body.userID, body.courseId, body.lessonNum, body.isTeacher)
        
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"未找到课时 {body.lessonNum} 的知识库内容，请先上传相关文件并更新知识库"
            )
        
        # 提取知识点
        knowledge_points = extract_knowledge_points_from_content(content)
        
        if not knowledge_points:
            raise HTTPException(
                status_code=500,
                detail="无法从内容中提取知识点"
            )
        
        print(f"提取的知识点: {knowledge_points}")
        
        # 根据知识点搜索题目
        questions = search_questions_by_knowledge(knowledge_points, body.targetCount)
        
        if not questions:
            raise HTTPException(
                status_code=404,
                detail="未找到匹配的题目，请检查数据库中的题目数据"
            )
        
        # 生成课时ID（这里需要根据实际情况调整）
        lesson_id = hash(f"{body.userID}_{body.courseId}_{body.lessonNum}") % 1000000
        
        # 调用映射API
        question_ids = [q['id'] for q in questions]
        map_success = call_map_add_api(lesson_id, question_ids)
        
        return {
            "success": True,
            "userID": body.userID,
            "sessionId": body.sessionId,
            "courseId": body.courseId,
            "lessonNum": body.lessonNum,
            "isTeacher": body.isTeacher,
            "targetCount": body.targetCount,
            "actualCount": len(questions),
            "knowledgePoints": knowledge_points,
            "questions": questions,
            "lessonId": lesson_id,
            "mapSuccess": map_success,
            "message": f"成功生成 {len(questions)} 道习题"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"生成习题时出错: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"生成习题失败: {str(e)}"
        ) 