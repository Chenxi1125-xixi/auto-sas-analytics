from pydantic import BaseModel, Field
from typing import Any


class TaskCreateRequest(BaseModel):
    uploaded_file_id: str
    template_slug: str
    delimiter: str = Field(default="comma", pattern="^(comma|tab|space)$")
    has_header: bool = True
    params_json: dict[str, Any] = Field(default_factory=dict)


class TaskListItem(BaseModel):
    id: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}


class TaskDetail(BaseModel):
    id: str
    status: str
    uploaded_file_id: str
    template_id: str
    delimiter: str
    has_header: bool
    params_json: dict[str, Any]
    artifacts: dict[str, str]
    error_message: str | None = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class TaskRunResponse(BaseModel):
    id: str
    status: str
    artifacts: dict[str, str]
    error_message: str | None = None
