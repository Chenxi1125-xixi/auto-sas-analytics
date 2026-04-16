#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/xixi/auto-sas-analytics"

mkdir -p "$ROOT/docs"
mkdir -p "$ROOT/apps/api/app/core"
mkdir -p "$ROOT/apps/api/app/db"

cat > "$ROOT/README.md" <<'EOF2'
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
EOF2

cat > "$ROOT/docs/mvp-architecture.md" <<'EOF2'
# MVP 架构设计（后端优先）

## 目标

先打通最小后端运行链路：

- FastAPI 服务可启动
- 健康检查可访问
- 数据库连接可初始化
- 为后续上传、任务、执行器扩展预留结构

## 技术选型

- API: FastAPI
- ORM: SQLAlchemy 2.x
- DB: SQLite（开发默认），后续可切 PostgreSQL
- 配置: pydantic-settings

## 目录约定

apps/api/
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  └─ config.py
│  └─ db/
│     └─ session.py
├─ requirements.txt
└─ .env.example

## 运行流程（当前）

- main.py 启动 FastAPI
- config.py 读取环境变量
- session.py 创建 SQLAlchemy engine / SessionLocal
- GET /health 用于服务探活

## 下一步（P0 后续）

- 增加模型：UploadedFile / AnalysisTemplate / AnalysisTask
- 增加上传接口：POST /api/uploads
- 增加任务接口：POST /api/tasks
- 增加执行接口：POST /api/tasks/{task_id}/run（先 mock）
EOF2

cat > "$ROOT/apps/api/requirements.txt" <<'EOF2'
fastapi==0.115.12
uvicorn[standard]==0.34.2
sqlalchemy==2.0.40
pydantic-settings==2.9.1
python-multipart==0.0.20
EOF2

cat > "$ROOT/apps/api/.env.example" <<'EOF2'
APP_NAME="Auto SAS Analytics API"
APP_ENV="development"
DEBUG=true
DATABASE_URL="sqlite:///./apps/api/local.db"
STORAGE_ROOT="storage"
EOF2

cat > "$ROOT/apps/api/app/main.py" <<'EOF2'
from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
EOF2

cat > "$ROOT/apps/api/app/core/config.py" <<'EOF2'
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Auto SAS Analytics API"
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)

    database_url: str = Field(default="sqlite:///./apps/api/local.db")
    storage_root: str = Field(default="storage")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
EOF2

cat > "$ROOT/apps/api/app/db/session.py" <<'EOF2'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF2

echo "setup.sh created successfully"
