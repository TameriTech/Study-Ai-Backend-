from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Any, List, Dict, Optional
from sqlalchemy.orm import Session
from database import schemas
from database.db import get_db
from database import models
from services.course_service import (
    get_course_from_db,
    get_simplified_modules,
    get_simplified_modules_by_course_id,
    get_summary_modules,
    get_summary_modules_by_course_id,
    get_user_simplified_modules,
    get_user_summary_modules,
    search_courses,
    update_simplified_progress,
    update_summary_progress
)
from database.schemas import CourseSearchResponse
from utils.i18n import translate, get_lang_from_request

router = APIRouter(prefix="/api", tags=["Course"])

@router.get("/get-course/{course_id}/")
def get_course_by_id(request: Request, course_id: int, db: Session = Depends(get_db)):
    lang = get_lang_from_request(request)
    course = get_course_from_db(db, course_id)
    if course:
        return course
    raise HTTPException(status_code=404, detail=translate("course_not_found", lang))


@router.get("/courses/search", response_model=CourseSearchResponse)
def search_courses_endpoint(
    request: Request,
    query: str = Query(..., min_length=2),
    fields: Optional[str] = Query(None),
    fuzzy: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        search_fields = fields.split(',') if fields else None
        results = search_courses(
            db=db,
            search_query=query,
            search_fields=search_fields,
            fuzzy_match=fuzzy,
            skip=skip,
            limit=limit,
            lang=lang
        )
        return {
            "results": results["results"],
            "pagination": results["pagination"]
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail=translate("search_failed", lang))


@router.get("/user/{user_id}/revisions", tags=["Course"])
def get_summary_modules_for_user(request: Request, user_id: int, db: Session = Depends(get_db)) -> Dict[str, List[dict]]:
    lang = get_lang_from_request(request)
    summary_data = get_user_summary_modules(user_id, db)
    if not summary_data:
        raise HTTPException(status_code=404, detail=translate("no_summary_modules", lang))
    return summary_data


@router.get("/user/{user_id}/courses", tags=["Course"])
def get_simplified_modules_for_user(request: Request, user_id: int, db: Session = Depends(get_db)) -> Dict[str, List[dict]]:
    lang = get_lang_from_request(request)
    simplified_data = get_user_simplified_modules(user_id, db)
    if not simplified_data:
        raise HTTPException(status_code=404, detail=translate("no_simplified_modules", lang))
    return simplified_data


@router.get("/user/{user_id}/courses", response_model=List[schemas.Course], tags=["Course"])
def get_user_courses(request: Request, user_id: int, db: Session = Depends(get_db)) -> Any:
    lang = get_lang_from_request(request)
    db_courses = db.query(models.Course)\
        .join(models.Document)\
        .filter(models.Document.user_id == user_id)\
        .all()
    if not db_courses:
        raise HTTPException(status_code=404, detail=translate("no_courses_for_user", lang))
    return db_courses


@router.get("/course-revision/{course_id}", response_model=List[Dict], tags=["Course"])
def get_simplified_modules(request: Request, course_id: int, db: Session = Depends(get_db)):
    lang = get_lang_from_request(request)
    modules = get_simplified_modules_by_course_id(db, course_id)
    if modules is not None:
        return modules
    raise HTTPException(status_code=404, detail=translate("simplified_modules_not_found", lang))


@router.get("/course/{course_id}", response_model=List[Dict], tags=["Course"])
def get_summary_modules(request: Request, course_id: int, db: Session = Depends(get_db)):
    lang = get_lang_from_request(request)
    modules = get_summary_modules_by_course_id(db, course_id)
    if modules is not None:
        return modules
    raise HTTPException(status_code=404, detail=translate("summary_modules_not_found", lang))


@router.put("/update-course/{course_id}/progress", response_model=schemas.Course, tags=["Course"])
def update_course_simplified_progress(
    request: Request,
    simplified_current_page: int,
    course_id: int,
    db: Session = Depends(get_db),
):
    lang = get_lang_from_request(request)
    try:
        db_update = update_simplified_progress(db, course_id, simplified_current_page, lang=lang)
        return db_update
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail=translate("update_progress_failed", lang))


@router.put("/course/{course_id}/update-revision-progress", response_model=schemas.Course, tags=["Course"])
def update_course_summary_progress(
    request: Request,
    summary_current_page: int,
    course_id: int,
    db: Session = Depends(get_db),
):
    lang = get_lang_from_request(request)
    try:
        db_update = update_summary_progress(db, course_id, summary_current_page, lang=lang)
        return db_update
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail=translate("update_progress_failed", lang))
