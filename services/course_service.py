from datetime import datetime
import re
from fastapi import HTTPException, status
from requests import Session
from sqlalchemy import func, or_
from database import schemas
from database import db
from database import models
from database.models import Course, Document
from typing import Optional
import json
from typing import List, Dict, Optional

from utils.general_utils import parse_modules
from utils.ollama_utils import generate_from_ollama


def create_course(
        db, 
        document_id: int,
        course_name: str,
        original_text: Optional[str] = None,
        simplified_text: Optional[str] = None,
        summary_text: Optional[str] = None,
        level: str = "beginner",
    ) -> Course:

    # Parse modules if provided
    simplified_modules_prompt = f"""
    I have this course notes I want you to structure it in modules which each module will have a topic and body for example we chave am introduction as topic and a body of the introduction and finally let it be in a way I can play it in an array so that each module represent an element in the array:
    ---
    {simplified_text}
    ---
    """
    simplified_modules_text = generate_from_ollama(simplified_modules_prompt)

    summary_modules_prompt = f"""
    I have this course notes I want you to structure it in modules which each module will have a topic and body for example we chave am introduction as topic and a body of the introduction and finally let it be in a way I can play it in an array so that each module represent an element in the array:
    ---
    {summary_text}
    ---
    """
    summary_modules_text = generate_from_ollama(summary_modules_prompt)
    
    estimated_completion_time_prompt = f"""
    Without saying anything esle just give the hours needed to revise this text the response should be less then 12 chareacters:
    ---
    {simplified_text}
    ---
    """
    estimated_completion_time = generate_from_ollama(estimated_completion_time_prompt)

    summary_modules = parse_modules(summary_modules_text) if summary_modules_text else None
    simplified_modules = parse_modules(simplified_modules_text) if simplified_modules_text else None
    
    # Calculate module pages
    simplified_module_pages = len(simplified_modules) if simplified_modules else 0
    summary_module_pages = len(summary_modules) if summary_modules else 0



    course = Course(
        document_id=document_id,
        course_name=course_name,
        original_text=original_text,
        simplified_text=simplified_text,
        summary_text=summary_text,
        level=level,
        estimated_completion_time=estimated_completion_time,
        summary_modules=summary_modules,
        simplified_modules=simplified_modules,
        simplified_module_pages=simplified_module_pages,
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
