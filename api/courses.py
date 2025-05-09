from fastapi import APIRouter, Depends, HTTPException, Query
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
    search_courses,
    update_simplified_progress,
    update_summary_progress
)
from database.schemas import CourseSearchResponse

router = APIRouter(prefix="/api", tags=["Course"])

@router.get("/get-course/{course_id}/")
def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    course = get_course_from_db(db, course_id)
    if course is not None:
        return course
    raise HTTPException(status_code=404, detail="Course not found")

@router.get("/courses/search", response_model=CourseSearchResponse)
def search_courses_endpoint(
    query: str = Query(..., min_length=2, description="Search term (2+ characters)"),
    fields: Optional[str] = Query(
        None, 
        description="Comma-separated fields to search (default: course_name)",
        example="course_name,summary_text"
    ),
    fuzzy: bool = Query(False, description="Enable fuzzy matching"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(10, ge=1, le=100, description="Results per page (max 100)"),
    db: Session = Depends(get_db)
):
    """
    Search courses with flexible options:
    - Partial matching by default
    - Optional fuzzy matching
    - Multiple field search
    - Pagination
    
    Examples:
    - /courses/search?query=eng
    - /courses/search?query=beginner&fields=course_name,summary_text&fuzzy=true
    - /courses/search?query=eng&skip=5&limit=3
    """
    try:
        # Convert comma-separated fields to list
        search_fields = fields.split(',') if fields else None
        
        results = search_courses(
            db=db,
            search_query=query,
            search_fields=search_fields,
            fuzzy_match=fuzzy,
            skip=skip,
            limit=limit
        )
        
        return {
            "results": results["results"],
            "pagination": results["pagination"]
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
        detail=f"Search failed: {str(e)}"
        )

# @router.get("/api/courses-doc/{document_id}/simplified-modules", tags=["Course"])
# def get_simplified_modules_by_document_id(
#     document_id: int,
#     db: Session = Depends(get_db),
# ):
#     modules = get_simplified_modules(db, document_id)
#     if modules:
#         return modules
#     raise HTTPException(status_code=404, detail="Modules not found for this document")

# @router.get("/api/courses-doc/{document_id}/summary-modules/", tags=["Course"])
# def get_summary_modules_by_document_id(
#     document_id: int,
#     db: Session = Depends(get_db),
# ):
#     modules = get_summary_modules(db, document_id)
#     if modules:
#         return modules
#     raise HTTPException(status_code=404, detail="Modules not found for this document")

@router.get("/api/user/{user_id}/courses", response_model=List[schemas.Course], tags=["Course"])
def get_user_courses(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    db_courses = db.query(models.Course)\
        .join(models.Document)\
        .filter(models.Document.user_id == user_id)\
        .all()
    
    if not db_courses:
        raise HTTPException(status_code=404, detail="No courses found for this user")
    
    return db_courses

@router.get("/api/courses-id/{course_id}/simplified-modules", response_model=List[Dict], tags=["Course"])
def get_simplified_modules(
    course_id: int,
    db: Session = Depends(get_db),
):
    modules = get_simplified_modules_by_course_id(db, course_id)
    if modules is not None:
        return modules
    raise HTTPException(status_code=404, detail="Simplified modules not found for this course")

@router.get("/api/courses/{course_id}/summary-modules", response_model=List[Dict], tags=["Course"])
def get_summary_modules(
    course_id: int,
    db: Session = Depends(get_db),
):
    modules = get_summary_modules_by_course_id(db, course_id)
    if modules is not None:
        return modules
    raise HTTPException(status_code=404, detail="Summary modules not found for this course")


@router.put("/api/course/{course_id}/update-simplified-progress", response_model=schemas.Course, tags=["Course"])
def update_course_simplified_progress(
    simplified_current_page: int,
    course_id: int,
    db: Session = Depends(get_db),
):
    db_update = update_simplified_progress(db, course_id, simplified_current_page)
    if not db_update:
        raise HTTPException(status_code=404, detail="Course not found!")
    return db_update

@router.put("/api/course/{course_id}/update-summary-progress", response_model=schemas.Course, tags=["Course"])
def update_course_summary_progress(
    summary_current_page: int,
    course_id: int,
    db: Session = Depends(get_db),
):
    db_update = update_summary_progress(db, course_id, summary_current_page)
    if not db_update:
        raise HTTPException(status_code=404, detail="Course not found!")
    return db_update