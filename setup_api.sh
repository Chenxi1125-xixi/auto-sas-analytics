#!/usr/bin/env bash
set -euo pipefail

BASE="/Users/xixi/auto-sas-analytics/apps/api"

mkdir -p \
  "$BASE/app/core" \
  "$BASE/app/db" \
  "$BASE/app/models" \
  "$BASE/app/routes" \
  "$BASE/app/schemas" \
  "$BASE/app/services" \
  "$BASE/tests" \
  "$BASE/storage/uploads" \
  "$BASE/storage/results"

cat <<'EOF2' > "$BASE/requirements.txt"
fastapi==0.111.0
uvicorn==0.30.1
sqlalchemy==2.0.30
pydantic==2.8.2
python-multipart==0.0.9
pytest==8.2.2
httpx==0.27.0
EOF2

cat <<'EOF2' > "$BASE/app/__init__.py"
EOF2

cat <<'EOF2' > "$BASE/app/core/__init__.py"
EOF2

cat <<'EOF2' > "$BASE/app/core/config.py"
from functools import lru_cache
from pathlib import Path


class Settings:
    app_name: str = "Auto SAS Analytics API"
    debug: bool = True
    database_url: str = "sqlite:///./storage/app.db"
    storage_root: str = str(Path(__file__).resolve().parents[2] / "storage")
    frontend_origin: str = "http://127.0.0.1:3000"
    sas_command: str = "sas"
    sas_run_timeout_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
EOF2

cat <<'EOF2' > "$BASE/app/db/__init__.py"
EOF2

cat <<'EOF2' > "$BASE/app/db/base.py"
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
EOF2

cat <<'EOF2' > "$BASE/app/db/session.py"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF2

cat <<'EOF2' > "$BASE/app/models/task_status.py"
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
EOF2

cat <<'EOF2' > "$BASE/app/models/uploaded_file.py"
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
EOF2

cat <<'EOF2' > "$BASE/app/models/analysis_template.py"
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisTemplate(Base):
    __tablename__ = "analysis_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sas_script_path: Mapped[str] = mapped_column(String(1024), nullable=False, default="app/templates/descriptive_report.sas")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
EOF2

cat <<'EOF2' > "$BASE/app/models/analysis_task.py"
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.task_status import TaskStatus


class AnalysisTask(Base):
    __tablename__ = "analysis_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    uploaded_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("uploaded_files.id"), nullable=False)
    template_id: Mapped[str] = mapped_column(String(36), ForeignKey("analysis_templates.id"), nullable=False)
    delimiter: Mapped[str] = mapped_column(String(16), nullable=False, default="comma")
    has_header: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=TaskStatus.PENDING.value)
    params_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    artifacts_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    uploaded_file = relationship("UploadedFile")
    template = relationship("AnalysisTemplate")
EOF2

cat <<'EOF2' > "$BASE/app/models/__init__.py"
from app.models.analysis_task import AnalysisTask
from app.models.analysis_template import AnalysisTemplate
from app.models.task_status import TaskStatus
from app.models.uploaded_file import UploadedFile

__all__ = ["AnalysisTask", "AnalysisTemplate", "TaskStatus", "UploadedFile"]
EOF2

cat <<'EOF2' > "$BASE/app/db/init_db.py"
from app.db.base import Base
from app.db.session import engine
from app.models import analysis_task, analysis_template, uploaded_file  # noqa: F401


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
EOF2

cat <<'EOF2' > "$BASE/app/db/seed.py"
from sqlalchemy.orm import Session

from app.models.analysis_template import AnalysisTemplate


def seed_data(db: Session) -> None:
    exists = db.query(AnalysisTemplate).filter(AnalysisTemplate.slug == "descriptive-report").first()
    if exists:
        return

    db.add(
        AnalysisTemplate(
            slug="descriptive-report",
            name="Descriptive Report",
            description="Basic descriptive statistics report template",
            sas_script_path="app/templates/descriptive_report.sas",
        )
    )
    db.commit()
EOF2

cat <<'EOF2' > "$BASE/app/schemas/upload.py"
from pydantic import BaseModel


class UploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    storage_path: str

    model_config = {"from_attributes": True}
EOF2

cat <<'EOF2' > "$BASE/app/schemas/template.py"
from pydantic import BaseModel


class TemplateResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: str

    model_config = {"from_attributes": True}
EOF2

cat <<'EOF2' > "$BASE/app/schemas/task.py"
from pydantic import BaseModel, Field
from typing import Any


class TaskCreateRequest(BaseModel):
    uploaded_file_id: str
    template_slug: str
    delimiter: str = Field(default="comma", pattern="^(comma|tab|space)$")
    has_header: bool = True
    params_json: dict[str, Any] = Field(default_factory=dict)


class TaskListItem(BaseModel):
    id: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}


class TaskDetail(BaseModel):
    id: str
    status: str
    uploaded_file_id: str
    template_id: str
    delimiter: str
    has_header: bool
    params_json: dict[str, Any]
    artifacts: dict[str, str]
    error_message: str | None = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class TaskRunResponse(BaseModel):
    id: str
    status: str
    artifacts: dict[str, str]
    error_message: str | None = None
