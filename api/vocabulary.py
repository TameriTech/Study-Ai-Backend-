from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from database import schemas
from database.db import get_db
from services.vocabulary_services import (
    create_vocabulary_entry,
    get_vocabulary_words_by_course,
    search_word_in_course
)

router = APIRouter(prefix="/api", tags=["Vocabularies"])

@router.post("/create-vocabularies/{course_id}/", response_model=schemas.Vocabulary)
def create_vocabulary(course_id: int, db: Session = Depends(get_db)):
    try:
        return create_vocabulary_entry(course_id=course_id, db=db)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.get("/vocabularies/{course_id}/words", response_model=schemas.VocabularyWords)
async def get_words_by_course(course_id: int, db: Session = Depends(get_db)):
    try:
        words = get_vocabulary_words_by_course(course_id, db)
        return {"words": words}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving words: {str(e)}")

@router.get("/vocabularies/{course_id}/search", response_model=schemas.VocabularyWords)
async def search_vocabulary_word(
    course_id: int,
    keyword: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    try:
        words = search_word_in_course(db=db, course_id=course_id, search_term=keyword)
        return {"words": words}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
