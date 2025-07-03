# 智能教学助手平台 API 接口文档

## 项目概述

智能教学助手平台(ITAP)是一个基于RWKV-RAG架构的智能教学系统，支持文件上传、知识库构建、智能问答、教学大纲生成、习题生成等功能。

### 技术栈
- **后端框架**: FastAPI
- **AI模型**: RWKV
- **向量数据库**: ChromaDB
- **嵌入模型**: BGEM3
- **重排序模型**: BGE-Reranker
- **文档处理**: python-docx, PyPDF2

### 服务器配置
- **默认端口**: 8001
- **默认主机**: 127.0.0.1
- **ChromaDB端口**: 8000

---

## 接口分类

### 1. 核心AI接口 (Core AI APIs)

#### 1.1 聊天完成接口

##### POST `/v1/chat/completions`
**功能**: 智能对话完成接口，支持多轮对话和工具调用

**请求体**:
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

**响应**:
```json
{
  "object": "chat.completion",
  "model": "rwkv",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "你好！我是智能教学助手..."
      },
      "finish_reason": "stop",
      "index": 0
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

##### POST `/chat/completions`
**功能**: 聊天完成接口的简化版本

##### POST `/v1/completions`
**功能**: 文本完成接口

##### POST `/completions`
**功能**: 文本完成接口的简化版本

#### 1.2 嵌入向量接口

##### POST `/v1/embeddings`
**功能**: 生成文本嵌入向量

##### POST `/embeddings`
**功能**: 嵌入向量接口的简化版本

##### POST `/v1/engines/text-embedding-ada-002/embeddings`
**功能**: 兼容OpenAI格式的嵌入接口

##### POST `/engines/text-embedding-ada-002/embeddings`
**功能**: 兼容OpenAI格式的嵌入接口简化版本

---

### 2. 模型配置接口 (Model Configuration)

#### 2.1 模型切换

##### POST `/switch-model`
**功能**: 切换RWKV模型

**请求体**:
```json
{
  "model": "models/RWKV-4-World-3B-v1-20230619-ctx4096.pth",
  "strategy": "cuda fp16",
  "tokenizer": "",
  "custom_cuda": false,
  "deploy": false
}
```

**响应**: `"success"`

#### 2.2 配置更新

##### POST `/update-config`
**功能**: 更新模型配置参数

#### 2.3 状态查询

##### GET `/status`
**功能**: 查询服务器和模型状态

**响应**:
```json
{
  "status": "Working",
  "pid": 12345,
  "device_name": "NVIDIA GeForce RTX 4090",
  "model_path": "models/RWKV-4-World-3B-v1-20230619-ctx4096.pth"
}
```

---

### 3. 文件管理接口 (File Management)

#### 3.1 文件上传

##### POST `/v1/upload`
**功能**: 上传文件并构建知识库

**请求参数**:
- `file`: 上传的文件 (支持PDF、DOCX、MD、TXT格式)
- `session_id`: 会话ID
- `user_id`: 用户ID
- `is_teacher`: 是否为教师 (默认false)
- `course_id`: 课程ID (教师模式下必填)
- `lesson_num`: 课时号 (教师模式下必填)
- `file_encoding`: 文件编码 (默认utf-8)
- `is_resource`: 是否为学习资料 (默认false)
- `is_ask`: 是否为可提问文件 (默认false)

**响应**:
```json
{
  "message": "文件已成功上传",
  "session_id": "session456",
  "user_id": "user123",
  "is_teacher": true,
  "course_id": "MATH101",
  "lesson_num": "lesson01",
  "is_resource": false,
  "is_ask": false,
  "file_path": "/path/to/uploaded/file.pdf",
  "download_url": "/v1/download/resource/user123/MATH101/file.pdf",
  "knowledge_status": "知识库更新成功",
  "collection_name": "kb_user123_MATH101_lesson01",
  "chromadb_host": "localhost",
  "chromadb_port": 8000
}
```

#### 3.2 文件下载

##### GET `/v1/download/resource/{user_id}/{course_id}/{filename}`
**功能**: 下载学习资料文件

**参数**:
- `user_id`: 用户ID
- `course_id`: 课程ID
- `filename`: 文件名
- `is_teacher`: 是否为教师 (默认true)

##### GET `/v1/download/outline/{user_id}/{course_id}/{lesson_num}/{filename}`
**功能**: 下载课时教学大纲文件

**参数**:
- `user_id`: 用户ID
- `course_id`: 课程ID
- `lesson_num`: 课时号
- `filename`: 文件名
- `is_teacher`: 是否为教师 (默认true)

##### GET `/v1/download/exercise/{user_id}/{course_id}/{lesson_num}/{filename}`
**功能**: 下载习题文件

#### 3.3 文件列表

##### GET `/v1/list/resources/{user_id}/{course_id}`
**功能**: 列出指定课程的所有学习资料文件

**响应**:
```json
{
  "files": [
    {
      "filename": "lesson01.pdf",
      "size": 1024576,
      "download_url": "/v1/download/resource/user123/MATH101/lesson01.pdf"
    }
  ],
  "total_files": 1,
  "course_id": "MATH101",
  "user_id": "user123",
  "is_teacher": true
}
```

##### GET `/v1/list/outlines/{user_id}/{course_id}/{lesson_num}`
**功能**: 列出指定课时的所有教学大纲文件

##### GET `/v1/list/exercises/{user_id}/{course_id}/{lesson_num}`
**功能**: 列出指定课时的所有习题文件

---

### 4. 知识库管理接口 (Knowledge Base Management)

#### 4.1 知识库搜索

##### POST `/v1/knowledge/search`
**功能**: 搜索知识库内容

**请求体**:
```json
{
  "query": "什么是机器学习",
  "user_id": "user123",
  "is_teacher": false,
  "course_id": "CS101",
  "lesson_num": "lesson01",
  "is_ask": false,
  "top_k": 5,
  "use_rerank": true
}
```

**响应**:
```json
{
  "query": "什么是机器学习",
  "results": [
    {
      "content": "机器学习是人工智能的一个分支...",
      "score": 0.95,
      "metadata": {}
    }
  ],
  "total_results": 1,
  "collection_name": "kb_user123_CS101_lesson01",
  "use_rerank": true
}
```

##### GET `/v1/search`
**功能**: 简化版知识库搜索

##### GET `/search`
**功能**: 最简化版知识库搜索

#### 4.2 知识库管理

##### GET `/v1/knowledge/collections`
**功能**: 列出用户的知识库collections

**参数**:
- `user_id`: 用户ID
- `is_teacher`: 是否为教师 (默认false)

**响应**:
```json
{
  "user_id": "user123",
  "is_teacher": false,
  "collections": [
    {
      "name": "kb_user123_CS101_lesson01",
      "metadata": {}
    }
  ],
  "total_count": 1
}
```

##### DELETE `/v1/knowledge/collection`
**功能**: 删除指定的collection

**参数**:
- `collection_name`: collection名称

##### GET `/v1/knowledge/status`
**功能**: 获取知识库系统状态

**响应**:
```json
{
  "status": "healthy",
  "chromadb": {
    "host": "localhost",
    "port": 8000,
    "connected": true,
    "collections_count": 5
  },
  "models": {
    "bgem3_path": "/path/to/bgem3",
    "reranker_path": "/path/to/reranker"
  },
  "config": {
    "chunk_size": 500,
    "chunk_overlap": 50
  }
}
```

---

### 5. 智能问答接口 (Intelligent Q&A)

#### 5.1 智能问答

##### POST `/v1/qa`
**功能**: 智能问答接口，支持基于知识库的问答

**请求体**:
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

**响应**:
```json
{
  "query": "什么是进程？",
  "answer": "进程是计算机中正在运行的程序实例...",
  "context_used": true,
  "search_results": [
    {
      "content": "进程相关的知识点...",
      "score": 0.95
    }
  ],
  "generation_time": 2.5,
  "tokens_used": 150,
  "session_id": "session456",
  "user_id": "teacher123"
}
```

#### 5.2 问答状态

##### GET `/v1/qa/status`
**功能**: 获取问答系统状态

**响应**:
```json
{
  "status": "healthy",
  "active_sessions": 5,
  "total_queries": 1000,
  "average_response_time": 2.3
}
```

#### 5.3 问答会话管理

##### GET `/v1/qa/sessions/{user_id}/{session_id}/history`
**功能**: 获取问答会话历史

**参数**:
- `user_id`: 用户ID
- `session_id`: 会话ID
- `limit`: 返回记录数限制 (默认10)
- `is_teacher`: 是否为教师 (默认false)

##### GET `/v1/qa/sessions/{user_id}/{session_id}/context`
**功能**: 获取问答会话上下文

**参数**:
- `user_id`: 用户ID
- `session_id`: 会话ID
- `max_messages`: 最大消息数 (默认20)
- `is_teacher`: 是否为教师 (默认false)

##### DELETE `/v1/qa/sessions/{user_id}/{session_id}/history`
**功能**: 清除问答会话历史

##### GET `/v1/qa/sessions/{user_id}`
**功能**: 获取用户的所有问答会话

---

### 6. 内容生成接口 (Content Generation)

#### 6.1 教学大纲生成

##### POST `/v1/create/outline`
**功能**: 生成教学大纲

**请求体**:
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

**响应**:
```json
{
  "success": true,
  "message": "教学大纲生成成功",
  "outline_content": "# 课时教学大纲\n\n## 1. 教学目标\n...",
  "word_count": 950,
  "generation_time": 5.2,
  "file_info": {
    "docx_path": "/path/to/outline.docx",
    "txt_path": "/path/to/outline.txt",
    "download_url": "/v1/download/outline/teacher123/math101/lesson01/outline.docx"
  },
  "user_id": "teacher123",
  "course_id": "math101",
  "lesson_num": "lesson01"
}
```

##### GET `/v1/create/outline/status`
**功能**: 获取大纲生成状态

**参数**:
- `user_id`: 用户ID
- `course_id`: 课程ID
- `lesson_num`: 课时号
- `is_teacher`: 是否为教师 (默认false)

##### GET `/create/outline`
**功能**: 简化版大纲生成接口

#### 6.2 习题生成

##### POST `/v1/exercise/generate`
**功能**: 生成习题

**请求体**:
```json
{
  "user_id": "teacher123",
  "session_id": "session456",
  "course_id": "math101",
  "lesson_num": "lesson01",
  "is_teacher": true,
  "question_count": 5,
  "difficulty": "medium",
  "max_tokens": 2000,
  "temperature": 0.7,
  "generation_mode": "block"
}
```

**响应**:
```json
{
  "success": true,
  "message": "习题生成成功",
  "data": "生成的习题原始文本...",
  "total_count": 5,
  "generation_time": 8.5
}
```

##### GET `/v1/exercise/list/{user_id}/{course_id}/{lesson_num}`
**功能**: 获取习题列表

##### GET `/v1/exercise/{user_id}/{course_id}/{lesson_num}/{filename}`
**功能**: 获取习题详情

##### DELETE `/v1/exercise/{user_id}/{course_id}/{lesson_num}/{filename}`
**功能**: 删除习题文件

##### GET `/v1/exercise/status`
**功能**: 获取习题生成状态

##### POST `/exercise`
**功能**: 简化版习题生成接口

---

### 7. 会话管理接口 (Session Management)

#### 7.1 对话管理

##### GET `/v1/users/{user_id}/sessions/{session_id}/dialogues`
**功能**: 获取指定会话的对话历史

**参数**:
- `user_id`: 用户ID
- `session_id`: 会话ID
- `limit`: 返回记录数限制 (默认10)
- `is_teacher`: 是否为教师 (默认false)

**响应**:
```json
{
  "user_id": "user123",
  "session_id": "session456",
  "is_teacher": false,
  "dialogues": [
    {
      "timestamp": "2023-12-01T10:00:00Z",
      "role": "user",
      "content": "你好"
    },
    {
      "timestamp": "2023-12-01T10:00:01Z",
      "role": "assistant",
      "content": "你好！有什么可以帮助您的吗？"
    }
  ],
  "count": 2
}
```

##### DELETE `/v1/users/{user_id}/sessions/{session_id}/dialogues`
**功能**: 清除指定会话的所有对话历史

#### 7.2 上下文管理

##### GET `/v1/users/{user_id}/sessions/{session_id}/context`
**功能**: 获取指定会话的上下文消息

**参数**:
- `user_id`: 用户ID
- `session_id`: 会话ID
- `max_messages`: 最大消息数 (默认10)
- `is_teacher`: 是否为教师 (默认false)

#### 7.3 会话信息

##### GET `/v1/users/{user_id}/sessions/{session_id}/info`
**功能**: 获取会话信息

##### GET `/v1/users/{user_id}/sessions`
**功能**: 获取用户的所有会话ID

**响应**:
```json
{
  "user_id": "user123",
  "is_teacher": false,
  "sessions": ["session456", "session789"],
  "session_count": 2
}
```

#### 7.4 会话保存与加载

##### POST `/v1/users/{user_id}/sessions/{session_id}/save`
**功能**: 保存当前会话的完整历史记录

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
      "content": "你好！有什么可以帮助您的吗？"
    }
  ]
}
```

