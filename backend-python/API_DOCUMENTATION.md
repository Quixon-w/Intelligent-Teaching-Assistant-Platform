# 智能教学助手平台 API 接口文档

## 目录
1. [文件上传接口 (upload.py)](#文件上传接口)
2. [内容创建接口 (create.py)](#内容创建接口)
3. [文件下载接口 (download.py)](#文件下载接口)
4. [智能问答接口 (qa.py)](#智能问答接口)
5. [会话管理接口 (session_routes.py)](#会话管理接口)
6. [状态缓存接口 (state_cache.py)](#状态缓存接口)
7. [配置管理接口 (config.py)](#配置管理接口)
8. [对话完成接口 (completion.py)](#对话完成接口)

---

## 文件上传接口

### 1. 文件上传
**接口地址**: `POST /v1/upload`

**功能描述**: 上传文件并保存至服务器指定的路径，支持教师和学生两种模式

**请求参数**:
- `file` (File, 必填): 上传的文件，支持 PDF、DOCX、MD、TXT 格式
- `session_id` (str, 必填): 会话ID，用于会话标识
- `user_id` (str, 必填): 用户ID，用于确定存储路径
- `is_teacher` (bool, 可选): 是否为教师，默认 False
- `course_id` (str, 可选): 课程ID，教师模式下非ask文件时必填
- `lesson_num` (str, 可选): 课时号，教师模式下非ask文件时必填
- `file_encoding` (str, 可选): 文件编码，默认 utf-8
- `is_resource` (bool, 可选): 是否为学习资料，默认 False
- `is_ask` (bool, 可选): 是否为自己上传的可提问文件，默认 False

**请求示例**:
```bash
curl -X POST "http://localhost:8000/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "session_id=session123" \
  -F "user_id=teacher001" \
  -F "is_teacher=true" \
  -F "course_id=math101" \
  -F "lesson_num=lesson01" \
  -F "is_resource=true"
```

**响应示例**:
```json
{
  "message": "文件已成功上传",
  "session_id": "session123",
  "user_id": "teacher001",
  "is_teacher": true,
  "course_id": "math101",
  "lesson_num": "lesson01",
  "is_resource": true,
  "is_ask": false,
  "file_path": "/path/to/file/document.pdf",
  "download_url": "/v1/download/resource/teacher001/math101/document.pdf",
  "knowledge_status": "知识库更新成功"
}
```

**错误响应**:
- `400`: 不支持的文件类型或参数验证失败
- `500`: 文件上传失败

---

## 内容创建接口

### 1. 创建教学大纲
**接口地址**: `POST /v1/create/outline`

**功能描述**: 基于上传的课程资料自动生成教学大纲

**请求参数**:
```json
{
  "user_id": "teacher123",
  "session_id": "session456",
  "course_id": "math101",
  "lesson_num": "lesson01",
  "is_teacher": true,
  "max_words": 1000
}
```

**参数说明**:
- `user_id` (str, 必填): 用户ID
- `session_id` (str, 必填): 会话ID
- `course_id` (str, 必填): 课程ID
- `lesson_num` (str, 必填): 课时号
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False
- `max_words` (int, 可选): 最大字数限制，建议1000字，范围500-2000

**请求示例**:
```bash
curl -X POST "http://localhost:8000/v1/create/outline" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "teacher123",
    "session_id": "session456",
    "course_id": "math101",
    "lesson_num": "lesson01",
    "is_teacher": true,
    "max_words": 1000
  }'
```

**响应示例**:
```json
{
  "message": "教学大纲生成任务已启动",
  "user_id": "teacher123",
  "course_id": "math101",
  "lesson_num": "lesson01",
  "is_teacher": true,
  "task_id": "task_12345",
  "status": "processing"
}
```

### 2. 获取大纲生成状态
**接口地址**: `GET /v1/create/outline/status`

**功能描述**: 查询教学大纲生成的状态和结果

**请求参数**:
- `user_id` (str, 必填): 用户ID
- `course_id` (str, 必填): 课程ID
- `lesson_num` (str, 必填): 课时号
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/create/outline/status?user_id=teacher123&course_id=math101&lesson_num=lesson01&is_teacher=true"
```

**响应示例**:
```json
{
  "status": "completed",
  "user_id": "teacher123",
  "course_id": "math101",
  "lesson_num": "lesson01",
  "is_teacher": true,
  "outline_content": "教学大纲内容...",
  "file_path": "/path/to/outline.md",
  "created_time": "2024-01-01 10:00:00"
}
```

---

## 文件下载接口

### 1. 下载学习资料
**接口地址**: `GET /v1/download/resource/{user_id}/{course_id}/{filename}`

**功能描述**: 下载指定课程的学习资料文件

**路径参数**:
- `user_id` (str): 用户ID
- `course_id` (str): 课程ID
- `filename` (str): 文件名

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 True

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/download/resource/teacher123/math101/document.pdf?is_teacher=true" \
  --output document.pdf
```

### 2. 下载教学大纲
**接口地址**: `GET /v1/download/outline/{user_id}/{course_id}/{lesson_num}/{filename}`

**功能描述**: 下载指定课时的教学大纲文件

**路径参数**:
- `user_id` (str): 用户ID
- `course_id` (str): 课程ID
- `lesson_num` (str): 课时号
- `filename` (str): 文件名

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 True

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/download/outline/teacher123/math101/lesson01/outline.md?is_teacher=true" \
  --output outline.md
```

### 3. 列出学习资料
**接口地址**: `GET /v1/list/resources/{user_id}/{course_id}`

**功能描述**: 列出指定课程的所有学习资料文件

**路径参数**:
- `user_id` (str): 用户ID
- `course_id` (str): 课程ID

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 True

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/list/resources/teacher123/math101?is_teacher=true"
```

**响应示例**:
```json
{
  "files": [
    {
      "filename": "document.pdf",
      "size": 1024000,
      "download_url": "/v1/download/resource/teacher123/math101/document.pdf"
    }
  ],
  "total_files": 1,
  "course_id": "math101",
  "user_id": "teacher123",
  "is_teacher": true
}
```

### 4. 列出教学大纲
**接口地址**: `GET /v1/list/outlines/{user_id}/{course_id}/{lesson_num}`

**功能描述**: 列出指定课时的所有教学大纲文件

**路径参数**:
- `user_id` (str): 用户ID
- `course_id` (str): 课程ID
- `lesson_num` (str): 课时号

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 True

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/list/outlines/teacher123/math101/lesson01?is_teacher=true"
```

**响应示例**:
```json
{
  "files": [
    {
      "filename": "outline.md",
      "size": 2048,
      "download_url": "/v1/download/outline/teacher123/math101/lesson01/outline.md",
      "created_time": "2024-01-01 10:00:00"
    }
  ],
  "total_files": 1,
  "course_id": "math101",
  "lesson_num": "lesson01",
  "user_id": "teacher123",
  "is_teacher": true
}
```

---

## 智能问答接口

### 1. 智能问答
**接口地址**: `POST /v1/qa`

**功能描述**: 基于知识库进行智能问答

**请求参数**:
```json
{
  "query": "什么是进程？",
  "user_id": "teacher123",
  "session_id": "session456",
  "is_teacher": true,
  "course_id": "MATH101",
  "lesson_num": "lesson01",
  "top_k": 3,
  "search_mode": "existing",
  "max_tokens": 1000,
  "temperature": 0.7,
  "use_context": true
}
```

**参数说明**:
- `query` (str, 必填): 用户问题
- `user_id` (str, 必填): 用户ID
- `session_id` (str, 必填): 会话ID
- `is_teacher` (bool, 可选): 是否为教师模式，默认 False
- `course_id` (str, 可选): 课程ID，已有文件查询模式下必填
- `lesson_num` (str, 可选): 课时号，已有文件查询模式下必填
- `top_k` (int, 可选): 搜索返回结果数量，默认 3，范围 1-10
- `search_mode` (str, 可选): 搜索模式，existing(已有文件查询) 或 uploaded(用户上传文件查询)，默认 existing
- `max_tokens` (int, 可选): 生成回答的最大token数，默认 1000，范围 100-2000
- `temperature` (float, 可选): 生成温度，默认 0.7，范围 0.1-1.0
- `use_context` (bool, 可选): 是否使用历史上下文，默认 True

**请求示例**:
```bash
curl -X POST "http://localhost:8000/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是进程？",
    "user_id": "teacher123",
    "session_id": "session456",
    "is_teacher": true,
    "course_id": "MATH101",
    "lesson_num": "lesson01",
    "top_k": 3,
    "search_mode": "existing",
    "max_tokens": 1000,
    "temperature": 0.7,
    "use_context": true
  }'
```

**响应示例**:
```json
{
  "answer": "进程是计算机中正在执行的程序的实例...",
  "user_id": "teacher123",
  "session_id": "session456",
  "is_teacher": true,
  "course_id": "MATH101",
  "lesson_num": "lesson01",
  "search_mode": "existing",
  "context_used": true,
  "tokens_used": 150,
  "response_time": 2.5
}
```

### 2. 获取问答状态
**接口地址**: `GET /v1/qa/status`

**功能描述**: 获取问答系统的状态信息

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/qa/status"
```

**响应示例**:
```json
{
  "status": "active",
  "model_loaded": true,
  "knowledge_base_ready": true,
  "active_sessions": 5
}
```

### 3. 获取问答历史
**接口地址**: `GET /v1/qa/sessions/{user_id}/{session_id}/history`

**功能描述**: 获取指定会话的问答历史记录

**路径参数**:
- `user_id` (str): 用户ID
- `session_id` (str): 会话ID

**查询参数**:
- `limit` (int, 可选): 返回记录数量限制，默认 10
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/qa/sessions/teacher123/session456/history?limit=10&is_teacher=true"
```

**响应示例**:
```json
{
  "user_id": "teacher123",
  "session_id": "session456",
  "is_teacher": true,
  "history": [
    {
      "query": "什么是进程？",
      "answer": "进程是计算机中正在执行的程序的实例...",
      "timestamp": "2024-01-01 10:00:00"
    }
  ],
  "count": 1
}
```

### 4. 获取问答上下文
**接口地址**: `GET /v1/qa/sessions/{user_id}/{session_id}/context`

**功能描述**: 获取指定会话的上下文消息

**路径参数**:
- `user_id` (str): 用户ID
- `session_id` (str): 会话ID

**查询参数**:
- `max_messages` (int, 可选): 最大消息数量，默认 20
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/qa/sessions/teacher123/session456/context?max_messages=20&is_teacher=true"
```

### 5. 清除问答历史
**接口地址**: `DELETE /v1/qa/sessions/{user_id}/{session_id}/history`

**功能描述**: 清除指定会话的问答历史记录

**路径参数**:
- `user_id` (str): 用户ID
- `session_id` (str): 会话ID

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X DELETE "http://localhost:8000/v1/qa/sessions/teacher123/session456/history?is_teacher=true"
```

### 6. 获取用户问答会话
**接口地址**: `GET /v1/qa/sessions/{user_id}`

**功能描述**: 获取用户的所有问答会话

**路径参数**:
- `user_id` (str): 用户ID

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/qa/sessions/teacher123?is_teacher=true"
```

---

## 会话管理接口

### 1. 清除会话对话
**接口地址**: `DELETE /v1/users/{user_id}/sessions/{session_id}/dialogues`

**功能描述**: 清除指定会话的所有对话历史

**路径参数**:
- `user_id` (str): 用户ID
- `session_id` (str): 会话ID

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X DELETE "http://localhost:8000/v1/users/teacher123/sessions/session456/dialogues?is_teacher=true"
```

**响应示例**:
```json
{
  "user_id": "teacher123",
  "session_id": "session456",
  "is_teacher": true,
  "deleted_count": 5,
  "message": "Successfully deleted 5 dialogue files"
}
```

### 2. 获取会话上下文
**接口地址**: `GET /v1/users/{user_id}/sessions/{session_id}/context`

**功能描述**: 获取指定会话的上下文消息

**路径参数**:
- `user_id` (str): 用户ID
- `session_id` (str): 会话ID

**查询参数**:
- `max_messages` (int, 可选): 最大消息数量，默认 10
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/users/teacher123/sessions/session456/context?max_messages=10&is_teacher=true"
```

**响应示例**:
```json
{
  "user_id": "teacher123",
  "session_id": "session456",
  "is_teacher": true,
  "context_messages": [
    {
      "role": "user",
      "content": "你好",
      "timestamp": "2024-01-01 10:00:00"
    }
  ],
  "message_count": 1
}
```

### 3. 获取用户会话
**接口地址**: `GET /v1/users/{user_id}/sessions`

**功能描述**: 获取用户的所有会话ID

**路径参数**:
- `user_id` (str): 用户ID

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/users/teacher123/sessions?is_teacher=true"
```

**响应示例**:
```json
{
  "user_id": "teacher123",
  "is_teacher": true,
  "sessions": ["session456", "session789"],
  "session_count": 2
}
```

### 4. 获取会话对话
**接口地址**: `GET /v1/users/{user_id}/sessions/{session_id}/dialogues`

**功能描述**: 获取指定会话的对话历史

**路径参数**:
- `user_id` (str): 用户ID
- `session_id` (str): 会话ID

**查询参数**:
- `limit` (int, 可选): 返回记录数量限制，默认 10
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/users/teacher123/sessions/session456/dialogues?limit=10&is_teacher=true"
```

### 5. 保存会话历史
**接口地址**: `POST /v1/users/{user_id}/sessions/{session_id}/save`

**功能描述**: 保存当前会话的完整历史记录

**路径参数**:
- `user_id` (str): 用户ID
- `session_id` (str): 会话ID

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求体**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "你好！有什么可以帮助你的吗？"
    }
  ]
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/v1/users/teacher123/sessions/session456/save?is_teacher=true" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"},
      {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"}
    ]
  }'
```

### 6. 加载会话历史
**接口地址**: `GET /v1/users/{user_id}/sessions/{session_id}/load`

**功能描述**: 加载指定会话的历史记录

**路径参数**:
- `user_id` (str): 用户ID
- `session_id` (str): 会话ID

**查询参数**:
- `is_teacher` (bool, 可选): 是否为教师用户，默认 False

**请求示例**:
```bash
curl -X GET "http://localhost:8000/v1/users/teacher123/sessions/session456/load?is_teacher=true"
```

---

## 状态缓存接口

### 1. 禁用状态缓存
**接口地址**: `POST /disable-state-cache`

**功能描述**: 禁用状态缓存功能

**请求示例**:
```bash
curl -X POST "http://localhost:8000/disable-state-cache"
```

**响应示例**:
```json
"success"
```

### 2. 启用状态缓存
**接口地址**: `POST /enable-state-cache`

**功能描述**: 启用状态缓存功能

**请求示例**:
```bash
curl -X POST "http://localhost:8000/enable-state-cache"
```

**响应示例**:
```json
"success"
```

### 3. 重置状态
**接口地址**: `POST /reset-state`

**功能描述**: 重置状态缓存

**请求示例**:
```bash
curl -X POST "http://localhost:8000/reset-state"
```

**响应示例**:
```json
"success"
```

---

## 配置管理接口

### 1. 切换模型
**接口地址**: `POST /switch-model`

**功能描述**: 切换RWKV模型

**请求参数**:
```json
{
  "model": "models/RWKV-4-World-3B-v1-20230619-ctx4096.pth",
  "strategy": "cuda fp16",
  "tokenizer": "",
  "custom_cuda": false,
  "deploy": false
}
```

**参数说明**:
- `model` (str, 必填): 模型文件路径
- `strategy` (str, 必填): 模型策略
- `tokenizer` (str, 可选): 分词器路径
- `custom_cuda` (bool, 可选): 是否使用自定义CUDA，默认 False
- `deploy` (bool, 可选): 部署模式，默认 False

**请求示例**:
```bash
curl -X POST "http://localhost:8000/switch-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models/RWKV-4-World-3B-v1-20230619-ctx4096.pth",
    "strategy": "cuda fp16",
    "tokenizer": "",
    "custom_cuda": false,
    "deploy": false
  }'
```

**响应示例**:
```json
"success"
```

### 2. 更新配置
**接口地址**: `POST /update-config`

**功能描述**: 更新模型配置

**请求参数**:
```json
{
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "max_tokens": 1000
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/update-config" \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_tokens": 1000
  }'
```

**响应示例**:
```json
"success"
```

### 3. 获取状态
**接口地址**: `GET /status`

**功能描述**: 获取系统状态信息

**请求示例**:
```bash
curl -X GET "http://localhost:8000/status"
```

**响应示例**:
```json
{
  "status": "Working",
  "pid": 12345,
  "device_name": "NVIDIA GeForce RTX 4090",
  "model_path": "models/RWKV-4-World-3B-v1-20230619-ctx4096.pth"
}
```

---

## 对话完成接口

### 1. 聊天完成
**接口地址**: `POST /v1/chat/completions`

**功能描述**: 基于RWKV模型进行对话生成

**请求参数**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "你好，请介绍一下自己"
    }
  ],
  "model": "rwkv",
  "stream": false,
  "stop": null,
  "tools": null,
  "tool_choice": "auto",
  "user_name": null,
  "assistant_name": null,
  "system_name": null,
  "presystem": false,
  "user_id": "user123",
  "session_id": "session456",
  "is_teacher": false
}
```

**参数说明**:
- `messages` (List, 必填): 对话消息列表
- `model` (str, 可选): 模型名称，默认 "rwkv"
- `stream` (bool, 可选): 是否流式响应，默认 False
- `stop` (str/List, 可选): 停止词
- `tools` (List, 可选): 工具列表
- `tool_choice` (str, 可选): 工具选择策略，默认 "auto"
- `user_name` (str, 可选): 用户名称
- `assistant_name` (str, 可选): 助手名称
- `system_name` (str, 可选): 系统名称
- `presystem` (bool, 可选): 是否插入默认系统提示，默认 False
- `user_id` (str, 必填): 用户ID
- `session_id` (str, 必填): 会话ID
- `is_teacher` (bool, 可选): 是否为教师，默认 False

**请求示例**:
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好，请介绍一下自己"}
    ],
    "model": "rwkv",
    "stream": false,
    "user_id": "user123",
    "session_id": "session456",
    "is_teacher": false
  }'
