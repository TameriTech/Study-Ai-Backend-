from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from database.db import get_db
from utils.pdf_util import extract_and_save_pdf
from utils.image_util import extract_and_save_image
from utils.video_util import extract_and_save_video
router = APIRouter(prefix="/api", tags=["Document"])

    

@router.post("/extract-pdf-text")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: int = Query(..., description="ID of the user uploading the document"),
    instructions: Optional[str] = Query(default=None, description="Optional instructions"),  # ✅ Properly optional
    db: Session = Depends(get_db)
):
    return await extract_and_save_pdf(db, file, user_id, instructions)

@router.post("/extract-text-from-image/")
async def extract_text_from_image_route(
    file: UploadFile = File(...),
    user_id: int = Query(..., description="ID of the user uploading the image"),
    instructions: Optional[str] = Query(default=None, description="Optional instructions"),  # ✅ Properly optional
    db: Session = Depends(get_db)
):
    try:
        return await extract_and_save_image(db, file, user_id, instructions)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/extract-text-from-video/")
async def process_video(
    file: UploadFile = File(...),
    user_id: int = Query(...),
    instructions: Optional[str] = Query(default=None, description="Optional instructions"),  # ✅ Properly optional
    db: Session = Depends(get_db)
):
    try:
        return await extract_and_save_video(db, file, user_id, instructions)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Video processing failed: {str(e)}")