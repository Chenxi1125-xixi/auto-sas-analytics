from fastapi import APIRouter, Depends, HTTPException
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
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskDetail)
def create_new_task(req: TaskCreateRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    return create_task(db, req, settings.storage_root)


@router.post("/{task_id}/run", response_model=TaskRunResponse)
def run_existing_task(task_id: str, db: Session = Depends(get_db)):
    settings = get_settings()
    return run_task(
        db,
        task_id,
        settings.storage_root,
        getattr(settings, "sas_command", "sas"),
        getattr(settings, "sas_run_timeout_seconds", 600),
    )
