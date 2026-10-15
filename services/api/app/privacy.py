from datetime import UTC, datetime, timedelta
from uuid import uuid4
from fastapi import HTTPException, UploadFile
from .config import Settings

IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

def create_upload_intent(purpose: str, consent: bool, retention: str, settings: Settings) -> dict:
    if not consent:
        raise HTTPException(status_code=422, detail="Explicit consent is required for visual analysis")
    expires = datetime.now(UTC) + (timedelta(hours=1) if retention == "one_hour" else timedelta(minutes=15))
    return {"asset_id": str(uuid4()), "purpose": purpose, "expires_at": expires.isoformat(), "instructions": "Upload endpoint is intentionally disabled until MinIO signed-URL configuration and malware scanning are enabled."}

async def validate_image(upload: UploadFile, settings: Settings) -> bytes:
    if upload.content_type not in IMAGE_MIME_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG and WEBP files are accepted")
    content = await upload.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB limit")
    if not content:
        raise HTTPException(status_code=422, detail="Image is empty")
    return content

