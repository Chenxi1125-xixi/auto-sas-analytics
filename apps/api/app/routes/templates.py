from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.template import TemplateResponse
from app.services.template_service import list_templates

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=list[TemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    return list_templates(db)
