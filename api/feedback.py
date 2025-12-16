from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database.db import get_db
from database import schemas
from services.feedback_service import create_feedback_for_course, get_feedback_by_course_id
from utils.i18n import translate, get_lang_from_request

router = APIRouter()

@router.post("/create/feedback/{course_id}", response_model=schemas.Feedback, tags=["Feedback"])
async def submit_feedback(
    request: Request,
    course_id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return await create_feedback_for_course(db=db, course_id=course_id, lang=lang)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("feedback_create_error", lang)
        )

@router.get("/get-feedback/course/{course_id}", response_model=schemas.Feedback, tags=["Feedback"])
def fetch_feedback_by_course_id(
    request: Request,
    course_id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return get_feedback_by_course_id(db, course_id, lang=lang)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("feedback_retrieve_error", lang)
        )
