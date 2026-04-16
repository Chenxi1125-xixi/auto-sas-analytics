from pydantic import BaseModel


class UploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    storage_path: str

    model_config = {"from_attributes": True}
