import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/tiff"}
ALLOWED_PDF_TYPES = {"application/pdf"}
ALLOWED_EXCEL_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}


def save_upload_file(upload_file: UploadFile, subfolder: str) -> str:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    dest_dir = Path(settings.UPLOAD_DIR) / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(upload_file.filename).suffix
    unique_name = f"{uuid.uuid4()}{ext}"
    dest_path = dest_dir / unique_name

    size = 0
    with open(dest_path, "wb") as f:
        for chunk in iter(lambda: upload_file.file.read(1024 * 1024), b""):
            size += len(chunk)
            if size > max_bytes:
                f.close()
                os.remove(dest_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB} MB.",
                )
            f.write(chunk)

    return str(dest_path)


def validate_file_type(upload_file: UploadFile, allowed_types: set[str]) -> None:
    if upload_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{upload_file.content_type}'. Allowed: {allowed_types}",
        )
