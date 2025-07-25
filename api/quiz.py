from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import schemas
from database.db import get_db
from services.quiz_service import (
    create_quiz,
    get_quiz_by_id,
    get_quiz_questions_by_course,
    get_user_quizzes_grouped_by_course,
    update_user_answer
)
from utils.i18n import translate, get_lang_from_request

router = APIRouter(prefix="/api", tags=["Quizzes"])

@router.post("/create/quizzes/", response_model=schemas.Quiz)
def create_quiz_question(
    request: Request,
    quiz_data: schemas.QuizCreateRequest,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return create_quiz(db=db, quiz_data=quiz_data, lang=lang)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("quiz_creation_error", lang)
        )

@router.get("/get-course/{course_id}/quizzes/", response_model=List[schemas.Quiz])
def get_course_quizzes(
    request: Request,
    course_id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return get_quiz_questions_by_course(db=db, course_id=course_id, lang=lang)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("quiz_fetch_error", lang)
        )

@router.patch("/quizzes/{quiz_id}/update-user-answer", response_model=schemas.Quiz)
def update_quiz_user_answer(
    request: Request,
    quiz_id: int,
    payload: schemas.QuizUserAnswerUpdate,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return update_user_answer(db=db, quiz_id=quiz_id, user_answer=payload.user_answer, lang=lang)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("quiz_update_error", lang)
        )

@router.get("/get-quizze/{quiz_id}", response_model=schemas.Quiz)
def get_quiz(
    request: Request,
    quiz_id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return get_quiz_by_id(db=db, quiz_id=quiz_id, lang=lang)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("quiz_retrieve_error", lang)
        )

@router.get("/user/{user_id}/quizzes", response_model=Dict[str, List[schemas.Quiz]])
def get_grouped_quizzes_for_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    grouped = get_user_quizzes_grouped_by_course(user_id, db)
    if not grouped:
        raise HTTPException(
            status_code=404,
            detail=translate("no_quizzes_for_user", lang)
        )
    return grouped
