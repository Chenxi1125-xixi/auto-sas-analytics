import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.uploaded_file import UploadedFile


def _detect_file_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".txt":
        return "txt"
    raise ValueError("Only .csv and .txt are supported")


def save_upload(db: Session, storage_root: str, file: UploadFile) -> UploadedFile:
    file_type = _detect_file_type(file.filename or "")
    upload_id = str(uuid.uuid4())
    target = Path(storage_root) / "uploads" / f"{upload_id}_{file.filename}"
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    model = UploadedFile(
        id=upload_id,
        filename=file.filename or "unknown",
        file_type=file_type,
        storage_path=str(target),
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model
