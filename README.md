# DeepStudy

基于 ModelScope 的递归学习 Agent

## 技术栈

- **前端**: React + TypeScript + ReactFlow + Vite
- **后端**: FastAPI + LlamaIndex
- **模型**: Qwen-2.5-Coder / Qwen-2.5-72B (ModelScope API)
- **数据库**: Neo4j (知识图谱) + SQLite (用户数据)

## 项目结构

```
DeepStudy/
├── frontend/          # React 前端应用
├── backend/           # FastAPI 后端服务
├── .env.example       # 环境变量模板
└── README.md          # 项目说明
```

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.10
- Neo4j Desktop 或 Neo4j Community Edition

### 配置 conda 环境

``` bash
# 创建新的 conda 环境（Python 3.10）
conda create -n deepstudy python=3.10

# 激活环境
conda activate deepstudy
```

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd DeepStudy
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置信息
```

3. 启动后端
```bash
# 安装依赖
cd backend
pip install -r requirements.txt
# 返回根目录
cd ..
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

详细开发指南请参考：
- [前端开发指南](frontend/README.md)
- [后端开发指南](backend/README.md)

## 开发规范

- 使用 Git 分支管理：`main` 分支保持稳定，功能开发使用 `feature/*` 分支
- 代码风格：前端 ESLint + Prettier，后端 Black + isort
- 提交前确保代码可运行，测试通过后再合并到 `main`
