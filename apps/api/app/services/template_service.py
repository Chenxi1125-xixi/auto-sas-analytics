from sqlalchemy.orm import Session

from app.models.analysis_template import AnalysisTemplate


def list_templates(db: Session) -> list[AnalysisTemplate]:
    return db.query(AnalysisTemplate).order_by(AnalysisTemplate.created_at.desc()).all()


def get_template_by_slug(db: Session, slug: str) -> AnalysisTemplate | None:
    return db.query(AnalysisTemplate).filter(AnalysisTemplate.slug == slug).first()
