# AI功能接口文档

本文件整理了 Intelligent-Teaching-Assistant-Platform/backend-python 中所有主要 AI 相关接口，包括接口路径、请求方式、请求参数、返回值说明等。

---

## 1. 习题生成相关接口

### 1.1 生成课后习题
- **接口**：`POST /v1/exercise/generate`
- **请求体**（JSON）：
```json
{
  "user_id": "teacher123",
  "session_id": "session456",
  "course_id": "math101",
  "lesson_num": "lesson01",
  "is_teacher": true,
  "question_count": 5,
  "difficulty": "medium", // 可选: easy/medium/hard
  "max_tokens": 2000,
  "temperature": 0.7,
  "generation_mode": "block" // 可选: block/whole
}
```
- **返回**：
```json
{
  "success": true,
  "message": "习题生成成功",
  "data": "习题原始文本",
  "total_count": 5,
  "generation_time": 2.34
}
```

### 1.2 基于知识点生成即时练习题
- **接口**：`POST /v1/practice/generate_instant`
- **请求体**（JSON）：
```json
{
  "knowledge_point": "牛顿第二定律",
  "difficulty": "medium" // 可选: easy/medium/hard
}
```
- **返回**：
```json
{
  "success": true,
  "message": "即时练习题目生成成功",
  "data": "习题原始文本",
  "knowledge_point": "牛顿第二定律",
  "difficulty": "medium"
}
```

### 1.3 获取/下载/删除习题文件
- **获取列表**：`GET /v1/exercise/list/{user_id}/{course_id}/{lesson_num}?is_teacher=false`
- **获取详情**：`GET /v1/exercise/{user_id}/{course_id}/{lesson_num}/{filename}?is_teacher=false`
- **下载文件**：`GET /v1/exercise/download/{user_id}/{course_id}/{lesson_num}/{filename}?is_teacher=false`
- **删除文件**：`DELETE /v1/exercise/{user_id}/{course_id}/{lesson_num}/{filename}?is_teacher=false`

---

## 2. 智能问答相关接口

### 2.1 智能问答
- **接口**：`POST /v1/qa`
- **请求体**（JSON）：
```json
{
  "query": "什么是进程？",
  "user_id": "teacher123",
  "session_id": "session456",
  "is_teacher": true,
  "course_id": "MATH101", // existing模式下必填
  "lesson_num": "lesson01", // existing模式下必填
  "top_k": 3,
  "search_mode": "existing", // existing 或 uploaded
  "max_tokens": 1000,
  "temperature": 0.7,
  "use_context": true
}
```
- **返回**：
```json
{
  "success": true,
  "message": "问答成功",
  "data": "AI回答内容"
}
```

---

## 3. 知识库相关接口

### 3.1 知识库搜索
- **接口**：`POST /v1/knowledge/search`
- **请求体**（JSON）：
```json
{
  "query": "牛顿第二定律",
  "user_id": "teacher123",
  "is_teacher": true,
  "course_id": "math101",
  "lesson_num": "lesson01",
  "is_ask": false,
  "top_k": 5,
  "use_rerank": true
}
```
- **返回**：
```json
{
  "query": "牛顿第二定律",
  "results": [ ... ],
  "total_results": 5,
  "collection_name": "kb_teacher123_math101_lesson01",
  "use_rerank": true
}
```

### 3.2 删除知识库 collection
- **接口**：`DELETE /v1/knowledge/collection?collection_name=xxx`
- **返回**：
```json
{
  "message": "成功删除collection: xxx",
  "collection_name": "xxx"
}
```

---

## 4. 文件上传/下载相关接口

### 4.1 上传文件
- **接口**：`POST /v1/upload`
- **请求体**：`multipart/form-data`
  - file: 文件（pdf/docx/md/txt）
  - session_id: string
  - user_id: string
  - is_teacher: bool
  - course_id: string (部分场景必填)
  - lesson_num: string (部分场景必填)
  - file_encoding: string (默认utf-8)
  - is_resource: bool
  - is_ask: bool
- **返回**：
```json
{
  "message": "文件已成功上传",
  ... // 其他上传信息
}
```

### 4.2 下载学习资料
- **接口**：`GET /v1/download/resource/{user_id}/{course_id}/{filename}?is_teacher=true`

### 4.3 列出学习资料
- **接口**：`GET /v1/list/resources/{user_id}/{course_id}?is_teacher=true`

---

## 5. 教学设计生成接口

### 5.1 生成教学设计
- **接口**：`POST /v1/create/content_design`
- **请求体**（JSON）：
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
- **返回**：
```json
{
  "success": true,
  "message": "教学设计生成成功",
  "data": "教学设计内容"
}
```

---

## 6. 会话管理相关接口

### 6.1 获取/清除/保存会话
- **获取会话列表**：`GET /v1/users/{user_id}/sessions?is_teacher=false`
- **清除会话历史**：`DELETE /v1/users/{user_id}/sessions/{session_id}/dialogues?is_teacher=false`
- **保存会话历史**：`POST /v1/users/{user_id}/sessions/{session_id}/save?is_teacher=false`
  - body: messages: List[Dict[str, Any]]

---

## 7. 聊天/对话接口

### 7.1 AI对话
- **接口**：`POST /v1/chat/completions`
- **请求体**（JSON）：
```json
{
  "messages": [
    {"role": "user", "content": "你好，请介绍一下自己"}
  ],
  "model": "rwkv",
  "stream": false,
  "user_id": "user123",
  "session_id": "session456",
  "is_teacher": false
}
```
- **返回**：
```json
{
  "choices": [ ... ],
  ... // 其他OpenAI风格返回
}
```

---

## 8. 其他

- 还有部分调试、状态、知识库管理等接口，详见各路由文件。

---

> **注：** 所有接口均建议带上必要的身份、会话等参数。部分接口参数有默认值，具体以实际代码为准。 