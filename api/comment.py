from typing import List
from fastapi import APIRouter, Depends
from requests import Session
from database import schemas
from database.db import get_db
from services.comment_service import create_comment, get_comment_by_id, get_comments_by_course_id, get_comments_by_user_id

router = APIRouter(prefix="/api")

@router.post("/create/comments/", response_model=schemas.Comment, tags=["Comments"])
def create_new_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db)
):
    return create_comment(db, comment)

@router.get("/comment-by-id/{comment_id}", response_model=schemas.Comment, tags=["Comments"])
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    return get_comment_by_id(db, comment_id)

@router.get("/user/comments/{user_id}", response_model=List[schemas.Comment], tags=["Comments"])
def read_comments_by_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_comments_by_user_id(db, user_id)

@router.get("/course/comment/{course_id}", response_model=List[schemas.Comment], tags=["Comments"])
def read_comments_by_course(
    course_id: int, 
    db: Session = Depends(get_db)
):
    return get_comments_by_course_id(db, course_id)