from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request
from sqlalchemy.orm import Session
from database.db import get_db
from utils.pdf_util import extract_and_save_pdf
from utils.image_util import extract_and_save_image
from utils.video_util import extract_and_save_video
from utils.i18n import translate, get_lang_from_request

router = APIRouter(prefix="/api", tags=["Document"])

@router.post("/extract-pdf-text")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    user_id: int = Query(..., description="ID of the user uploading the document"),
    instructions: Optional[str] = Query(default=None, description="Optional instructions"),
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return await extract_and_save_pdf(db, file, user_id, instructions)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("pdf_processing_error", lang)
        )

@router.post("/extract-text-from-image/")
async def extract_text_from_image_route(
    request: Request,
    file: UploadFile = File(...),
    user_id: int = Query(..., description="ID of the user uploading the image"),
    instructions: Optional[str] = Query(default=None, description="Optional instructions"),
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return await extract_and_save_image(db, file, user_id, instructions)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("image_processing_error", lang)
        )

@router.post("/extract-text-from-video/")
async def process_video(
    request: Request,
    file: UploadFile = File(...),
    user_id: int = Query(...),
    instructions: Optional[str] = Query(default=None, description="Optional instructions"),
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return await extract_and_save_video(db, file, user_id, instructions)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("video_processing_error", lang)
        )
