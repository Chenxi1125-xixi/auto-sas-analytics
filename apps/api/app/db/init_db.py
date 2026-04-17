from __future__ import annotations

from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "analysis_templates" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("analysis_templates")}
    with engine.begin() as connection:
        if "runner_type" not in columns:
            connection.execute(text("ALTER TABLE analysis_templates ADD COLUMN runner_type VARCHAR(50)"))
            connection.execute(
                text("UPDATE analysis_templates SET runner_type = 'sas' WHERE runner_type IS NULL")
            )

        if "engine" not in columns:
            connection.execute(text("ALTER TABLE analysis_templates ADD COLUMN engine VARCHAR(50)"))
            connection.execute(
                text("UPDATE analysis_templates SET engine = COALESCE(runner_type, 'sas') WHERE engine IS NULL")
            )

        if "is_active" not in columns:
            connection.execute(text("ALTER TABLE analysis_templates ADD COLUMN is_active BOOLEAN"))
            connection.execute(
                text("UPDATE analysis_templates SET is_active = 1 WHERE is_active IS NULL")
            )
