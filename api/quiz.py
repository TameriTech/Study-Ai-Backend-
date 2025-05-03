from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import schemas
from database.db import get_db
from services.quiz_service import (
    create_quiz,
    get_quiz_by_id,
    get_quiz_questions_by_course,
    update_user_answer
)

router = APIRouter(prefix="/api", tags=["Quizzes"])

@router.post("/create/quizzes/", response_model=schemas.Quiz)
def create_quiz_question(
    quiz_data: schemas.QuizCreate,  # Remove course_id from QuizCreate schema
    db: Session = Depends(get_db)
):
    # Set course_id from path parameter
    quiz_data_dict = quiz_data.dict()
    return create_quiz(db=db, quiz_data=schemas.QuizCreate(**quiz_data_dict))

@router.get("/get-course/{course_id}/quizzes/", response_model=List[schemas.Quiz])
def get_course_quizzes(
    course_id: int,
    db: Session = Depends(get_db)
):
    try:
        return get_quiz_questions_by_course(db=db, course_id=course_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quizzes: {str(e)}")
    
@router.patch("/quizzes/{quiz_id}/update-user-answer", response_model=schemas.Quiz)
def update_quiz_user_answer(
    quiz_id: int,
    payload: schemas.QuizUserAnswerUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_quiz = update_user_answer(db=db, quiz_id=quiz_id, user_answer=payload.user_answer)
        return updated_quiz
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating quiz answer: {str(e)}")
    
@router.get("/get-quizze/{quiz_id}", response_model=schemas.Quiz)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    try:
        return get_quiz_by_id(db=db, quiz_id=quiz_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quiz: {str(e)}")