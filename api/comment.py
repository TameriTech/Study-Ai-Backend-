from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import schemas
from database.db import get_db
from services.comment_service import (
    create_comment,
    get_comment_by_id,
    get_comments_by_course_id,
    get_comments_by_user_id
)
from utils.i18n import translate, get_lang_from_request

router = APIRouter(prefix="/api", tags=["Comments"])

@router.post("/create/comments/", response_model=schemas.Comment)
def create_new_comment(
    request: Request,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return create_comment(db, comment)
    except HTTPException as e:
        detail_key = e.detail if isinstance(e.detail, str) else None
        if detail_key:
            raise HTTPException(status_code=e.status_code, detail=translate(detail_key, lang))
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("comment_create_error", lang)
        )

@router.get("/comment-by-id/{comment_id}", response_model=schemas.Comment)
def read_comment(
    request: Request,
    comment_id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        comment = get_comment_by_id(db, comment_id)
        return comment
    except HTTPException as e:
        detail_key = e.detail if isinstance(e.detail, str) else None
        if detail_key:
            raise HTTPException(status_code=e.status_code, detail=translate(detail_key, lang))
        raise

@router.get("/user/comments/{user_id}", response_model=List[schemas.Comment])
def read_comments_by_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return get_comments_by_user_id(db, user_id)
    except HTTPException as e:
        detail_key = e.detail if isinstance(e.detail, str) else None
        if detail_key:
            raise HTTPException(status_code=e.status_code, detail=translate(detail_key, lang))
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("user_comments_fetch_error", lang)
        )

@router.get("/course/comment/{course_id}", response_model=List[schemas.Comment])
def read_comments_by_course(
    request: Request,
    course_id: int, 
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return get_comments_by_course_id(db, course_id)
    except HTTPException as e:
        detail_key = e.detail if isinstance(e.detail, str) else None
        if detail_key:
            raise HTTPException(status_code=e.status_code, detail=translate(detail_key, lang))
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("course_comments_fetch_error", lang)
        )
