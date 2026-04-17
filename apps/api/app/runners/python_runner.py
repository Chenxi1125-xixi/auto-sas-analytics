from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


DELIMITER_MAP = {
    "comma": ",",
    "tab": "\t",
    "space": r"\s+",
}


@dataclass
class PythonRunResult:
    row_count: int | None
    message: str


class PythonRunner:
    def run(
        self,
        *,
        input_file: str,
        output_dir: str,
        delimiter: str,
        has_header: bool,
        report_html_path: str,
        run_log_path: str,
        summary_path: str,
        manifest_path: str,
        template_slug: str = "descriptive-report-python",
        task_id: str | None = None,
    ) -> PythonRunResult:
        output_root = Path(output_dir)
        tables_dir = output_root / "tables"
        figures_dir = output_root / "figures"
        report_dir = output_root / "report"
        logs_dir = output_root / "logs"

        tables_dir.mkdir(parents=True, exist_ok=True)
        figures_dir.mkdir(parents=True, exist_ok=True)
        report_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        if delimiter not in DELIMITER_MAP:
            raise RuntimeError(f"Unsupported delimiter: {delimiter}")

        separator = DELIMITER_MAP[delimiter]
        header = 0 if has_header else None

        read_kwargs: dict[str, object] = {"header": header}
        if delimiter == "space":
            read_kwargs["sep"] = separator
            read_kwargs["engine"] = "python"
        else:
            read_kwargs["sep"] = separator

        started_at = datetime.utcnow().isoformat() + "Z"
        input_path = Path(input_file)

        df = pd.read_csv(input_path, **read_kwargs)
        if not has_header:
            df.columns = [f"column_{idx + 1}" for idx in range(df.shape[1])]

        row_count, col_count = int(df.shape[0]), int(df.shape[1])

        missing_counts = df.isna().sum().astype(int)
        missing_df = (
            missing_counts.rename("missing_count")
            .to_frame()
            .assign(missing_ratio=lambda d: (d["missing_count"] / max(row_count, 1)).round(4))
            .reset_index(names="column")
        )

        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.shape[1] > 0:
            numeric_summary = numeric_df.describe().transpose().reset_index(names="column")
        else:
            numeric_summary = pd.DataFrame(
                columns=["column", "count", "mean", "std", "min", "25%", "50%", "75%", "max"]
            )

        categorical_df = df.select_dtypes(exclude=["number"])
        categorical_rows: list[dict[str, object]] = []
        for column in categorical_df.columns:
            value_counts = categorical_df[column].fillna("<NA>").astype(str).value_counts().head(10)
            for value, count in value_counts.items():
                categorical_rows.append(
                    {
                        "column": column,
                        "value": value,
                        "count": int(count),
                    }
                )
        categorical_summary = pd.DataFrame(categorical_rows)

        pd.DataFrame(
            {
                "metric": ["rows", "columns", "numeric_columns", "categorical_columns"],
                "value": [row_count, col_count, numeric_df.shape[1], categorical_df.shape[1]],
            }
        ).to_csv(tables_dir / "summary.csv", index=False)

        missing_df.to_csv(tables_dir / "missing_overview.csv", index=False)
        numeric_summary.to_csv(tables_dir / "numeric_describe.csv", index=False)
        categorical_summary.to_csv(tables_dir / "categorical_frequency_top10.csv", index=False)

        histogram_rel_path: str | None = None
        if numeric_df.shape[1] > 0:
            first_col = numeric_df.columns[0]
            fig_path = figures_dir / "histogram.png"
            plt.figure(figsize=(8, 4.5))
            numeric_df[first_col].dropna().hist(bins=20)
            plt.title(f"Histogram of {first_col}")
            plt.xlabel(str(first_col))
            plt.ylabel("Frequency")
            plt.tight_layout()
            plt.savefig(fig_path)
            plt.close()
            histogram_rel_path = "figures/histogram.png"

        report_html = self._build_report_html(
            row_count=row_count,
            col_count=col_count,
            delimiter=delimiter,
            has_header=has_header,
            missing_preview=missing_df.head(20).to_html(index=False),
            numeric_preview=numeric_summary.head(20).to_html(index=False),
            categorical_preview=(
                categorical_summary.head(30).to_html(index=False)
                if not categorical_summary.empty
                else "<p>No categorical columns detected.</p>"
            ),
            histogram_rel_path=histogram_rel_path,
        )

        Path(report_html_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_html_path).write_text(report_html, encoding="utf-8")

        completed_at = datetime.utcnow().isoformat() + "Z"
        Path(run_log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(run_log_path).write_text(
            "\n".join(
                [
                    f"started_at: {started_at}",
                    f"completed_at: {completed_at}",
                    f"step: read_input ({input_path})",
                    "step: compute_missing_overview",
                    "step: compute_numeric_describe",
                    "step: compute_categorical_frequency",
                    "step: write_tables_csv",
                    "step: write_html_report",
                    "status: success",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        summary_data = {
            "task_id": task_id or output_root.name,
            "template": template_slug,
            "row_count": row_count,
            "column_count": col_count,
            "message": "Python analysis completed successfully.",
            "status": "completed",
        }
        Path(summary_path).write_text(json.dumps(summary_data, indent=2), encoding="utf-8")

        manifest_data = {
            "task_id": task_id or output_root.name,
            "template": template_slug,
            "status": "completed",
            "generated_at": completed_at,
            "artifacts": {
                "report_html": report_html_path,
                "run_log": run_log_path,
                "summary": summary_path,
                "manifest": manifest_path,
            },
        }
        Path(manifest_path).write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

        return PythonRunResult(
            row_count=row_count,
            message="Python analysis completed successfully.",
        )

    @staticmethod
    def _build_report_html(
        *,
        row_count: int,
        col_count: int,
        delimiter: str,
        has_header: bool,
        missing_preview: str,
        numeric_preview: str,
        categorical_preview: str,
        histogram_rel_path: str | None,
    ) -> str:
        figure_html = (
            f'<img src="../{histogram_rel_path}" alt="Histogram" style="max-width: 100%;" />'
            if histogram_rel_path
            else "<p>No numeric column found for histogram.</p>"
        )

        return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Descriptive Report (Python)</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 24px; line-height: 1.4; }}
      h1, h2 {{ margin-bottom: 8px; }}
      table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
      th, td {{ border: 1px solid #ddd; padding: 6px 8px; font-size: 13px; }}
      th {{ background: #f5f5f5; }}
      .meta {{ background: #fafafa; border: 1px solid #eee; padding: 12px; margin-bottom: 18px; }}
    </style>
  </head>
  <body>
    <h1>Descriptive Report (Python Engine)</h1>
    <div class="meta">
      <p><strong>Rows:</strong> {row_count}</p>
      <p><strong>Columns:</strong> {col_count}</p>
      <p><strong>Delimiter:</strong> {delimiter}</p>
      <p><strong>Has Header:</strong> {has_header}</p>
    </div>

    <h2>Missing Value Overview</h2>
    {missing_preview}

    <h2>Numeric Describe</h2>
    {numeric_preview}

    <h2>Categorical Frequency (Top 10 each)</h2>
    {categorical_preview}

    <h2>Histogram</h2>
    {figure_html}
  </body>
</html>
""".strip()
