from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class TaskCreateRequest(BaseModel):
    uploaded_file_id: str
    template_id: str | None = None
    template_slug: str | None = None
    delimiter: str = Field(pattern="^(comma|tab|space)$")
    has_header: bool = True
    params_json: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_template_reference(self):
        has_template_id = self.template_id is not None
        has_template_slug = self.template_slug is not None
        if has_template_id == has_template_slug:
            raise ValueError("Provide exactly one of template_id or template_slug")
        return self


class TaskListItem(BaseModel):
    id: str
    template_id: str
    template_slug: str | None = None
    template_name: str | None = None
    template_engine: str | None = None
    uploaded_file_id: str
    status: str
    delimiter: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskDetail(BaseModel):
    id: str
    uploaded_file_id: str
    template_id: str
    template_slug: str | None = None
    template_name: str | None = None
    template_engine: str | None = None
    status: str
    delimiter: str
    has_header: bool
    params_json: dict
    artifacts: dict[str, str]
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskRunResponse(BaseModel):
    id: str
    status: str
    artifacts: dict[str, str]
    error_message: str | None = None
