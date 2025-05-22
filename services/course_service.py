from datetime import datetime
import json
import re
from fastapi import HTTPException, status
from requests import Session
from sqlalchemy import func, or_
from database import schemas
from database import db
from database import models
from database.models import Course, Document
from typing import Optional
from typing import List, Dict, Optional
from utils.gemini_api import generate_gemini_response, validate_and_parse_json
    
def create_course(
        db, 
        document_id: int,
        course_name: str,
        original_text: Optional[str] = None,
        simplified_text: Optional[str] = None,
        summary_text: Optional[str] = None,
    ) -> Course:

    # Prompt for simplified modules
    simplified_modules_prompt = f"""
    You must return a simplified structured course modules strictly as a JSON array of objects, each object with "topic" and "body" keys.

    Example:
    [
    {{"topic": "topic 1", "body": "body 1"}}
    ]

    Course content:
    ---
    {simplified_text}
    ---
    Return only JSON.
    """

    # Prompt for summary modules
    summary_modules_prompt = f"""
    Course content:
    ---
    {original_text}
    ---
    From the above course content you must return a summarized structured course modules strictly as a JSON array of objects, each object with "topic" and "body" keys.

    Example:
    [
    {{"topic": "topic 1", "body": "body 1"}}
    ]
    Return only JSON.
    """
    simplified_modules_text = generate_gemini_response(
        prompt=simplified_modules_prompt,
        response_type="json",
        system_prompt="You are a JSON-only assistant. Only output valid JSON"
    )
    print("Simplified Modules successfully!")
    summary_modules_text = generate_gemini_response(
        prompt=summary_modules_prompt,
        response_type="json",
        system_prompt="You are a JSON-only assistant. Only output valid JSON"
    )
    print("summary Modules successfully!")
    course_name_prompt = f"""
    Check this course content and the original name and give a name
    to the course that is best appropriate for displaying on a mobile app or websit
    Give exactly the name no pre-text or text after, I want to directly save it in the database.
    for example: Mathematics - Intergration.
    ---
    Course content: {summary_modules_text}, course original name: {course_name}
    ---

    """
    course_name = generate_gemini_response(
        prompt=course_name_prompt,
        response_type="text",
        system_prompt="You are a TETX-only assistant."
    )
    # Parse the module results
    simplified_modules = validate_and_parse_json(simplified_modules_text) or []
    summary_modules = validate_and_parse_json(summary_modules_text) or []

    # Estimated time (10 mins per module for estimation)
    num_simplified_modules = len(simplified_modules)
    num_summary_modules = len(summary_modules)
    estimated_completion_time = f"{max(num_simplified_modules, num_summary_modules) * 10} minutes"

    simplified_module_pages = num_simplified_modules
    summary_module_pages = num_summary_modules

    # Create course
    course = Course(
        document_id=document_id,
        course_name=course_name,
        original_text=original_text,
        simplified_text=simplified_text,
        summary_text=summary_text,
        level_of_difficulty="medium",
        estimated_completion_time=estimated_completion_time,
        quiz_instruction="Quiz instruction",
        simplified_modules=simplified_modules,
        simplified_module_pages=simplified_module_pages,
        summary_modules=summary_modules,
        summary_module_pages=summary_module_pages,
        created_at=datetime.utcnow()
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def get_simplified_modules(db: Session, document_id: int) -> Optional[List[Dict]]:
    course = db.query(Course).filter(Course.document_id == document_id).first()
    if not course or not course.simplified_modules:
        return None
    return course.simplified_modules

def get_summary_modules(db: Session, document_id: int) -> Optional[List[Dict]]:
    course = db.query(Course).filter(Course.document_id == document_id).first()
    if not course or not course.summary_modules:
        return None
    return course.summary_modules


def get_simplified_modules_by_course_id(db: Session, course_id: int) -> Optional[List[Dict]]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course or not course.simplified_modules:
        return None
    return course.simplified_modules

def get_summary_modules_by_course_id(db: Session, course_id: int) -> Optional[List[Dict]]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course or not course.summary_modules:
        return None
    return course.summary_modules

def get_user_summary_modules(user_id: int, db: Session) -> Dict[str, List[dict]]:
    courses = (
        db.query(models.Course)
        .join(models.Document)
        .filter(models.Document.user_id == user_id)
        .all()
    )

    summary_data = {}

    for course in courses:
        if course.summary_modules:
            summary_data[f"Course_id_{course.id_course}"] = course.summary_modules

    return summary_data

def get_user_simplified_modules(user_id: int, db: Session) -> Dict[str, List[dict]]:
    courses = (
        db.query(models.Course)
        .join(models.Document)
        .filter(models.Document.user_id == user_id)
        .all()
    )

    simplified_data = {}

    for course in courses:
        if course.simplified_modules:
            simplified_data[f"Course_id_{course.id_course}"] = course.simplified_modules

    return simplified_data


def update_simplified_progress(db: Session, course_id: int, simplified_current_page: int) -> Optional[Course]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        return None
    
    # Ensure current page doesn't exceed total pages
    if course.simplified_module_pages and simplified_current_page > course.simplified_module_pages:
        simplified_current_page = course.simplified_module_pages
    
    # Update current page
    course.simplified_current_page = simplified_current_page
    
    # Calculate and update progress statistic
    if course.simplified_module_pages and course.simplified_module_pages > 0:
        course.simplified_module_statistic = int(
            (simplified_current_page / course.simplified_module_pages) * 100
        )

    db.commit()
    db.refresh(course)
    return course

def update_summary_progress(db: Session, course_id: int, summary_current_page: int) -> Optional[Course]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        return None
    
    # Update the current page
    course.summary_current_page = summary_current_page
    
    # Calculate and update progress if total pages exists
    if course.summary_module_pages and course.summary_module_pages > 0:
        course.summary_modules_statistic = int(
            (summary_current_page / course.summary_module_pages) * 100
        )


    db.commit()
    db.refresh(course)
    return course

def get_course_from_db(db: Session, course_id: int) -> Optional[Dict]:  # Renamed function
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        return None
    return course

def get_user_courses(db: Session, user_id: int) -> List[Dict]:
    """Returns SQLAlchemy Course objects (not Pydantic models)"""
    return db.query(Course)\
        .join(Document)\
        .filter(Document.user_id == user_id)\
        .all()

def search_courses(
    db: Session,
    search_query: str,
    min_query_length: int = 2,
    limit: int = 10,
    skip: int = 0,
    search_fields: Optional[List[str]] = None,
    fuzzy_match: bool = False
) -> dict:
    """
    Search courses with flexible matching
    
    Args:
        db: Database session
        search_query: Search term
        min_query_length: Minimum characters required
        limit: Results per page
        skip: Pagination offset
        search_fields: Fields to search (default: ['course_name'])
        fuzzy_match: Enable approximate matching
    
    Returns:
        Dictionary with results and pagination info
    """
    # Validate input
    if len(search_query) < min_query_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Search query must be at least {min_query_length} characters"
        )
    
    # Default fields to search
    if search_fields is None:
        search_fields = ['course_name']
    
    # Prepare search term
    search_term = f"%{search_query}%"
    
    # Base query
    query = db.query(models.Course)
    
    # Build filters
    filters = []
    for field in search_fields:
        if hasattr(models.Course, field):
            if fuzzy_match:
                # Using PostgreSQL similarity function (requires pg_trgm extension)
                filters.append(func.similarity(getattr(models.Course, field), search_query) > 0.3)
            else:
                filters.append(getattr(models.Course, field).ilike(search_term))
    
    if not filters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid search fields specified"
        )
    
    # Apply filters with OR condition
    query = query.filter(or_(*filters))
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    courses = query.offset(skip).limit(limit).all()
    
    return {
        "results": courses,
        "pagination": {
            "total": total,
            "returned": len(courses),
            "skip": skip,
            "limit": limit
        }
    }