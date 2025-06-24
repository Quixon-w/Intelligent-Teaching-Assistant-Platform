import asyncio
import json
import os
from threading import Lock
from typing import List, Union, Literal, Optional, Dict, Any
from enum import Enum
import base64
import time, re, random, string
from datetime import datetime
import pickle

from fastapi import APIRouter, Request, status, HTTPException, Form
from fastapi.encoders import jsonable_encoder
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
import tiktoken

from routes.schema import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ChatCompletionNamedToolChoiceParam,
)
from utils.rwkv import *
from utils.log import quick_log
import global_var


router = APIRouter()


class SessionManager:
    """会话管理器，负责存储和检索对话历史"""
    
    def __init__(self, base_path: str = "/data-extend/wangqianxu/wqxspace/ITAP/base_knowledge"):
        self.base_path = base_path
        self.max_dialogues = 10
        self._session_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_user_path(self, user_id: str, is_teacher: bool) -> str:
        """根据userID和isTeacher确定用户路径"""
        user_type = "Teachers" if is_teacher else "Students"
        return os.path.join(self.base_path, user_type, user_id)
    
    def _ensure_user_dialogue_dir(self, user_id: str, session_id: str, is_teacher: bool) -> str:
        """确保用户会话目录存在"""
        user_path = self._get_user_path(user_id, is_teacher)
        dialogue_path = os.path.join(user_path, "dialogue", session_id)
        if not os.path.exists(dialogue_path):
            os.makedirs(dialogue_path, exist_ok=True)
        return dialogue_path
    
    def _get_session_files(self, session_path: str) -> List[str]:
        """获取会话目录下的所有对话文件，按时间排序"""
        if not os.path.exists(session_path):
            return []
        
        files = []
        for file in os.listdir(session_path):
            if file.endswith('.pkl'):
                file_path = os.path.join(session_path, file)
                files.append((file_path, os.path.getmtime(file_path)))
        
        # 按修改时间排序，最新的在前
        files.sort(key=lambda x: x[1], reverse=True)
        return [file[0] for file in files]
    
    def _cleanup_old_dialogues(self, session_path: str):
        """清理旧的对话记录，保持最多max_dialogues个"""
        files = self._get_session_files(session_path)
        if len(files) >= self.max_dialogues:
            # 删除最旧的文件
            for old_file in files[self.max_dialogues:]:
                try:
                    os.remove(old_file)
                    print(f"Deleted old dialogue file: {old_file}")
                except Exception as e:
                    print(f"Error deleting file {old_file}: {e}")
    
    def _generate_dialogue_filename(self) -> str:
        """生成对话文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"dialogue_{timestamp}.pkl"
    
    def save_dialogue(self, user_id: str, session_id: str, messages: List[Dict[str, Any]], response: str, is_teacher: bool = False):
        """保存对话记录"""
        try:
            session_path = self._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
            
            # 创建对话记录
            dialogue_record = {
                "user_id": user_id,
                "session_id": session_id,
                "user_type": "teacher" if is_teacher else "student",
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
                "response": response,
                "message_count": len(messages)
            }
            
            # 生成文件名并保存
            filename = self._generate_dialogue_filename()
            file_path = os.path.join(session_path, filename)
            
            with open(file_path, 'wb') as f:
                pickle.dump(dialogue_record, f)
            
            # 清理旧记录
            self._cleanup_old_dialogues(session_path)
            
            # 更新缓存
            cache_key = f"{user_id}_{session_id}_{filename}"
            self._session_cache[cache_key] = dialogue_record
            
            print(f"Saved dialogue for user {user_id}, session {session_id}: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"Error saving dialogue for user {user_id}, session {session_id}: {e}")
            return None
    
    def get_session_dialogues(self, user_id: str, session_id: str, limit: int = 5, is_teacher: bool = False) -> List[Dict[str, Any]]:
        """获取指定会话的对话记录"""
        try:
            session_path = self._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
            files = self._get_session_files(session_path)
            dialogues = []
            
            for file_path in files[:limit]:
                try:
                    with open(file_path, 'rb') as f:
                        dialogue = pickle.load(f)
                        dialogues.append(dialogue)
                except Exception as e:
                    print(f"Error loading dialogue file {file_path}: {e}")
                    continue
            
            return dialogues
            
        except Exception as e:
            print(f"Error getting dialogues for user {user_id}, session {session_id}: {e}")
            return []
    
    def get_context_messages(self, user_id: str, session_id: str, max_messages: int = 20, is_teacher: bool = False) -> List[Dict[str, Any]]:
        """获取用于上下文的最近消息"""
        dialogues = self.get_session_dialogues(user_id, session_id, limit=5, is_teacher=is_teacher)
        context_messages = []
        
        for dialogue in reversed(dialogues):  # 从最旧到最新
            if "messages" in dialogue:
                # 确保消息格式正确
                for msg in dialogue["messages"]:
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        context_messages.append({
                            "role": msg["role"],
                            "content": msg["content"],
                            "raw": msg.get("raw", False)
                        })
                if len(context_messages) >= max_messages:
                    break
        
        return context_messages[-max_messages:]  # 只返回最近的max_messages条
    
    def save_session_history(self, user_id: str, session_id: str, messages: List[Dict[str, Any]], is_teacher: bool = False) -> bool:
        """保存当前会话的完整历史记录"""
        try:
            session_path = self._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
            
            # 创建会话历史记录
            session_history = {
                "user_id": user_id,
                "session_id": session_id,
                "user_type": "teacher" if is_teacher else "student",
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
                "message_count": len(messages),
                "is_session_history": True  # 标记为会话历史
            }
            
            # 保存为会话历史文件
            history_filename = f"session_history_{session_id}.pkl"
            history_path = os.path.join(session_path, history_filename)
            
            with open(history_path, 'wb') as f:
                pickle.dump(session_history, f)
            
            print(f"Saved session history for user {user_id}, session {session_id}: {history_path}")
            return True
            
        except Exception as e:
            print(f"Error saving session history for user {user_id}, session {session_id}: {e}")
            return False
    
    def load_session_history(self, user_id: str, session_id: str, is_teacher: bool = False) -> List[Dict[str, Any]]:
        """加载指定会话的历史记录"""
        try:
            session_path = self._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
            history_filename = f"session_history_{session_id}.pkl"
            history_path = os.path.join(session_path, history_filename)
            
            if not os.path.exists(history_path):
                print(f"Session history not found: {history_path}")
                return []
            
            with open(history_path, 'rb') as f:
                session_history = pickle.load(f)
            
            if "messages" in session_history:
                print(f"Loaded session history for user {user_id}, session {session_id}: {len(session_history['messages'])} messages")
                return session_history["messages"]
            else:
                print(f"No messages found in session history: {history_path}")
                return []
                
        except Exception as e:
            print(f"Error loading session history for user {user_id}, session {session_id}: {e}")
            return []
    
    def get_user_sessions(self, user_id: str, is_teacher: bool = False) -> List[str]:
        """获取用户的所有会话ID"""
        try:
            user_path = self._get_user_path(user_id, is_teacher)
            dialogue_path = os.path.join(user_path, "dialogue")
            
            if not os.path.exists(dialogue_path):
                return []
            
            sessions = []
            for session_dir in os.listdir(dialogue_path):
                session_path = os.path.join(dialogue_path, session_dir)
                if os.path.isdir(session_path):
                    sessions.append(session_dir)
            
            return sessions
            
        except Exception as e:
            print(f"Error getting sessions for user {user_id}: {e}")
            return []


# 创建全局会话管理器实例
session_manager = SessionManager()


class Role(Enum):
    User = "user"
    Assistant = "assistant"
    System = "system"
    Tool = "tool"


default_stop = [
    "\n\nUser",
    "\n\nQuestion",
    "\n\nQ",
    "\n\nHuman",
    "\n\nBob",
    "\n\nAssistant",
    "\n\nAnswer",
    "\n\nA",
    "\n\nBot",
    "\n\nAlice",
    "\n\nObservation",
]


class ChatCompletionBody(ModelConfigBody):
    messages: Union[List[ChatCompletionMessageParam], None]
    model: Union[str, None] = "rwkv"
    stream: bool = False
    stop: Union[str, List[str], None] = default_stop
    tools: Union[List[ChatCompletionToolParam], None] = None
    toolChoice: Union[
        Literal["none", "auto", "required"], ChatCompletionNamedToolChoiceParam
    ] = "auto"
    userName: Union[str, None] = Field(
        None, description="Internal user name", min_length=1
    )
    assistantName: Union[str, None] = Field(
        None, description="Internal assistant name", min_length=1
    )
    systemName: Union[str, None] = Field(
        None, description="Internal system name", min_length=1
    )
    presystem: bool = Field(
        False, description="Whether to insert default system prompt at the beginning"
    )
    userID: str = Field(..., description="User ID for identifying the user")
    sessionID: str = Field(..., description="Session ID for the current conversation")
    isTeacher: bool = Field(
        False, description="Whether the user is a teacher (true) or student (false)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "messages": [
                    {"role": Role.User.value, "content": "hello", "raw": False}
                ],
                "model": "rwkv",
                "stream": False,
                "stop": None,
                "userName": None,
                "assistantName": None,
                "systemName": None,
                "presystem": True,
                "userID": "user123",  # 用户ID
                "sessionID": "session456",  # 会话ID
                "isTeacher": False,  # 用户类型
                "max_tokens": 1000,
                "temperature": 1,
                "top_p": 0.3,
                "presence_penalty": 0,
                "frequency_penalty": 1,
            }
        }
    }


completion_lock = Lock()

requests_num = 0


async def eval_rwkv(
    model: AbstractRWKV,
    request: Request,
    body: ModelConfigBody,
    prompt: str,
    stream: bool,
    stop: Union[str, List[str], None],
    chat_mode: bool,
):
    global requests_num
    requests_num = requests_num + 1
    quick_log(request, None, "Start Waiting. RequestsNum: " + str(requests_num))
    while completion_lock.locked():
        if await request.is_disconnected():
            requests_num = requests_num - 1
            print(f"{request.client} Stop Waiting (Lock)")
            quick_log(
                request,
                None,
                "Stop Waiting (Lock). RequestsNum: " + str(requests_num),
            )
            return
        await asyncio.sleep(0.1)
    else:
        with completion_lock:
            if await request.is_disconnected():
                requests_num = requests_num - 1
                print(f"{request.client} Stop Waiting (Lock)")
                quick_log(
                    request,
                    None,
                    "Stop Waiting (Lock). RequestsNum: " + str(requests_num),
                )
                return
            set_rwkv_config(model, global_var.get(global_var.Model_Config))
            set_rwkv_config(model, body)
            print(get_rwkv_config(model))

            response, prompt_tokens, completion_tokens = "", 0, 0
            completion_start_time = None
            try:
                for response, delta, prompt_tokens, completion_tokens in model.generate(
                    prompt,
                    stop=stop,
                ):
                    if not completion_start_time:
                        completion_start_time = time.time()
                    if await request.is_disconnected():
                        break
                    if stream:
                        yield json.dumps(
                            {
                                "object": (
                                    "chat.completion.chunk"
                                    if chat_mode
                                    else "text_completion"
                                ),
                                # "response": response,
                                "model": model.name,
                                "choices": [
                                    (
                                        {
                                            "delta": {"content": delta},
                                            "finish_reason": None,
                                            "index": 0,
                                        }
                                        if chat_mode
                                        else {
                                            "text": delta,
                                            "finish_reason": None,
                                            "index": 0,
                                        }
                                    )
                                ],
                            }
                        ) + "\n"
                    else:
                        response += delta
                if not stream:
                    yield json.dumps(
                        {
                            "object": (
                                "chat.completion" if chat_mode else "text_completion"
                            ),
                            "model": model.name,
                            "choices": [
                                (
                                    {
                                        "message": {"role": "assistant", "content": response},
                                        "finish_reason": "stop",
                                        "index": 0,
                                    }
                                    if chat_mode
                                    else {
                                        "text": response,
                                        "finish_reason": "stop",
                                        "index": 0,
                                    }
                                )
                            ],
                            "usage": {
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "total_tokens": prompt_tokens + completion_tokens,
                            },
                        }
                    )
            except Exception as e:
                print(f"Generation error: {e}")
                if not stream:
                    yield json.dumps(
                        {
                            "error": {
                                "message": f"Generation error: {str(e)}",
                                "type": "generation_error",
                            }
                        }
                    )
            finally:
                requests_num = requests_num - 1
                quick_log(
                    request,
                    None,
                    "Generation Complete. RequestsNum: " + str(requests_num),
                )


async def eval_rwkv_with_context(
    model: AbstractRWKV,
    request: Request,
    body: ModelConfigBody,
    prompt: str,
    stream: bool,
    stop: Union[str, List[str], None],
    chat_mode: bool,
    user_id: str,
    session_id: str,
    current_messages: List[ChatCompletionMessageParam],
):
    """带上下文管理的RWKV评估函数"""
    global requests_num
    requests_num = requests_num + 1
    quick_log(request, None, "Start Waiting. RequestsNum: " + str(requests_num))
    
    while completion_lock.locked():
        if await request.is_disconnected():
            requests_num = requests_num - 1
            print(f"{request.client} Stop Waiting (Lock)")
            quick_log(
                request,
                None,
                "Stop Waiting (Lock). RequestsNum: " + str(requests_num),
            )
            return
        await asyncio.sleep(0.1)
    else:
        with completion_lock:
            if await request.is_disconnected():
                requests_num = requests_num - 1
                print(f"{request.client} Stop Waiting (Lock)")
                quick_log(
                    request,
                    None,
                    "Stop Waiting (Lock). RequestsNum: " + str(requests_num),
                )
                return
            set_rwkv_config(model, global_var.get(global_var.Model_Config))
            set_rwkv_config(model, body)
            print(get_rwkv_config(model))

            response, prompt_tokens, completion_tokens = "", 0, 0
            completion_start_time = None
            try:
                for response, delta, prompt_tokens, completion_tokens in model.generate(
                    prompt,
                    stop=stop,
                ):
                    if not completion_start_time:
                        completion_start_time = time.time()
                    if await request.is_disconnected():
                        break
                    if stream:
                        yield json.dumps(
                            {
                                "object": (
                                    "chat.completion.chunk"
                                    if chat_mode
                                    else "text_completion"
                                ),
                                "model": model.name,
                                "choices": [
                                    (
                                        {
                                            "delta": {"content": delta},
                                            "finish_reason": None,
                                            "index": 0,
                                        }
                                        if chat_mode
                                        else {
                                            "text": delta,
                                            "finish_reason": None,
                                            "index": 0,
                                        }
                                    )
                                ],
                            }
                        ) + "\n"
                    else:
                        response += delta
                
                # 保存对话记录（只在非流式模式下）
                if not stream and response:
                    try:
                        # 转换消息格式为字典，包含完整的对话
                        messages_dict = []
                        
                        # 添加用户消息
                        for msg in current_messages:
                            messages_dict.append({
                                "role": msg.role,
                                "content": msg.content,
                                "raw": getattr(msg, 'raw', False)
                            })
                        
                        # 添加助手回复
                        messages_dict.append({
                            "role": "assistant",
                            "content": response,
                            "raw": False
                        })
                        
                        # 保存完整的对话记录
                        session_manager.save_dialogue(user_id, session_id, messages_dict, response, body.isTeacher)
                        print(f"保存完整对话记录: 用户消息 {len(current_messages)} 条 + 助手回复 1 条")
                    except Exception as e:
                        print(f"Error saving dialogue: {e}")
                
                if not stream:
                    yield json.dumps(
                        {
                            "object": (
                                "chat.completion" if chat_mode else "text_completion"
                            ),
                            "model": model.name,
                            "choices": [
                                (
                                    {
                                        "message": {"role": "assistant", "content": response},
                                        "finish_reason": "stop",
                                        "index": 0,
                                    }
                                    if chat_mode
                                    else {
                                        "text": response,
                                        "finish_reason": "stop",
                                        "index": 0,
                                    }
                                )
                            ],
                            "usage": {
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "total_tokens": prompt_tokens + completion_tokens,
                            },
                        }
                    )
            except Exception as e:
                print(f"Generation error: {e}")
                if not stream:
                    yield json.dumps(
                        {
                            "error": {
                                "message": f"Generation error: {str(e)}",
                                "type": "generation_error",
                            }
                        }
                    )
            finally:
                requests_num = requests_num - 1
                quick_log(
                    request,
                    None,
                    "Generation Complete. RequestsNum: " + str(requests_num),
                )


def chat_template(
    model: TextRWKV, body: ChatCompletionBody, interface: str, user: str, bot: str
):
    prompt = ""
    if body.presystem:
        prompt += f"{interface}\n\n"
    if body.messages:
        for message in body.messages:
            if message.role == "system":
                prompt += f"{body.systemName or 'System'}: {message.content}\n\n"
            elif message.role == "user":
                prompt += f"{body.userName or user}: {message.content}\n\n"
            elif message.role == "assistant":
                prompt += f"{body.assistantName or bot}: {message.content}\n\n"
            elif message.role == "tool":
                prompt += f"Observation: {message.content}\n\n"
    prompt += f"{body.assistantName or bot}: "
    return prompt


@router.post("/v1/chat/completions", tags=["Completions"])
@router.post("/chat/completions", tags=["Completions"])
async def chat_completions(body: ChatCompletionBody, request: Request):
    model: TextRWKV = global_var.get(global_var.Model)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded",
        )

    if body.messages is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="messages is required",
        )

    # 检查userID和sessionID是否提供
    if not body.userID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="userID is required",
        )
    
    if not body.sessionID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sessionID is required",
        )

    interface = "You are a helpful assistant."
    user = "User"
    bot = "Assistant"

    # 获取历史上下文消息
    context_messages = session_manager.get_context_messages(body.userID, body.sessionID, max_messages=20, is_teacher=body.isTeacher)
    
    # 合并历史消息和当前消息
    all_messages = []
    
    # 添加历史消息（保留所有历史消息）
    all_messages.extend(context_messages)
    
    # 添加当前消息（转换为字典格式）
    for msg in body.messages:
        all_messages.append({
            "role": msg.role,
            "content": msg.content,
            "raw": getattr(msg, 'raw', False)
        })
    
    print(f"历史消息数量: {len(context_messages)}")
    print(f"当前消息数量: {len(body.messages)}")
    print(f"总消息数量: {len(all_messages)}")
    
    # 打印历史消息内容用于调试
    if context_messages:
        print("历史消息内容:")
        for i, msg in enumerate(context_messages[-3:]):  # 只显示最后3条
            print(f"  {i+1}. {msg['role']}: {msg['content'][:50]}...")
    
    # 创建包含上下文的请求体
    context_body_data = {
        "messages": all_messages,
        "model": body.model,
        "stream": body.stream,
        "stop": body.stop,
        "tools": body.tools,
        "toolChoice": body.toolChoice,
        "userName": body.userName,
        "assistantName": body.assistantName,
        "systemName": body.systemName,
        "presystem": body.presystem,
        "userID": body.userID,
        "sessionID": body.sessionID,
        "isTeacher": body.isTeacher,
    }
    
    # 只在有值时才添加配置参数
    if hasattr(body, 'max_tokens') and body.max_tokens is not None:
        context_body_data["max_tokens"] = body.max_tokens
    if hasattr(body, 'temperature') and body.temperature is not None:
        context_body_data["temperature"] = body.temperature
    if hasattr(body, 'top_p') and body.top_p is not None:
        context_body_data["top_p"] = body.top_p
    if hasattr(body, 'presence_penalty') and body.presence_penalty is not None:
        context_body_data["presence_penalty"] = body.presence_penalty
    if hasattr(body, 'frequency_penalty') and body.frequency_penalty is not None:
        context_body_data["frequency_penalty"] = body.frequency_penalty
    
    context_body = ChatCompletionBody(**context_body_data)

    prompt = chat_template(model, context_body, interface, user, bot)
    
    print(f"生成的prompt长度: {len(prompt)}")
    print(f"Prompt预览: {prompt[:200]}...")

    if body.stream:
        return EventSourceResponse(
            eval_rwkv_with_context(
                model,
                request,
                context_body,
                prompt,
                True,
                body.stop,
                True,
                body.userID,
                body.sessionID,
                body.messages,  # 只保存当前消息，不包含历史
            )
        )
    else:
        async for response in eval_rwkv_with_context(
            model,
            request,
            context_body,
            prompt,
            False,
            body.stop,
            True,
            body.userID,
            body.sessionID,
            body.messages,  # 只保存当前消息，不包含历史
        ):
            return response


async def chat_with_tools(
    model: TextRWKV, body: ChatCompletionBody, request: Request, completion_text: str
):
    # 检查是否有工具调用
    if not body.tools:
        return completion_text

    # 解析工具调用
    tool_calls = []
    # 这里需要实现工具调用的解析逻辑
    # 暂时返回原始文本
    return completion_text


def generate_tool_call_id():
    return f"call_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"


async def async_generator_stream_response_tool_call(
    model: TextRWKV,
    body: ChatCompletionBody,
    request: Request,
    completion_text: str,
    tool_call_id: str,
):
    # NOTE: There is none of existing failure analysis.

    # Initialization
    tool_calls = []
    current_tool_call = None
    current_function_name = ""
    current_arguments = ""
    in_function_call = False
    in_arguments = False
    brace_count = 0
    quote_count = 0
    escape_next = False

    # Process the completion text character by character
    for char in completion_text:
        if escape_next:
            if in_arguments:
                current_arguments += char
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            if in_arguments:
                current_arguments += char
            continue

        if char == '"' and not escape_next:
            quote_count += 1
            if in_arguments:
                current_arguments += char
            continue

        if quote_count % 2 == 1:  # Inside quotes
            if in_arguments:
                current_arguments += char
            continue

        # Outside quotes
        if char == "{":
            brace_count += 1
            if in_arguments:
                current_arguments += char
            if brace_count == 1 and not in_function_call:
                in_function_call = True
                current_tool_call = {
                    "id": tool_call_id,
                    "type": "function",
                    "function": {"name": "", "arguments": ""},
                }
        elif char == "}":
            brace_count -= 1
            if in_arguments:
                current_arguments += char
            if brace_count == 0 and in_function_call:
                in_function_call = False
                in_arguments = False
                if current_tool_call:
                    current_tool_call["function"]["arguments"] = current_arguments
                    tool_calls.append(current_tool_call)
                    current_tool_call = None
                    current_arguments = ""
        elif char == ":" and in_function_call and not in_arguments:
            in_arguments = True
        else:
            if in_function_call and not in_arguments:
                current_function_name += char
            elif in_arguments:
                current_arguments += char

    # Finalize any incomplete tool call
    if current_tool_call and current_function_name:
        current_tool_call["function"]["name"] = current_function_name.strip()
        current_tool_call["function"]["arguments"] = current_arguments
        tool_calls.append(current_tool_call)

    # Generate streaming response
    if tool_calls:
        # Send tool calls
        yield json.dumps(
            {
                "object": "chat.completion.chunk",
                "model": model.name,
                "choices": [
                    {
                        "delta": {
                            "role": "assistant",
                            "tool_calls": tool_calls,
                        },
                        "finish_reason": "tool_calls",
                        "index": 0,
                    }
                ],
            }
        ) + "\n"

        # Process tool calls
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            # Find the tool definition
            tool_definition = None
            for tool in body.tools:
                if tool.function.name == function_name:
                    tool_definition = tool
                    break

            if tool_definition:
                try:
                    # Parse arguments
                    args_dict = json.loads(arguments)
                    
                    # Execute function (placeholder)
                    # In a real implementation, you would call the actual function
                    result = f"Function {function_name} executed with arguments: {args_dict}"
                    
                    # Send tool result
                    yield json.dumps(
                        {
                            "object": "chat.completion.chunk",
                            "model": model.name,
                            "choices": [
                                {
                                    "delta": {
                                        "role": "tool",
                                        "content": result,
                                        "tool_call_id": tool_call["id"],
                                    },
                                    "finish_reason": None,
                                    "index": 0,
                                }
                            ],
                        }
                    ) + "\n"
                    
                except json.JSONDecodeError:
                    # Invalid JSON arguments
                    yield json.dumps(
                        {
                            "object": "chat.completion.chunk",
                            "model": model.name,
                            "choices": [
                                {
                                    "delta": {
                                        "role": "tool",
                                        "content": f"Invalid JSON arguments for function {function_name}",
                                        "tool_call_id": tool_call["id"],
                                    },
                                    "finish_reason": None,
                                    "index": 0,
                                }
                            ],
                        }
                    ) + "\n"
            else:
                # Tool not found
                yield json.dumps(
                    {
                        "object": "chat.completion.chunk",
                        "model": model.name,
                        "choices": [
                            {
                                "delta": {
                                    "role": "tool",
                                    "content": f"Tool {function_name} not found",
                                    "tool_call_id": tool_call["id"],
                                },
                                "finish_reason": None,
                                "index": 0,
                            }
                        ],
                    }
                ) + "\n"

        # Send final message
        yield json.dumps(
            {
                "object": "chat.completion.chunk",
                "model": model.name,
                "choices": [
                    {
                        "delta": {},
                        "finish_reason": "stop",
                        "index": 0,
                    }
                ],
            }
        ) + "\n"
    else:
        # No tool calls, send regular completion
        yield json.dumps(
            {
                "object": "chat.completion.chunk",
                "model": model.name,
                "choices": [
                    {
                        "delta": {"content": completion_text},
                        "finish_reason": "stop",
                        "index": 0,
                    }
                ],
            }
        ) + "\n"


def postprocess_response(response: dict, tool_call_id: str):
    # NOTE: There is none of existing failure analysis.

    # Extract the completion text from the response
    completion_text = ""
    if "choices" in response and len(response["choices"]) > 0:
        choice = response["choices"][0]
        if "message" in choice and "content" in choice["message"]:
            completion_text = choice["message"]["content"]
        elif "text" in choice:
            completion_text = choice["text"]

    # Check if the completion contains tool calls
    if "function" in completion_text.lower() or "{" in completion_text:
        # This might contain tool calls, process them
        return None  # Indicate that streaming is needed
    else:
        # Regular completion, return as is
        return response


async def chat(
    model: TextRWKV, body: ChatCompletionBody, request: Request, completion_text: str, sessionId: str
):
    # 处理工具调用
    if body.tools and body.toolChoice != "none":
        # 检查是否需要工具调用
        if "function" in completion_text.lower() or "{" in completion_text:
            tool_call_id = generate_tool_call_id()
            return EventSourceResponse(
                async_generator_stream_response_tool_call(
                    model, body, request, completion_text, tool_call_id
                )
            )
    
    # 返回普通聊天响应
    return completion_text


# 会话管理相关的API端点
@router.get("/v1/users/{user_id}/sessions/{session_id}/dialogues", tags=["Session Management"])
async def get_session_dialogues(user_id: str, session_id: str, limit: int = 10, is_teacher: bool = False):
    """获取指定会话的对话历史"""
    try:
        dialogues = session_manager.get_session_dialogues(user_id, session_id, limit=limit, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "dialogues": dialogues,
            "count": len(dialogues)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dialogues: {str(e)}"
        )


@router.delete("/v1/users/{user_id}/sessions/{session_id}/dialogues", tags=["Session Management"])
async def clear_session_dialogues(user_id: str, session_id: str, is_teacher: bool = False):
    """清除指定会话的所有对话历史"""
    try:
        session_path = session_manager._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
        
        # 删除所有对话文件
        files = session_manager._get_session_files(session_path)
        deleted_count = 0
        
        for file_path in files:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} dialogue files"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing dialogues: {str(e)}"
        )


@router.get("/v1/users/{user_id}/sessions/{session_id}/context", tags=["Session Management"])
async def get_session_context(user_id: str, session_id: str, max_messages: int = 10, is_teacher: bool = False):
    """获取指定会话的上下文消息"""
    try:
        context_messages = session_manager.get_context_messages(user_id, session_id, max_messages=max_messages, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "context_messages": context_messages,
            "message_count": len(context_messages)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving context: {str(e)}"
        )


@router.get("/v1/users/{user_id}/sessions/{session_id}/info", tags=["Session Management"])
async def get_session_info(user_id: str, session_id: str, is_teacher: bool = False):
    """获取指定会话的基本信息"""
    try:
        session_path = session_manager._ensure_user_dialogue_dir(user_id, session_id, is_teacher)
        
        files = session_manager._get_session_files(session_path)
        total_size = sum(os.path.getsize(f) for f in files)
        
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "dialogue_count": len(files),
            "total_size_bytes": total_size,
            "max_dialogues": session_manager.max_dialogues,
            "session_path": session_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session info: {str(e)}"
        )


@router.post("/v1/users/{user_id}/sessions/{session_id}/save", tags=["Session Management"])
async def save_session_history(user_id: str, session_id: str, messages: List[Dict[str, Any]], is_teacher: bool = False):
    """保存当前会话的完整历史记录"""
    try:
        success = session_manager.save_session_history(user_id, session_id, messages, is_teacher=is_teacher)
        if success:
            return {
                "user_id": user_id,
                "session_id": session_id,
                "is_teacher": is_teacher,
                "message": "Session history saved successfully",
                "message_count": len(messages)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save session history"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving session history: {str(e)}"
        )


@router.get("/v1/users/{user_id}/sessions/{session_id}/load", tags=["Session Management"])
async def load_session_history(user_id: str, session_id: str, is_teacher: bool = False):
    """加载指定会话的历史记录"""
    try:
        messages = session_manager.load_session_history(user_id, session_id, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "is_teacher": is_teacher,
            "messages": messages,
            "message_count": len(messages)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading session history: {str(e)}"
        )


@router.get("/v1/users/{user_id}/sessions", tags=["Session Management"])
async def get_user_sessions(user_id: str, is_teacher: bool = False):
    """获取用户的所有会话ID"""
    try:
        sessions = session_manager.get_user_sessions(user_id, is_teacher=is_teacher)
        return {
            "user_id": user_id,
            "is_teacher": is_teacher,
            "sessions": sessions,
            "session_count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user sessions: {str(e)}"
        )
