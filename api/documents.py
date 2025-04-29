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
    db: Session = Depends(get_db)
):
    return await extract_and_save_pdf(db, file, user_id)

@router.post("/extract-text-from-image/")
async def extract_text_from_image_route(
    file: UploadFile = File(...),
    user_id: int = Query(..., description="ID of the user uploading the image"),
    db: Session = Depends(get_db)
):
    try:
        return await extract_and_save_image(db, file, user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/extract-text-from-video/")
async def process_video(
    file: UploadFile = File(...),
    user_id: int = Query(...),
    frames_per_second: int = Query(1, gt=0, le=10),
    db: Session = Depends(get_db)
):
    try:
        return await extract_and_save_video(db, file, user_id, frames_per_second)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Processing failed: {str(e)}")