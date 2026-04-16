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
