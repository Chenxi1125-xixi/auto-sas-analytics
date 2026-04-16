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
