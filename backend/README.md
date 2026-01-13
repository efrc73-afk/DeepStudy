# DeepStudy 后端开发指南

## 技术栈

- **框架**: FastAPI
- **LLM 框架**: LlamaIndex
- **模型**: ModelScope API (Qwen-2.5)
- **数据库**: Neo4j (知识图谱) + SQLite (用户数据)
- **认证**: JWT

## 项目结构

```
backend/
├── api/                 # API Layer
│   ├── routes/          # 路由定义
│   ├── middleware/    # 中间件（JWT）
│   └── schemas/         # Pydantic 模型
├── agent/               # Agent Layer
│   ├── orchestrator.py  # 编排器
│   ├── intent_router.py # 意图识别
│   ├── prompts/         # Prompt 模板
│   └── strategies/      # 处理策略
├── data/                # Data Layer
│   ├── neo4j_client.py  # Neo4j 客户端
│   ├── vector_store.py  # 向量存储
│   └── sqlite_db.py     # SQLite 操作
├── config.py            # 配置管理
└── main.py              # 应用入口
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填入配置：

```env
MODELSCOPE_API_KEY=your_api_key
NEO4J_PASSWORD=your_neo4j_password
JWT_SECRET_KEY=your_jwt_secret
```

### 3. 初始化数据库

#### SQLite

SQLite 数据库会在应用启动时自动创建表结构。

#### Neo4j

1. 安装 Neo4j Desktop 或 Neo4j Community Edition
2. 创建数据库
3. 启动 Neo4j 服务
4. 在 `.env` 中配置连接信息

### 4. 启动服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API 文档访问：`http://localhost:8000/docs`

## API 协议

### 认证

#### 注册
```
POST /api/auth/register
Body: {username, email, password}
Response: {access_token, token_type, user_id, username}
```

#### 登录
```
POST /api/auth/login
Body: {username, password}
Response: {access_token, token_type, user_id, username}
```

### 聊天

#### 发送消息
```
POST /api/chat
Headers: Authorization: Bearer <token>
Body: {query, parent_id?}
Response: {answer, fragments, knowledge_triples, conversation_id, parent_id}
```

#### 递归追问
```
POST /api/chat/recursive
Headers: Authorization: Bearer <token>
Body: {parent_id, fragment_id, query}
Response: {answer, fragments, knowledge_triples, conversation_id, parent_id}
```

#### 获取对话树
```
GET /api/chat/conversation/{conversation_id}
Headers: Authorization: Bearer <token>
Response: {id, query, answer, parent_id, children, created_at}
```

### 思维导图

#### 获取思维导图
```
GET /api/mindmap/{conversation_id}
Headers: Authorization: Bearer <token>
Response: {nodes: [...], edges: [...]}
```

## 开发规范

1. **代码风格**: 使用 Black + isort
2. **类型提示**: 所有函数使用类型注解
3. **错误处理**: 统一使用 HTTPException
4. **文档**: 使用 JSDoc 风格注释

## 数据库初始化

### SQLite 表结构

**users 表**:
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- email (TEXT UNIQUE)
- hashed_password (TEXT)
- created_at (TEXT)

**conversations 表**:
- id (TEXT PRIMARY KEY)
- user_id (INTEGER)
- parent_id (TEXT)
- query (TEXT)
- answer (TEXT)
- created_at (TEXT)

### Neo4j 节点和关系

节点标签：
- `Topic`: 知识主题
- `Concept`: 概念

关系类型：
- `RELATED_TO`: 相关关系
- `PART_OF`: 部分关系
- `REQUIRES`: 前置知识关系

## 待实现功能

1. **意图识别**: 完善 Few-shot 提示词
2. **Chat-to-Graph**: 从对话中提取知识三元组并构建图谱
3. **向量检索**: 实现对话历史的向量检索和 Rerank
4. **学习画像**: 计算掌握度热力图和生成诊断报告

## 常见问题

### 1. ModelScope API 调用失败

检查：
- API Key 是否正确
- 网络连接是否正常
- API Base URL 是否正确

### 2. Neo4j 连接失败

检查：
- Neo4j 服务是否启动
- 连接 URI、用户名、密码是否正确

### 3. JWT Token 过期

Token 默认 24 小时过期，可在 `.env` 中配置 `JWT_EXPIRATION_HOURS`。

## 环境变量配置

### 快速开始

1. 复制环境变量模板：

```bash
cd backend
copy .env.example .env
# 或者在 Linux/Mac 上：
# cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的配置信息（开发环境可以先用占位值）：

- `MODELSCOPE_API_KEY`: 你的 ModelScope API Key
- `NEO4J_PASSWORD`: 你的 Neo4j 密码（如果使用本地 Neo4j）
- `JWT_SECRET_KEY`: 用于 JWT 签名的密钥（建议使用随机字符串）

### 环境变量说明

#### ModelScope API

- `MODELSCOPE_API_KEY`: **必填** - ModelScope API 密钥  
- `MODELSCOPE_API_BASE`: API 基础地址（默认：`https://api.modelscope.cn/v1`）

#### Neo4j

- `NEO4J_URI`: Neo4j 连接地址（默认：`bolt://localhost:7687`）
- `NEO4J_USER`: Neo4j 用户名（默认：`neo4j`）
- `NEO4J_PASSWORD`: **必填** - Neo4j 密码

#### JWT

- `JWT_SECRET_KEY`: **必填** - JWT 签名密钥（生产环境请使用强随机字符串）
- `JWT_ALGORITHM`: JWT 算法（默认：`HS256`）
- `JWT_EXPIRATION_HOURS`: Token 过期时间（小时，默认：`24`）

#### 数据库

- `SQLITE_DB_PATH`: SQLite 数据库路径（默认：`./data/deepstudy.db`）
- `VECTOR_STORE_PATH`: 向量存储路径（默认：`./data/vector_store`）

#### CORS

- `CORS_ORIGINS`: 允许的跨域来源（JSON 数组格式，默认：`["http://localhost:5173","http://localhost:3000"]`）

#### 服务器

- `API_HOST`: 服务器监听地址（默认：`0.0.0.0`）
- `API_PORT`: 服务器端口（默认：`8000`）

### 注意事项

1. **不要将 `.env` 文件提交到 Git**（已在 `.gitignore` 中排除）
2. 生产环境请使用强随机字符串作为 `JWT_SECRET_KEY`
3. 如果暂时没有 ModelScope API Key，可以先使用占位值，但 Agent 相关功能将无法真正调用云端模型
4. 如果暂时没有 Neo4j，可以先使用占位值，但知识图谱相关功能将不可用

