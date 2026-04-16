from pydantic import BaseModel


class TemplateResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: str

    model_config = {"from_attributes": True}