```

**响应示例**:
```json
{
  "object": "chat.completion",
  "model": "rwkv",
  "choices": [
    {
      "delta": {
        "content": "你好！我是一个基于RWKV模型的AI助手..."
      },
      "finish_reason": "stop",
      "index": 0
    }
  ]
}
```

**流式响应示例**:
```json
{"object": "chat.completion.chunk", "model": "rwkv", "choices": [{"delta": {"content": "你"}, "finish_reason": null, "index": 0}]}

{"object": "chat.completion.chunk", "model": "rwkv", "choices": [{"delta": {"content": "好"}, "finish_reason": null, "index": 0}]}

{"object": "chat.completion.chunk", "model": "rwkv", "choices": [{"delta": {"content": "！"}, "finish_reason": "stop", "index": 0}]}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 注意事项

1. **文件格式限制**: 上传接口仅支持 PDF、DOCX、MD、TXT 格式的文件
2. **权限控制**: 教师模式和学生模式有不同的文件存储路径和权限
3. **会话管理**: 每个用户可以有多个会话，会话历史会被保存
4. **模型状态**: 切换模型时系统会暂时不可用，请等待模型加载完成
5. **流式响应**: 聊天完成接口支持流式响应，适用于实时对话场景
6. **知识库更新**: 文件上传后会自动更新知识库，可能需要一些时间
7. **并发控制**: 某些接口使用锁机制控制并发访问，避免资源冲突 