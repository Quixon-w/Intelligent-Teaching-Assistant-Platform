# Intelligent-Teaching-Assistant-Platform
Intelligent Teaching Assistant Platform (ITAP) 是一个融合人工智能与教育科学的智能辅助平台，旨在为教师和学习者提供全周期教学支持。通过实时数据分析、个性化内容推荐和自动化流程管理，ITAP 优化教学效率、提升学习成效，构建“教-学-评-练”一体化的智能教育生态。

---

# 🎓 智能教学助手平台

## 项目简介

本项目旨在开发一个基于开源大语言模型的智能教学助手平台，聚焦于教学过程的**备课设计自动化**、**学生个性化练习辅导**以及**教学数据分析可视化**，助力教育数字化转型，提升实训教学效率与个性化水平。

该项目采用前后端分离架构，模块清晰，便于团队协作。平台整合了本地知识库与大模型能力，实现从“教师教”到“AI辅助教”，从“学生练”到“AI智能练”。

---

## 🎯 项目功能

### 教师端功能

* 智能备课设计（基于课程大纲生成教学内容）
* 自动生成考核题目（选择题）
* 学情分析与建议（学生答题批改与趋势报告）
* 教学资源导出与管理

### 学生端功能

* 课程选择与查询筛选
* 在线练习与错题反馈
* 智能问答助手（结合本地课程知识）

### 管理端功能

* 用户管理（教师、学生、管理员）
* 课程管理（课件、试题等）

---

## 📦 技术栈

| 模块    | 技术                                                  |
| ----- | --------------------------------------------------- |
| 前端    | Vue 3 + Vite + Element Plus + ECharts + Pinia      |
| 后端    | Java 17 + Spring Boot 3.4.3 + MyBatis Plus + MySQL + Redis |
| 大模型服务 | Python + FastAPI + RWKV + ChromaDB + LangChain |
| 知识库构建 | BGE-M3嵌入模型 + 文档向量化 + 重排序模型 |

---

## 👥 团队分工

| 成员 | 负责模块                   |
| -- | ---------------------- |
| 王乾旭  | 大模型服务开发与知识库构建、后端开发（模型服务集成）、前端界面开发 |
| 洪宇灿  | 后端开发（接口开发、数据处理）、测试与整理、可视化开发 |

---

## 📁 项目结构说明

```
Intelligent-Teaching-Assistant-Platform/
├── backend/                          # Java后端服务
│   ├── src/main/java/org/cancan/usercenter/
│   │   ├── controller/               # 控制器层（API接口）
│   │   │   ├── UserController.java   # 用户管理接口
│   │   │   ├── CoursesController.java # 课程管理接口
│   │   │   ├── LessonsController.java # 课程管理接口
│   │   │   ├── QuestionsController.java # 题目管理接口
│   │   │   └── ...
│   │   ├── service/                  # 业务逻辑层
│   │   │   ├── impl/                # 服务实现类
│   │   │   ├── UserService.java     # 用户服务接口
│   │   │   ├── CoursesService.java  # 课程服务接口
│   │   │   └── ...
│   │   ├── mapper/                  # 数据访问层
│   │   │   ├── UserMapper.java      # 用户数据访问
│   │   │   ├── CoursesMapper.java   # 课程数据访问
│   │   │   └── ...
│   │   ├── model/domain/            # 数据模型
│   │   │   ├── User.java           # 用户实体
│   │   │   ├── Courses.java        # 课程实体
│   │   │   ├── request/            # 请求对象
│   │   │   └── response/           # 响应对象
│   │   ├── common/                  # 公共组件
│   │   │   ├── BaseResponse.java   # 统一响应格式
│   │   │   ├── ErrorCode.java      # 错误码定义
│   │   │   └── ResultUtils.java    # 响应工具类
│   │   └── utils/                   # 工具类
│   │       ├── RedisUtil.java      # Redis工具
│   │       └── ...
│   ├── src/main/resources/
│   │   ├── application.yml          # 应用配置
│   │   └── mapper/                 # MyBatis映射文件
│   └── pom.xml                     # Maven依赖配置
├── backend-python/                  # Python大模型服务
│   ├── config/                      # 配置文件
│   │   ├── settings.py             # 主配置文件
│   │   ├── database.py             # 数据库配置
│   │   └── env_example.env         # 环境变量示例
│   ├── routes/                      # API路由
│   │   ├── completion.py           # 文本补全接口
│   │   ├── qa.py                   # 问答接口
│   │   ├── exercise.py             # 练习生成接口
│   │   ├── knowledge.py            # 知识库管理
│   │   └── ...
│   ├── rwkv_pip/                   # RWKV模型相关
│   │   ├── model.py                # 模型加载
│   │   ├── rwkv_tokenizer.py       # 分词器
│   │   └── ...
│   ├── utils/                       # 工具模块
│   │   ├── rwkv.py                 # RWKV模型工具
│   │   ├── knowledge.py            # 知识库工具
│   │   └── ...
│   ├── main.py                     # 服务启动入口
│   └── requirements.txt             # Python依赖
├── vue-ui/                          # Vue3前端应用
│   ├── src/
│   │   ├── components/             # 组件目录
│   │   │   ├── ai/                # AI相关组件
│   │   │   ├── role/              # 角色相关组件
│   │   │   │   ├── admin/         # 管理员组件
│   │   │   │   ├── teacher/       # 教师组件
│   │   │   │   └── student/       # 学生组件
│   │   │   └── ...
│   │   ├── views/                  # 页面视图
│   │   │   ├── admin/             # 管理员页面
│   │   │   ├── teacher/           # 教师页面
│   │   │   ├── student/           # 学生页面
│   │   │   └── ...
│   │   ├── api/                    # API接口
│   │   │   ├── auth.js            # 认证接口
│   │   │   ├── course.js          # 课程接口
│   │   │   └── ...
│   │   ├── router/                 # 路由配置
│   │   ├── stores/                 # 状态管理
│   │   └── utils/                  # 工具函数
│   ├── package.json                # 前端依赖配置
│   └── vite.config.js              # Vite构建配置
├── itap.sql                         # 数据库初始化脚本
└── README.md                        # 项目说明文档
```

