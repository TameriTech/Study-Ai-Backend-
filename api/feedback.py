from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database import schemas
from services.feedback_service import create_feedback_for_course, get_feedback_by_course_id

router = APIRouter()

@router.post("/create/feedback/{course_id}", response_model=schemas.Feedback, tags=["Feedback"])
def submit_feedback(course_id: int, db: Session = Depends(get_db)):
    try:
        return create_feedback_for_course(db=db, course_id=course_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating feedback: {str(e)}")

@router.get("/get-feedback/course/{course_id}", response_model=schemas.Feedback, tags=["Feedback"])
def fetch_feedback_by_course_id(course_id: int, db: Session = Depends(get_db)):
    return get_feedback_by_course_id(db, course_id)
