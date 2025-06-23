import asyncio
import json
import os
from threading import Lock
from typing import List, Union, Literal, Optional
from enum import Enum
import base64
import time, re, random, string

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


# class ChatCompletionMessageParam(BaseModel):
#     role: str
#     content: str

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
    sessionId: str  # 添加 sessionId 字段
    isTeacher: bool = Field(
        False, description="Whether the user is a teacher"
    )
    courseId: Union[str, None] = Field(
        None, description="Course ID, required when isTeacher is True"
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
                "sessionId": "session-id",  # 在示例中包含 sessionId
                "isTeacher": False,  # 在示例中包含 isTeacher
                "courseId": None,  # 在示例中包含 courseId
                "maxTokens": 1000,
                "temperature": 1,
                "topP": 0.3,
                "presencePenalty": 0,
                "frequencyPenalty": 1,
            }
        }
    }


# class CompletionBody(ModelConfigBody):
#     prompt: Union[str, List[str], None]
#     model: Union[str, None] = "rwkv"
#     stream: bool = False
#     stop: Union[str, List[str], None] = None

#     model_config = {
#         "json_schema_extra": {
#             "example": {
#                 "prompt": "The following is an epic science fiction masterpiece that is immortalized, "
#                 + "with delicate descriptions and grand depictions of interstellar civilization wars.\nChapter 1.\n",
#                 "model": "rwkv",
#                 "stream": False,
#                 "stop": None,
#                 "maxTokens": 100,
#                 "temperature": 1,
#                 "topP": 0.3,
#                 "presencePenalty": 0,
#                 "frequencyPenalty": 1,
#             }
#         }
#     }


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


def chat_template_old(
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

    # 检查sessionId是否提供
    if not body.sessionId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sessionId is required",
        )

    # 检查教师模式下的必要参数
    if body.isTeacher and not body.courseId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="courseId is required when isTeacher is True",
        )

    interface = "You are a helpful assistant."
    user = "User"
    bot = "Assistant"

    prompt = chat_template(model, body, interface, user, bot)

    if body.stream:
        return EventSourceResponse(
            eval_rwkv(
                model,
                request,
                body,
                prompt,
                True,
                body.stop,
                True,
            )
        )
    else:
        async for response in eval_rwkv(
            model,
            request,
            body,
            prompt,
            False,
            body.stop,
            True,
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
    model: TextRWKV, body: ChatCompletionBody, request: Request, completion_text: str, sessionId: str, isTeacher: bool, courseId: Union[str, None]
):
    # 根据isTeacher属性调整响应逻辑
    if isTeacher:
        # 教师模式：可以访问课程相关的内容
        # 这里可以添加教师特有的逻辑
        pass
    else:
        # 学生模式：只能访问学生相关的内容
        # 这里可以添加学生特有的逻辑
        pass
    
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
