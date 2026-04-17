from __future__ import annotations

import json
from pathlib import Path

from app.runners.python_runner import PythonRunner


def test_python_runner_generates_report_and_protocol_files(tmp_path: Path) -> None:
    data_path = tmp_path / "sample.csv"
    data_path.write_text("a,b,c\n1,2,x\n3,,y\n4,6,x\n", encoding="utf-8")

    output_dir = tmp_path / "result"
    report_html_path = str(output_dir / "report" / "report.html")
    run_log_path = str(output_dir / "logs" / "run.log")
    summary_path = str(output_dir / "summary.json")
    manifest_path = str(output_dir / "manifest.json")

    runner = PythonRunner()
    result = runner.run(
        input_file=str(data_path),
        output_dir=str(output_dir),
        delimiter="comma",
        has_header=True,
        report_html_path=report_html_path,
        run_log_path=run_log_path,
        summary_path=summary_path,
        manifest_path=manifest_path,
        template_slug="descriptive-report-python",
        task_id="task-test-1",
    )

    assert result.row_count == 3
    assert Path(report_html_path).exists()
    assert Path(run_log_path).exists()
    assert Path(summary_path).exists()
    assert Path(manifest_path).exists()
    assert (output_dir / "tables" / "summary.csv").exists()

    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))

    assert summary["status"] == "completed"
    assert summary["row_count"] == 3
    assert manifest["status"] == "completed"
    assert "report_html" in manifest["artifacts"]
