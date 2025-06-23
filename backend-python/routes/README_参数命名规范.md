# 路由参数命名规范修改说明

## 概述
所有路由接口的参数命名已统一为小驼峰格式（camelCase），删除下划线命名方式。

## 修改的文件

### 1. completion.py
**修改内容：**
- `session_id` → `sessionId`
- `courseID` → `courseId`
- `user_name` → `userName`
- `assistant_name` → `assistantName`
- `system_name` → `systemName`
- `tool_choice` → `toolChoice`
- `max_tokens` → `maxTokens`
- `top_p` → `topP`
- `presence_penalty` → `presencePenalty`
- `frequency_penalty` → `frequencyPenalty`

### 2. upload.py
**修改内容：**
- `session_id` → `sessionId`
- `courseID` → `courseId`
- `file_encoding` → `fileEncoding`
- `Is_Resource` → `isResource`
- `Is_Outline` → `isOutline`
- `Is_Ask` → `isAsk`

**新增功能：**
- 只支持PDF和DOCX文件格式
- 添加知识库更新失败的错误处理，返回`knowledgeError`字段

### 3. create.py
**修改内容：**
- `session_id` → `sessionId`
- `courseID` → `courseId`
- `max_words` → `maxWords`

### 4. search.py
**修改内容：**
- `session_id` → `sessionId`
- `courseID` → `courseId`
- `top_k` → `topK`
- `search_mode` → `searchMode`

### 5. exercise.py
**修改内容：**
- `session_id` → `sessionId`
- `courseID` → `courseId`
- `target_count` → `targetCount`

### 6. download.py
**修改内容：**
- `session_id` → `sessionId`
- `course_id` → `courseId`
- `lesson_num` → `lessonNum`
- `download_url` → `downloadUrl`
- `total_files` → `totalFiles`
- `created_time` → `createdTime`

## 接口测试示例

### 1. 聊天完成接口
```json
{
  "messages": [
    {
      "role": "user",
      "content": "你好",
      "raw": false
    }
  ],
  "model": "rwkv",
  "stream": false,
  "sessionId": "test_session_001",
  "isTeacher": false,
  "courseId": null,
  "maxTokens": 1000,
  "temperature": 1.0,
  "topP": 0.3,
  "presencePenalty": 0,
  "frequencyPenalty": 1
}
```

### 2. 文件上传接口
```form-data
file: [PDF或DOCX文件]
sessionId: "teacher_session_001"
isTeacher: true
courseId: "MATH101"
isResource: true
fileEncoding: "utf-8"
```

### 3. 创建大纲接口
```json
{
  "sessionId": "teacher_session_001",
  "courseId": "MATH101",
  "lessonNum": "lesson01",
  "maxWords": 1000
}
```

### 4. 搜索接口
```json
{
  "query": "什么是微积分？",
  "sessionId": "session123",
  "isTeacher": false,
  "courseId": "MATH101",
  "lessonNum": "lesson01",
  "topK": 2,
  "searchMode": "existing"
}
```

### 5. 习题生成接口
```json
{
  "sessionId": "teacher_session_001",
  "courseId": "MATH101",
  "lessonNum": "lesson01",
  "targetCount": 10
}
```

## 注意事项

1. **文件格式限制**：upload接口现在只支持PDF和DOCX格式
2. **错误处理**：upload接口会返回知识库更新状态，包括失败时的错误信息
3. **参数验证**：所有接口都保持原有的参数验证逻辑
4. **向后兼容**：建议前端同步更新参数命名

## 测试建议

1. 使用Postman测试所有接口的参数命名
2. 验证文件上传的文件格式限制
3. 测试知识库更新失败的错误处理
4. 确认所有响应字段也使用小驼峰命名 