EOF2

cat <<'EOF2' > "$BASE/app/schemas/__init__.py"
from app.schemas.task import TaskCreateRequest, TaskDetail, TaskListItem, TaskRunResponse
from app.schemas.template import TemplateResponse
from app.schemas.upload import UploadResponse

__all__ = [
    "TaskCreateRequest",
    "TaskDetail",
    "TaskListItem",
    "TaskRunResponse",
    "TemplateResponse",
    "UploadResponse",
]
EOF2

cat <<'EOF2' > "$BASE/app/services/upload_service.py"
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.uploaded_file import UploadedFile


def _detect_file_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".txt":
        return "txt"
    raise ValueError("Only .csv and .txt are supported")


def save_upload(db: Session, storage_root: str, file: UploadFile) -> UploadedFile:
    file_type = _detect_file_type(file.filename or "")
    upload_id = str(uuid.uuid4())
    target = Path(storage_root) / "uploads" / f"{upload_id}_{file.filename}"
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    model = UploadedFile(
        id=upload_id,
        filename=file.filename or "unknown",
        file_type=file_type,
        storage_path=str(target),
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model
EOF2

cat <<'EOF2' > "$BASE/app/services/template_service.py"
from sqlalchemy.orm import Session

from app.models.analysis_template import AnalysisTemplate


def list_templates(db: Session) -> list[AnalysisTemplate]:
    return db.query(AnalysisTemplate).order_by(AnalysisTemplate.created_at.desc()).all()


def get_template_by_slug(db: Session, slug: str) -> AnalysisTemplate | None:
    return db.query(AnalysisTemplate).filter(AnalysisTemplate.slug == slug).first()
EOF2

cat <<'EOF2' > "$BASE/app/services/task_executor.py"
import json
from datetime import datetime
from pathlib import Path

from app.models.analysis_task import AnalysisTask
from app.models.task_status import TaskStatus


def run_task_mock(task: AnalysisTask, storage_root: str) -> AnalysisTask:
    task.status = TaskStatus.RUNNING.value
    task.updated_at = datetime.utcnow()

    result_dir = Path(storage_root) / "results" / task.id
    result_dir.mkdir(parents=True, exist_ok=True)

    report_path = result_dir / "report.html"
    log_path = result_dir / "run.log"

    params = {}
    try:
        params = json.loads(task.params_json or "{}")
    except Exception:
        params = {}

    if params.get("force_fail") is True:
        log_path.write_text("status: failed\nreason: forced failure\n", encoding="utf-8")
        task.status = TaskStatus.FAILED.value
        task.error_message = "forced failure"
        task.artifacts_json = json.dumps({"run_log": str(log_path)})
    else:
        report_path.write_text("<html><body><h1>Mock SAS Report</h1></body></html>", encoding="utf-8")
        log_path.write_text("status: success\n", encoding="utf-8")
        task.status = TaskStatus.COMPLETED.value
        task.error_message = ""
        task.artifacts_json = json.dumps({"report": str(report_path), "run_log": str(log_path)})

    task.updated_at = datetime.utcnow()
    return task
EOF2

cat <<'EOF2' > "$BASE/app/services/task_service.py"
import json
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.analysis_task import AnalysisTask
from app.models.task_status import TaskStatus
from app.models.uploaded_file import UploadedFile
from app.schemas.task import TaskCreateRequest
from app.services.task_executor import run_task_mock
from app.services.template_service import get_template_by_slug


def _to_task_detail(task: AnalysisTask) -> dict:
    try:
        params = json.loads(task.params_json or "{}")
    except Exception:
        params = {}
    try:
        artifacts = json.loads(task.artifacts_json or "{}")
    except Exception:
        artifacts = {}

    return {
        "id": task.id,
        "status": task.status,
        "uploaded_file_id": task.uploaded_file_id,
        "template_id": task.template_id,
        "delimiter": task.delimiter,
        "has_header": task.has_header,
        "params_json": params,
        "artifacts": artifacts,
        "error_message": task.error_message or None,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


def list_tasks(db: Session) -> list[dict]:
    tasks = db.query(AnalysisTask).order_by(AnalysisTask.created_at.desc()).all()
    return [{"id": t.id, "status": t.status, "created_at": t.created_at.isoformat()} for t in tasks]


def get_task(db: Session, task_id: str) -> dict | None:
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    return _to_task_detail(task) if task else None


def create_task(db: Session, req: TaskCreateRequest) -> dict:
    upload = db.query(UploadedFile).filter(UploadedFile.id == req.uploaded_file_id).first()
    if upload is None:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    template = get_template_by_slug(db, req.template_slug)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    task = AnalysisTask(
        uploaded_file_id=upload.id,
        template_id=template.id,
        delimiter=req.delimiter,
        has_header=req.has_header,
        status=TaskStatus.PENDING.value,
        params_json=json.dumps(req.params_json or {}),
        artifacts_json="{}",
        error_message="",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _to_task_detail(task)


def run_task(db: Session, task_id: str, storage_root: str) -> dict:
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.PENDING.value:
        raise HTTPException(status_code=409, detail="Task is not pending")

    task = run_task_mock(task, storage_root)
    db.add(task)
    db.commit()
    db.refresh(task)

    detail = _to_task_detail(task)
    return {
        "id": detail["id"],
        "status": detail["status"],
        "artifacts": detail["artifacts"],
        "error_message": detail["error_message"],
    }
EOF2

cat <<'EOF2' > "$BASE/app/services/__init__.py"
from app.services.task_service import create_task, get_task, list_tasks, run_task
from app.services.template_service import list_templates
from app.services.upload_service import save_upload

__all__ = ["create_task", "get_task", "list_tasks", "run_task", "list_templates", "save_upload"]
EOF2

cat <<'EOF2' > "$BASE/app/routes/health.py"
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
EOF2

cat <<'EOF2' > "$BASE/app/routes/templates.py"
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.template import TemplateResponse
from app.services.template_service import list_templates

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=list[TemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    return list_templates(db)
EOF2

cat <<'EOF2' > "$BASE/app/routes/uploads.py"
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.upload import UploadResponse
from app.services.upload_service import save_upload

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("", response_model=UploadResponse)
def create_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    try:
        return save_upload(db, settings.storage_root, file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
EOF2

cat <<'EOF2' > "$BASE/app/routes/tasks.py"
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.task import TaskCreateRequest, TaskDetail, TaskListItem, TaskRunResponse
from app.services.task_service import create_task, get_task, list_tasks, run_task

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskListItem])
def get_tasks(db: Session = Depends(get_db)):
    return list_tasks(db)


@router.get("/{task_id}", response_model=TaskDetail)
def get_task_detail(task_id: str, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if task is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskDetail)
def create_new_task(req: TaskCreateRequest, db: Session = Depends(get_db)):
    return create_task(db, req)


@router.post("/{task_id}/run", response_model=TaskRunResponse)
def run_task_api(task_id: str, db: Session = Depends(get_db)):
    settings = get_settings()
    return run_task(db, task_id, settings.storage_root)
EOF2

cat <<'EOF2' > "$BASE/app/routes/__init__.py"
from app.routes.health import router as health_router
from app.routes.tasks import router as tasks_router
from app.routes.templates import router as templates_router
from app.routes.uploads import router as uploads_router

__all__ = ["health_router", "tasks_router", "templates_router", "uploads_router"]
EOF2

cat <<'EOF2' > "$BASE/app/main.py"
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.init_db import create_tables
from app.db.seed import seed_data
from app.db.session import SessionLocal
from app.routes.health import router as health_router
from app.routes.tasks import router as tasks_router
from app.routes.templates import router as templates_router
from app.routes.uploads import router as uploads_router

settings = get_settings()
Path(settings.storage_root).mkdir(parents=True, exist_ok=True)
Path(settings.storage_root, "uploads").mkdir(parents=True, exist_ok=True)
Path(settings.storage_root, "results").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(templates_router)
app.include_router(uploads_router)
app.include_router(tasks_router)
EOF2

cat <<'EOF2' > "$BASE/tests/test_health.py"
from fastapi.testclient import TestClient

from app.main import app


def test_health_check():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
EOF2

cat <<'EOF2' > "$BASE/tests/test_templates.py"
from fastapi.testclient import TestClient

from app.main import app


def test_list_templates_smoke():
    client = TestClient(app)
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(item["slug"] == "descriptive-report" for item in data)
EOF2

cat <<'EOF2' > "$BASE/tests/test_writes.py"
import io

from fastapi.testclient import TestClient

from app.main import app


def test_upload_create_run_smoke():
    client = TestClient(app)

    upload_resp = client.post(
        "/api/uploads",
        files={"file": ("sample.csv", io.BytesIO(b"a,b\n1,2\n"), "text/csv")},
    )
    assert upload_resp.status_code == 200
    upload_id = upload_resp.json()["id"]

    create_resp = client.post(
        "/api/tasks",
        json={
            "uploaded_file_id": upload_id,
            "template_slug": "descriptive-report",
            "delimiter": "comma",
            "has_header": True,
            "params_json": {},
        },
    )
    assert create_resp.status_code == 200
    task_id = create_resp.json()["id"]

    list_resp = client.get("/api/tasks")
    assert list_resp.status_code == 200
    assert any(t["id"] == task_id for t in list_resp.json())

    detail_resp = client.get(f"/api/tasks/{task_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["status"] == "pending"

    run_resp = client.post(f"/api/tasks/{task_id}/run")
    assert run_resp.status_code == 200
    assert run_resp.json()["status"] in ("completed", "failed")
EOF2

echo "MVP backend files created under: $BASE"
echo "Run:"
echo "  cd $BASE"
echo "  python3 -m venv .venv && source .venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  PYTHONPATH=. pytest -q"
echo "  PYTHONPATH=. uvicorn app.main:app --reload --port 8000"
