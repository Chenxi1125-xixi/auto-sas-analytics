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
