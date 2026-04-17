from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.analysis_task import AnalysisTask
from app.models.analysis_template import AnalysisTemplate
from app.models.task_status import TaskStatus
from app.models.uploaded_file import UploadedFile
from app.runners.python_runner import PythonRunner
from app.schemas.task import TaskRunResponse


def _now() -> datetime:
    return datetime.utcnow()


def _parse_json(value: str | None) -> dict:
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def _build_public_artifacts(task_id: str) -> dict[str, str]:
    base_url = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    return {
        "report_html": f"{base_url}/storage/results/{task_id}/report/report.html",
        "run_log": f"{base_url}/storage/results/{task_id}/logs/run.log",
        "summary": f"{base_url}/storage/results/{task_id}/summary.json",
        "manifest": f"{base_url}/storage/results/{task_id}/manifest.json",
    }


def execute_task(
    db: Session,
    task_id: str,
    storage_root: str,
    sas_command: str,
    sas_timeout_seconds: int = 600,
) -> TaskRunResponse:
    task = db.get(AnalysisTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.PENDING.value:
        raise HTTPException(status_code=409, detail="Only pending tasks can be executed")

    template = db.get(AnalysisTemplate, task.template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    uploaded = db.get(UploadedFile, task.uploaded_file_id)
    if uploaded is None:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    task.status = TaskStatus.RUNNING.value
    task.updated_at = _now()
    db.add(task)
    db.commit()
    db.refresh(task)

    result_dir = Path(storage_root) / "results" / task.id
    report_html_path = str(result_dir / "report" / "report.html")
    run_log_path = str(result_dir / "logs" / "run.log")
    summary_path = str(result_dir / "summary.json")
    manifest_path = str(result_dir / "manifest.json")

    public_artifacts = _build_public_artifacts(task.id)
    params = _parse_json(task.params_json)

    try:
        engine = (getattr(template, "engine", None) or "sas").lower()

        if engine == "python":
            runner = PythonRunner()
            run_result = runner.run(
                input_file=uploaded.storage_path,
                output_dir=str(result_dir),
                delimiter=task.delimiter,
                has_header=task.has_header,
                report_html_path=report_html_path,
                run_log_path=run_log_path,
                summary_path=summary_path,
                manifest_path=manifest_path,
                template_slug=template.slug,
                task_id=task.id,
            )
        else:
            raise RuntimeError(
                "SAS engine path is not upgraded yet. Please use descriptive-report-python for now."
            )

        task.status = TaskStatus.COMPLETED.value
        task.error_message = ""
        task.artifacts_json = json.dumps(public_artifacts)
        task.updated_at = _now()
        db.add(task)
        db.commit()
        db.refresh(task)

        return TaskRunResponse(
            id=task.id,
            status=task.status,
            artifacts=public_artifacts,
            error_message=None,
        )

    except Exception as exc:
        result_dir.mkdir(parents=True, exist_ok=True)
        Path(run_log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(run_log_path).write_text(
            f"status: failed\nerror: {exc}\n",
            encoding="utf-8",
        )

        task.status = TaskStatus.FAILED.value
        task.error_message = str(exc)
        task.artifacts_json = json.dumps({"run_log": public_artifacts["run_log"]})
        task.updated_at = _now()
        db.add(task)
        db.commit()
        db.refresh(task)

        return TaskRunResponse(
            id=task.id,
            status=task.status,
            artifacts={"run_log": public_artifacts["run_log"]},
            error_message=str(exc),
        )
