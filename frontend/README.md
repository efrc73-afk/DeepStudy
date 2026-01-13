# DeepStudy 前端开发指南

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **路由**: React Router v6
- **HTTP 客户端**: Axios
- **图表**: ReactFlow
- **Markdown 渲染**: react-markdown + KaTeX

## 项目结构

```
frontend/
├── src/
│   ├── components/      # UI 组件
│   │   ├── Auth/        # 登录/注册
│   │   ├── Chat/        # 聊天界面
│   │   ├── MindMap/     # 思维导图
│   │   └── Markdown/    # Markdown 渲染
│   ├── services/        # API 服务
│   ├── hooks/           # React Hooks
│   ├── types/           # TypeScript 类型
│   └── utils/           # 工具函数
├── package.json
└── vite.config.ts
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

### 构建生产版本

```bash
npm run build
```

## 核心组件说明

### 1. ChatInterface

主聊天界面组件，包含：
- 消息列表展示
- 输入框和发送功能
- 思维导图侧边栏
- 划词选择监听

### 2. TextFragment

Markdown 文本片段组件，功能：
- 渲染 Markdown 和数学公式（KaTeX）
- 为代码块和公式注入唯一 ID
- 监听文本选择事件，触发递归追问

### 3. KnowledgeGraph

知识图谱组件，使用 ReactFlow：
- 接收后端返回的 nodes/edges 数据
- 可视化展示知识图谱
- 支持节点点击交互

### 4. API 服务

`src/services/api.ts` 封装了所有 API 调用：
- 自动添加 JWT token
- 处理 token 过期
- 统一的错误处理

## 开发规范

1. **代码风格**: 使用 ESLint + Prettier
2. **类型安全**: 所有 API 调用使用 TypeScript 类型
3. **组件复用**: 遵循单一职责原则
4. **错误处理**: 统一使用 try-catch 和错误提示

## 环境变量

创建 `.env.local` 文件（可选）：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## 常见问题

### 1. 跨域问题

开发环境下，Vite 已配置代理，将 `/api` 请求转发到后端。

### 2. Token 管理

Token 存储在 `localStorage`，过期后自动跳转到登录页。

### 3. ReactFlow 样式

确保导入 `reactflow/dist/style.css`。