##### GET `/v1/users/{user_id}/sessions/{session_id}/load`
**功能**: 加载指定会话的历史记录

---

### 8. 状态管理接口 (State Management)

#### 8.1 状态缓存管理

##### POST `/disable-state-cache`
**功能**: 禁用状态缓存

**响应**: `"success"`

##### POST `/enable-state-cache`
**功能**: 启用状态缓存

**响应**: `"success"`

##### POST `/reset-state`
**功能**: 重置状态缓存

**响应**: `"success"`

---

### 9. 系统接口 (System APIs)

#### 9.1 根接口

##### GET `/`
**功能**: 根路径，返回欢迎消息

**响应**:
```json
{
  "Hello": "World!"
}
```

#### 9.2 系统控制

##### POST `/exit`
**功能**: 退出服务器 (仅非部署模式下可用)

**响应**: 服务器关闭

---

## 错误处理

### 标准错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

### 常见错误代码
- `400 Bad Request`: 请求参数错误
- `403 Forbidden`: 权限不足 (部署模式下)
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

---

## 使用示例

### 1. 完整的文件上传和问答流程

```python
import requests

# 1. 上传文件
files = {'file': open('lesson01.pdf', 'rb')}
data = {
    'session_id': 'session123',
    'user_id': 'teacher001',
    'is_teacher': True,
    'course_id': 'MATH101',
    'lesson_num': 'lesson01',
    'is_resource': False,
    'is_ask': False
}

response = requests.post('http://localhost:8001/v1/upload', files=files, data=data)
print(response.json())

# 2. 智能问答
qa_data = {
    'query': '什么是微积分？',
    'user_id': 'teacher001',
    'session_id': 'session123',
    'is_teacher': True,
    'course_id': 'MATH101',
    'lesson_num': 'lesson01',
    'search_mode': 'existing',
    'top_k': 3
}

response = requests.post('http://localhost:8001/v1/qa', json=qa_data)
print(response.json())
```

