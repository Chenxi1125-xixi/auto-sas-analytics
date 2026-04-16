from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.upload import UploadResponse
from app.services.upload_service import save_upload

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("", response_model=UploadResponse)
def create_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    try:
        return save_upload(db, settings.storage_root, file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