---

## 🧪 接口示例（由后端封装调用模型服务）

### 用户管理接口

```http
# 用户注册
POST /api/user/register
Content-Type: application/json

{
  "userAccount": "teacher001",
  "userPassword": "123456",
  "checkPassword": "123456",
  "userRole": 1
}

# 用户登录
POST /api/user/login
Content-Type: application/json

{
  "userAccount": "teacher001",
  "userPassword": "123456"
}

# 获取当前用户信息
GET /api/user/current
Authorization: Bearer {session_token}
```

### 课程管理接口

```http
# 创建课程
POST /api/courses/create
Content-Type: application/json

{
  "courseName": "Java程序设计",
  "courseDescription": "Java基础编程课程",
  "courseOutline": "1. Java基础语法\n2. 面向对象编程\n3. 集合框架"
}

# 获取课程列表
GET /api/courses/list?pageNum=1&pageSize=10
Authorization: Bearer {session_token}
```

### AI服务接口

```http
# 智能问答
POST /api/ai/qa
Content-Type: application/json

{
  "question": "什么是面向对象编程？",
  "context": "Java程序设计课程",
  "userId": "123"
}

# 生成练习题
POST /api/ai/exercise
Content-Type: application/json

{
  "courseId": "course_001",
  "lessonNum": "1",
  "difficulty": "medium",
  "questionType": "multiple_choice",
  "count": 5
}

# 上传知识文档
POST /api/ai/upload
Content-Type: multipart/form-data

{
  "file": "course_material.pdf",
  "userId": "123",
  "courseId": "course_001",
  "lessonNum": "1"
}
```

---

## 🏁 启动指南

### 环境要求

- **Java**: JDK 17+
- **Python**: Python 3.8+
- **Node.js**: Node.js 16+
- **MySQL**: MySQL 8.0+
- **Redis**: Redis 6.0+
- **CUDA**: 12.6

### 1. 数据库初始化

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE itap CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入数据表结构
mysql -u root -p itap < itap.sql
```

建表语句中无默认账户，需自己手动在数据库中添加管理员

### 2. 后端服务启动

```bash
# 进入后端目录
cd backend

# 修改数据库配置
# 编辑 src/main/resources/application.yml
# 修改数据库连接信息

# 启动Java后端服务
mvn spring-boot:run
# 或使用IDE直接运行 UserCenterApplication.java
```

### 3. Python大模型服务启动

```bash
# 进入Python服务目录
cd backend-python

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp config/env_example.env .env
# 编辑 .env 文件，配置模型路径、数据库连接等

# 启动ChromaDB向量数据库与大模型服务
python main.py 
```

### 4. 前端应用启动

```bash
# 进入前端目录
cd vue-ui

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 5. 访问应用

- **前端应用**: http://localhost:3000
- **后端API文档**: http://localhost:8080/api/swagger-ui
- **Python服务**: http://localhost:8001

### 6. 模型文件与其他文件准备

将RWKV模型文件放置在 `path_to_your_workspace/model/` 目录下：
- RWKV-x060-World-7B-v3-20241112-ctx4096.pth或其他RWKV模型
- bge-m3 嵌入模型
- bge-reranker-v2-m3 重排序模型
其他缺少的文件较多，需自行前往RWKV模型库中下载添加

---

## 📚 免责声明

本项目仅为学生实训实践项目，目的为教育实训，涉及的大模型及其使用需遵守相应开源协议。

---

