from app.db.base import Base
from app.db.session import engine
from app.models import analysis_task, analysis_template, uploaded_file  # noqa: F401


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
