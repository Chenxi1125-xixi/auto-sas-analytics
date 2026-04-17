from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis_task import AnalysisTask
from app.models.analysis_template import AnalysisTemplate
from app.models.task_status import TaskStatus
from app.models.uploaded_file import UploadedFile
from app.schemas.task import TaskCreateRequest, TaskDetail, TaskListItem, TaskRunResponse
from app.services.task_executor import execute_task


def _parse_json(value: str | None) -> dict:
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def _to_task_list_item(task: AnalysisTask, template: AnalysisTemplate | None) -> TaskListItem:
    return TaskListItem(
        id=task.id,
        template_id=task.template_id,
        template_slug=template.slug if template else None,
        template_name=template.name if template else None,
        template_engine=getattr(template, "engine", None) if template else None,
        uploaded_file_id=task.uploaded_file_id,
        status=task.status,
        delimiter=task.delimiter,
        created_at=task.created_at,
    )


def _to_task_detail(task: AnalysisTask, template: AnalysisTemplate | None) -> TaskDetail:
    return TaskDetail(
        id=task.id,
        uploaded_file_id=task.uploaded_file_id,
        template_id=task.template_id,
        template_slug=template.slug if template else None,
        template_name=template.name if template else None,
        template_engine=getattr(template, "engine", None) if template else None,
        status=task.status,
        delimiter=task.delimiter,
        has_header=task.has_header,
        params_json=_parse_json(task.params_json),
        artifacts=_parse_json(task.artifacts_json),
        error_message=task.error_message or None,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def list_tasks(db: Session) -> list[TaskListItem]:
    stmt = select(AnalysisTask).order_by(AnalysisTask.created_at.desc())
    tasks = list(db.scalars(stmt).all())

    template_ids = {t.template_id for t in tasks}
    templates = {}
    if template_ids:
        t_stmt = select(AnalysisTemplate).where(AnalysisTemplate.id.in_(template_ids))
        templates = {tpl.id: tpl for tpl in db.scalars(t_stmt).all()}

    return [_to_task_list_item(task, templates.get(task.template_id)) for task in tasks]


def get_task(db: Session, task_id: str) -> TaskDetail | None:
    stmt = select(AnalysisTask).where(AnalysisTask.id == task_id)
    task = db.scalar(stmt)
    if task is None:
        return None

    template = db.get(AnalysisTemplate, task.template_id)
    return _to_task_detail(task, template)


def _resolve_template(db: Session, req: TaskCreateRequest) -> AnalysisTemplate | None:
    if req.template_id is not None:
        stmt = select(AnalysisTemplate).where(AnalysisTemplate.id == req.template_id)
    else:
        stmt = select(AnalysisTemplate).where(AnalysisTemplate.slug == req.template_slug)
    return db.scalar(stmt)


def create_task(db: Session, req: TaskCreateRequest, storage_root: str) -> TaskDetail:
    uploaded_file = db.get(UploadedFile, req.uploaded_file_id)
    if uploaded_file is None:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    template = _resolve_template(db, req)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    task = AnalysisTask(
        id=str(uuid4()),
        uploaded_file_id=uploaded_file.id,
        template_id=template.id,
        delimiter=req.delimiter,
        has_header=req.has_header,
        status=TaskStatus.PENDING.value,
        params_json=json.dumps(req.params_json),
        artifacts_json="{}",
        error_message="",
    )

    Path(storage_root).mkdir(parents=True, exist_ok=True)
    (Path(storage_root) / "results" / task.id).mkdir(parents=True, exist_ok=True)

    db.add(task)
    db.commit()
    db.refresh(task)
    return _to_task_detail(task, template)


def run_task(
    db: Session,
    task_id: str,
    storage_root: str,
    sas_command: str,
    sas_timeout_seconds: int,
) -> TaskRunResponse:
    return execute_task(db, task_id, storage_root, sas_command, sas_timeout_seconds)
