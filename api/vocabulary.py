from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from database import schemas
from database.db import get_db
from services.vocabulary_services import (
    create_vocabulary_entry,
    get_vocabulary_words_by_course,
    search_word_in_course
)
from utils.i18n import translate, get_lang_from_request

router = APIRouter(prefix="/api", tags=["Vocabularies"])


@router.post("/create-vocabularies/{course_id}/", response_model=schemas.Vocabulary)
def create_vocabulary(
    request: Request,
    course_id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        return create_vocabulary_entry(course_id=course_id, db=db)
    except HTTPException as e:
        # translate known error keys if present
        detail_key = e.detail if isinstance(e.detail, str) else None
        if detail_key:
            raise HTTPException(status_code=e.status_code, detail=translate(detail_key, lang))
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("vocab_create_error", lang)
        )


@router.get("/vocabularies/{course_id}/words", response_model=schemas.VocabularyWords)
async def get_words_by_course(
    request: Request,
    course_id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        words = get_vocabulary_words_by_course(course_id, db)
        return {"words": words}
    except HTTPException as e:
        detail_key = e.detail if isinstance(e.detail, str) else None
        if detail_key:
            raise HTTPException(status_code=e.status_code, detail=translate(detail_key, lang))
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("vocab_retrieve_error", lang)
        )


@router.get("/vocabularies/{course_id}/search", response_model=schemas.VocabularyWords)
async def search_vocabulary_word(
    request: Request,
    course_id: int,
    keyword: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        words = search_word_in_course(db=db, course_id=course_id, search_term=keyword)
        return {"words": words}
    except HTTPException as e:
        detail_key = e.detail if isinstance(e.detail, str) else None
        if detail_key:
            raise HTTPException(status_code=e.status_code, detail=translate(detail_key, lang))
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("vocab_search_error", lang)
        )
