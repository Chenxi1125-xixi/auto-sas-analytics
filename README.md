# auto-sas-analytics

这是一个用于自动化 SAS 数据分析平台的 MVP 仓库。  
当前阶段先提供**最小可运行后端骨架**（FastAPI + SQLAlchemy）。

## 项目结构（当前）

auto-sas-analytics/
├─ apps/
│  └─ api/
│     ├─ app/
│     │  ├─ main.py
│     │  ├─ core/config.py
│     │  └─ db/session.py
│     ├─ requirements.txt
│     └─ .env.example
└─ docs/
   └─ mvp-architecture.md

## 后端快速启动

1. 创建虚拟环境并安装依赖

cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. 准备环境变量

cp .env.example .env

3. 启动服务

cd apps/api
source .venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --reload --port 8000

4. 验证服务

curl http://127.0.0.1:8000/health

预期返回：
{"status":"ok","app":"Auto SAS Analytics API"}

## 说明

- 默认数据库为本地 SQLite：apps/api/local.db
- 此阶段仅实现基础骨架，不包含真实 SAS 调用
