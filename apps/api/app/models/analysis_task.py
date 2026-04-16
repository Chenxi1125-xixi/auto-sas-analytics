import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.task_status import TaskStatus


class AnalysisTask(Base):
    __tablename__ = "analysis_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    uploaded_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("uploaded_files.id"), nullable=False)
    template_id: Mapped[str] = mapped_column(String(36), ForeignKey("analysis_templates.id"), nullable=False)
    delimiter: Mapped[str] = mapped_column(String(16), nullable=False, default="comma")
    has_header: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=TaskStatus.PENDING.value)
    params_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    artifacts_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    uploaded_file = relationship("UploadedFile")
    template = relationship("AnalysisTemplate")