### 2. 生成教学大纲

```python
import requests

outline_data = {
    'user_id': 'teacher001',
    'session_id': 'session123',
    'course_id': 'MATH101',
    'lesson_num': 'lesson01',
    'is_teacher': True,
    'max_words': 1000
}

response = requests.post('http://localhost:8001/v1/create/outline', json=outline_data)
print(response.json())
```

### 3. 生成习题

```python
import requests

exercise_data = {
    'user_id': 'teacher001',
    'session_id': 'session123',
    'course_id': 'MATH101',
    'lesson_num': 'lesson01',
    'is_teacher': True,
    'question_count': 5,
    'difficulty': 'medium'
}

response = requests.post('http://localhost:8001/v1/exercise/generate', json=exercise_data)
print(response.json())
```

---

## 部署说明

### 环境要求
- Python 3.8+
- CUDA 11.8+ (如果使用GPU)
- ChromaDB服务器

### 启动服务
```bash
# 启动ChromaDB服务器
chroma run --host localhost --port 8000

# 启动主服务器
python main.py --port 8001 --host 0.0.0.0
```

### 配置文件
主要配置项位于 `config/settings.py` 中：
- `CHROMADB_HOST`: ChromaDB服务器地址
- `CHROMADB_PORT`: ChromaDB服务器端口
- `TEACHERS_DIR`: 教师文件存储目录
- `STUDENTS_DIR`: 学生文件存储目录
- `BGEM3_MODEL_PATH`: BGEM3模型路径
- `BGE_RERANKER_MODEL_PATH`: BGE重排序模型路径

---

## 更新日志

### 版本 2.0.0 (当前版本)
- 从FAISS迁移到ChromaDB
- 集成BGEM3嵌入模型和BGE重排序模型
- 支持RWKV-RAG架构
- 新增教学大纲和习题生成功能
- 完善会话管理系统
- 添加文件下载和列表功能

### 版本 1.0.0
- 基础的RWKV聊天功能
- FAISS向量数据库支持
- 基本的文件上传和问答功能 