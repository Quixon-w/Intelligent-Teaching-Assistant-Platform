# RWKV 后端 API 接口文档

## 概述

本文档描述了RWKV后端系统的API接口，包含以下五个主要模块：
- **Completions**: 聊天完成接口
- **Create**: 大纲生成接口  
- **Exercise**: 习题生成接口
- **Search**: 知识库搜索接口
- **Upload**: 文件上传接口

---

## 1. Completions 模块

### 1.1 聊天完成接口

**接口地址**: 
- `POST /v1/chat/completions`
- `POST /chat/completions`

**功能描述**: 提供聊天对话功能，支持流式和非流式响应

**请求参数**:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "hello",
      "raw": false
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
  "presystem": true,
  "session_id": "session-id",
  "isTeacher": false,
  "courseID": null,
  "max_tokens": 1000,
  "temperature": 1,
  "top_p": 0.3,
  "presence_penalty": 0,
  "frequency_penalty": 1
}
```

**参数说明**:
- `messages`: 对话消息列表，必需
- `model`: 模型名称，默认为"rwkv"
- `stream`: 是否流式响应，默认false
- `stop`: 停止词列表
- `tools`: 工具列表（可选）
- `tool_choice`: 工具选择策略
- `user_name`: 用户名（内部使用）
- `assistant_name`: 助手名（内部使用）
- `system_name`: 系统名（内部使用）
- `presystem`: 是否插入默认系统提示
- `session_id`: 会话ID，必需
- `isTeacher`: 是否为教师模式
- `courseID`: 课程ID（教师模式必需）
- `max_tokens`: 最大生成token数
- `temperature`: 温度参数
- `top_p`: top-p采样参数
- `presence_penalty`: 存在惩罚
- `frequency_penalty`: 频率惩罚

**响应格式**:
```json
{
  "object": "chat.completion",
  "model": "rwkv",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！我是RWKV助手。"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

---

## 2. Create 模块

### 2.1 大纲生成接口

**接口地址**:
- `POST /v1/create/outline`
- `POST /create/outline`

**功能描述**: 根据课程内容生成教学大纲

**请求参数**:

```json
{
  "session_id": "teacher123",
  "courseID": "math101",
  "lessonNum": "lesson01",
  "outline_type": "lesson",
  "max_words": 1000
}
```

**参数说明**:
- `session_id`: 会话ID，必需
- `courseID`: 课程ID，必需
- `lessonNum`: 课时号，可选（不提供则生成整个课程大纲）
- `outline_type`: 大纲类型，"course"(课程大纲) 或 "lesson"(课时大纲)
- `max_words`: 最大字数限制，课程大纲建议2500字，课时大纲建议1000字

**响应格式**:
```json
{
  "session_id": "teacher123",
  "courseID": "math101",
  "lessonNum": "lesson01",
  "outline_type": "lesson",
  "outline": "生成的大纲内容...",
  "word_count": 850,
  "status": "success"
}
```

### 2.2 大纲状态查询接口

**接口地址**: `GET /v1/create/outline/status`

**功能描述**: 查询大纲生成状态

**请求参数**:
- `session_id`: 会话ID
- `courseID`: 课程ID
- `lessonNum`: 课时号（可选）

**响应格式**:
```json
{
  "session_id": "teacher123",
  "courseID": "math101",
  "lessonNum": "lesson01",
  "status": "completed",
  "outline": "大纲内容..."
}
```

---

## 3. Exercise 模块

### 3.1 习题生成接口

**接口地址**:
- `POST /v1/exercise`
- `POST /exercise`

**功能描述**: 根据知识库内容生成相关习题

**请求参数**:

```json
{
  "session_id": "teacher001",
  "courseID": "MATH101",
  "lessonNum": "lesson03",
  "target_count": 10
}
```

**参数说明**:
- `session_id`: 会话ID，必需
- `courseID`: 课程ID，必需
- `lessonNum`: 课时号，必需
- `target_count`: 目标题目数量，范围1-20，默认10

**响应格式**:
```json
{
  "session_id": "teacher001",
  "courseID": "MATH101",
  "lessonNum": "lesson03",
  "exercises": [
    {
      "knowledge": "微积分/导数",
      "question": "什么是导数？",
      "options": {
        "A": "函数在某点的变化率",
        "B": "函数的积分",
        "C": "函数的极限",
        "D": "函数的连续性"
      },
      "answer": "A",
      "explain": "导数是函数在某点的变化率..."
    }
  ],
  "total_count": 10,
  "status": "success"
}
```

---

## 4. Search 模块

### 4.1 知识库搜索接口

**接口地址**:
- `POST /v1/search`
- `POST /search`

**功能描述**: 在知识库中搜索相关内容

**请求参数**:

```json
{
  "query": "什么是微积分？",
  "session_id": "session123",
  "isTeacher": false,
  "courseID": "MATH101",
  "lessonNum": "lesson01",
  "top_k": 2,
  "search_mode": "existing"
}
```

**参数说明**:
- `query`: 查询内容，必需
- `session_id`: 会话ID，必需
- `isTeacher`: 是否为教师模式，默认false
- `courseID`: 课程ID（已有文件查询模式下必填）
- `lessonNum`: 课时号（已有文件查询模式下必填）
- `top_k`: 返回结果数量，范围1-10，默认2
- `search_mode`: 搜索模式，"existing"(已有文件查询) 或 "uploaded"(用户上传文件查询)

**响应格式**:
```json
{
  "query": "什么是微积分？",
  "session_id": "session123",
  "isTeacher": false,
  "courseID": "MATH101",
  "lessonNum": "lesson01",
  "search_mode": "existing",
  "result": "[相似度: 0.856] 微积分是数学的一个分支..."
}
```

---

## 5. Upload 模块

### 5.1 文件上传接口

**接口地址**: `POST /v1/upload`

**功能描述**: 上传文件并保存至服务器指定路径

**请求参数** (multipart/form-data):
- `file`: 上传的文件，必需
- `session_id`: 会话ID，必需
- `isTeacher`: 是否为教师，默认false
- `courseID`: 课程ID（教师模式下非ask文件时必填）
- `lessonNum`: 课时号（教师模式下大纲与习题生成参考文件时必填）
- `file_encoding`: 文件编码，默认"utf-8"
- `Is_Resource`: 是否为学习资料，默认false
- `Is_Outline`: 是否为大纲与习题生成参考文件，默认false
- `Is_Ask`: 是否为可提问文件，默认false

**文件存储路径规则**:

**教师模式**:
- 学习资料: `/base_knowledge/Teachers/{session_id}/{courseID}/`
- 大纲与习题参考文件: `/base_knowledge/Teachers/{session_id}/{courseID}/{lessonNum}/`
- 可提问文件: `/base_knowledge/Teachers/{session_id}/ask/`

**学生模式**:
- 可提问文件: `/base_knowledge/Students/{session_id}/ask/`
- 其他文件: `/base_knowledge/Students/{session_id}/`

**响应格式**:
```json
{
  "message": "文件已成功上传",
  "isTeacher": true,
  "courseID": "MATH101",
  "lessonNum": "lesson01",
  "Is_Resource": false,
  "Is_Outline": true,
  "Is_Ask": false,
  "file_path": "/data-extend/wangqianxu/wqxspace/RWKV/base_knowledge/Teachers/teacher123/MATH101/lesson01/document.pdf",
  "knowledge_status": "知识库更新成功"
}
```

---

## 错误处理

所有接口在发生错误时会返回相应的HTTP状态码和错误信息：

**常见错误码**:
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

**错误响应格式**:
```json
{
  "detail": "错误描述信息"
}
```

---

## 注意事项

1. **会话管理**: 所有接口都需要提供有效的`session_id`
2. **权限控制**: 教师模式和学生模式有不同的文件访问权限
3. **文件编码**: 上传文件时注意指定正确的编码格式
4. **知识库更新**: 文件上传后会自动更新对应的知识库
5. **并发控制**: 某些接口（如completion）使用锁机制控制并发请求
6. **流式响应**: completion接口支持流式响应，需要正确处理SSE格式

---

## 示例代码

### Python 客户端示例

```python
import requests

# 聊天完成
response = requests.post("http://localhost:8000/v1/chat/completions", json={
    "messages": [{"role": "user", "content": "你好"}],
    "session_id": "test123",
    "stream": False
})

# 文件上传
with open("document.pdf", "rb") as f:
    response = requests.post("http://localhost:8000/v1/upload", 
        files={"file": f},
        data={
            "session_id": "teacher123",
            "isTeacher": True,
            "courseID": "MATH101",
            "lessonNum": "lesson01",
            "Is_Outline": True
        }
    )
```

### JavaScript 客户端示例

```javascript
// 搜索知识库
const response = await fetch('/v1/search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        query: "什么是微积分？",
        session_id: "session123",
        courseID: "MATH101",
        lessonNum: "lesson01",
        search_mode: "existing"
    })
});
``` 