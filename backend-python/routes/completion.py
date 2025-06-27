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
from utils.session_manager import session_manager
import global_var


router = APIRouter()


# 创建全局会话管理器实例
# session_manager = SessionManager()  # 已移动到utils/session_manager.py


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
    tool_choice: Union[
        Literal["none", "auto", "required"], ChatCompletionNamedToolChoiceParam
    ] = "auto"
    user_name: Union[str, None] = Field(
        None, description="Internal user name", min_length=1
    )
    assistant_name: Union[str, None] = Field(
        None, description="Internal assistant name", min_length=1
    )
    system_name: Union[str, None] = Field(
        None, description="Internal system name", min_length=1
    )
    presystem: bool = Field(
        False, description="Whether to insert default system prompt at the beginning"
    )
    user_id: str = Field(..., description="User ID for identifying the user")
    session_id: str = Field(..., description="Session ID for the current conversation")
    is_teacher: bool = Field(
        False, description="Whether the user is a teacher (true) or student (false)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "你好，请介绍一下自己"
                    }
                ],
                "model": "rwkv",
                "stream": False,
                "stop": None,
                "tools": None,
                "tool_choice": "auto",
                "user_name": None,
                "assistant_name": None,
                "system_name": None,
                "presystem": False,
                "user_id": "user123",  # 用户ID
                "session_id": "session456",  # 会话ID
                "is_teacher": False,  # 用户类型
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
                            },
                            ensure_ascii=False
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
                        },
                        ensure_ascii=False
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
                        },
                        ensure_ascii=False
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
                            },
                            ensure_ascii=False
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
                        session_manager.save_dialogue(user_id, session_id, messages_dict, response, body.is_teacher)
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
                        },
                        ensure_ascii=False
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
                        },
                        ensure_ascii=False
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
    
    # 添加上下文提示
    if body.messages and len(body.messages) > 1:
        prompt += "以下是我们的对话历史，如果有需要的话，请基于历史对话来回答当前问题：\n\n"
    
    if body.messages:
        for i, message in enumerate(body.messages):
            if message.role == "system":
                prompt += f"{body.system_name or 'System'}: {message.content}\n\n"
            elif message.role == "user":
                # 为当前用户消息添加特殊标记
                if i == len(body.messages) - 1:
                    prompt += f"【当前问题】{body.user_name or user}: {message.content}\n\n"
                else:
                    prompt += f"{body.user_name or user}: {message.content}\n\n"
            elif message.role == "assistant":
                prompt += f"{body.assistant_name or bot}: {message.content}\n\n"
            elif message.role == "tool":
                prompt += f"Observation: {message.content}\n\n"
    
    # 添加回答提示
    if len(body.messages) > 1:
        prompt += f"请基于上述对话历史回答当前问题：\n{body.assistant_name or bot}: "
    else:
        prompt += f"{body.assistant_name or bot}: "
    return prompt


@router.post("/v1/chat/completions", tags=["Completions"])
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

    # 检查user_id和session_id是否提供
    if not body.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required",
        )
    
    if not body.session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id is required",
        )

    interface = "You are a helpful assistant."
    user = "User"
    bot = "Assistant"

    # 获取历史上下文消息
    context_messages = session_manager.get_context_messages(body.user_id, body.session_id, max_messages=20, is_teacher=body.is_teacher)
    
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
        "tool_choice": body.tool_choice,
        "user_name": body.user_name,
        "assistant_name": body.assistant_name,
        "system_name": body.system_name,
        "presystem": body.presystem,
        "user_id": body.user_id,
        "session_id": body.session_id,
        "is_teacher": body.is_teacher,
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
                body.user_id,
                body.session_id,
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
            body.user_id,
            body.session_id,
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
            },
            ensure_ascii=False
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
                        },
                        ensure_ascii=False
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
                        },
                        ensure_ascii=False
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
                    },
                    ensure_ascii=False
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
            },
            ensure_ascii=False
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
            },
            ensure_ascii=False
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
    if body.tools and body.tool_choice != "none":
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
