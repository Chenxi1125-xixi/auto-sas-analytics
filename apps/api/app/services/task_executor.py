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
        task.artifacts_json = json.dumps(
            {
                "run_log": f"http://127.0.0.1:8000/storage/results/{task.id}/run.log"
            }
        )
    else:
        report_path.write_text("<html><body><h1>Mock SAS Report</h1></body></html>", encoding="utf-8")
        log_path.write_text("status: success\n", encoding="utf-8")
        task.status = TaskStatus.COMPLETED.value
        task.error_message = ""
        task.artifacts_json = json.dumps(
            {
                "report": f"http://127.0.0.1:8000/storage/results/{task.id}/report.html",
                "run_log": f"http://127.0.0.1:8000/storage/results/{task.id}/run.log",
            }
        )

    task.updated_at = datetime.utcnow()
    return task
