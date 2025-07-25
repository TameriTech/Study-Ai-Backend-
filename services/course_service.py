from datetime import datetime
import json
import re
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from database import schemas
from database import models
from database.models import Course, Document
from typing import Optional, List, Dict
from utils.gemini_api import generate_gemini_response, validate_and_parse_json
from utils.i18n import translate


def create_course(
        db,
        document_id: int,
        course_name: str,
        original_text: Optional[str] = None,
        instructions: Optional[str] = None,
        lang: str = "en"
    ) -> Course:

    simplified_modules_prompt = f"""
    You must return a simplified structured course modules strictly as a JSON array of objects, each object with "topic" and "body" keys.
    Make sure to simplify in the language of the provided text.
    Example:
    [
    {{"topic": "topic 1", "body": "body 1"}}
    ]

    Course content:
    ---
    {original_text}
    ---
    Return only JSON.
    Make sure you follow these instructions: {instructions}
    """

    summary_modules_prompt = f"""
    Course content:
    ---
    {original_text}
    ---
    From the above course content you must return a summarized structured course modules strictly as a JSON array of objects, each object with "topic" and "body" keys.
    Make sure to summarize in the language of the provided text.
    Example:
    [
    {{"topic": "topic 1", "body": "body 1"}}
    ]
    Return only JSON.
    Make sure you follow these instructions: {instructions}
    """

    simplified_modules_text = generate_gemini_response(
        prompt=simplified_modules_prompt,
        response_type="json",
        system_prompt="You are a JSON-only assistant. Only output valid JSON"
    )

    summary_modules_text = generate_gemini_response(
        prompt=summary_modules_prompt,
        response_type="json",
        system_prompt="You are a JSON-only assistant. Only output valid JSON"
    )

    course_name_prompt = f"""
    Check this course content and the original name and give a name
    to the course that is best appropriate for displaying on a mobile app or website.
    Give exactly the name no pre-text or text after, I want to directly save it in the database.
    For example: Mathematics - Integration.
    ---
    Course content: {summary_modules_text}, course original name: {course_name}
    ---
    Make sure it is in the language of the course content.
    """

    course_name_generated = generate_gemini_response(
        prompt=course_name_prompt,
        response_type="text",
        system_prompt="You are a TEXT-only assistant."
    )

    simplified_modules = validate_and_parse_json(simplified_modules_text) or []
    summary_modules = validate_and_parse_json(summary_modules_text) or []

    num_simplified_modules = len(simplified_modules)
    num_summary_modules = len(summary_modules)
    estimated_completion_time = f"{max(num_simplified_modules, num_summary_modules) * 10} minutes"

    simplified_module_pages = num_simplified_modules
    summary_module_pages = num_summary_modules

    course = Course(
        document_id=document_id,
        course_name=course_name_generated,
        original_text=original_text,
        simplified_text="simplified_text",
        summary_text="summary_text",
        level_of_difficulty="medium",
        estimated_completion_time=estimated_completion_time,
        quiz_instruction=instructions,
        simplified_modules=simplified_modules,
        simplified_module_pages=simplified_module_pages,
        summary_modules=summary_modules,
        summary_module_pages=summary_module_pages,
        has_quiz=False,
        created_at=datetime.utcnow()
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def get_simplified_modules(db, document_id: int) -> Optional[List[Dict]]:
    course = db.query(Course).filter(Course.document_id == document_id).first()
    if not course or not course.simplified_modules:
        return None
    return course.simplified_modules


def get_summary_modules(db, document_id: int) -> Optional[List[Dict]]:
    course = db.query(Course).filter(Course.document_id == document_id).first()
    if not course or not course.summary_modules:
        return None
    return course.summary_modules


def get_simplified_modules_by_course_id(db, course_id: int) -> Optional[List[Dict]]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course or not course.simplified_modules:
        return None
    return course.simplified_modules


def get_summary_modules_by_course_id(db, course_id: int) -> Optional[List[Dict]]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course or not course.summary_modules:
        return None
    return course.summary_modules


def get_user_summary_modules(user_id: int, db) -> Dict[str, List[dict]]:
    courses = (
        db.query(models.Course)
        .join(models.Document)
        .filter(models.Document.user_id == user_id)
        .all()
    )

    course_list = []

    for course in courses:
        if course.summary_modules:
            course_list.append({
                f"Course_id_{course.id_course}": {
                    "id_course": course.id_course,
                    "course_name": course.course_name,
                    "level_of_difficulty": course.level_of_difficulty,
                    "estimated_completion_time": course.estimated_completion_time,
                    "simplified_module_statistic": course.simplified_module_statistic,
                    "summary_modules": course.summary_modules,
                    "created_at": course.created_at,
                    "has_quiz": course.has_quiz,
                }
            })

    return {"courses": course_list}


def get_user_simplified_modules(user_id: int, db) -> Dict[str, List[dict]]:
    courses = (
        db.query(models.Course)
        .join(models.Document)
        .filter(models.Document.user_id == user_id)
        .all()
    )

    course_list = []

    for course in courses:
        if course.simplified_modules:
            course_list.append({
                f"Course_id_{course.id_course}": {
                    "id_course": course.id_course,
                    "course_name": course.course_name,
                    "level_of_difficulty": course.level_of_difficulty,
                    "estimated_completion_time": course.estimated_completion_time,
                    "simplified_module_statistic": course.simplified_module_statistic,
                    "simplified_modules": course.simplified_modules,
                    "created_at": course.created_at,
                    "has_quiz": course.has_quiz,
                }
            })

    return {"courses": course_list}


def update_simplified_progress(db, course_id: int, simplified_current_page: int, lang: str = "en") -> Optional[Course]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=translate("course_not_found", lang))

    if course.simplified_module_pages and simplified_current_page > course.simplified_module_pages:
        simplified_current_page = course.simplified_module_pages

    course.simplified_current_page = simplified_current_page

    if course.simplified_module_pages and course.simplified_module_pages > 0:
        course.simplified_module_statistic = int(
            (simplified_current_page / course.simplified_module_pages) * 100
        )

    db.commit()
    db.refresh(course)
    return course


def update_summary_progress(db, course_id: int, summary_current_page: int, lang: str = "en") -> Optional[Course]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=translate("course_not_found", lang))

    course.summary_current_page = summary_current_page

    if course.summary_module_pages and course.summary_module_pages > 0:
        course.summary_modules_statistic = int(
            (summary_current_page / course.summary_module_pages) * 100
        )

    db.commit()
    db.refresh(course)
    return course


def get_course_from_db(db, course_id: int) -> Optional[Course]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    return course


def get_user_courses(db, user_id: int) -> List[Course]:
    return db.query(Course) \
        .join(Document) \
        .filter(Document.user_id == user_id) \
        .all()


def search_courses(
    db,
    search_query: str,
    min_query_length: int = 2,
    limit: int = 10,
    skip: int = 0,
    search_fields: Optional[List[str]] = None,
    fuzzy_match: bool = False,
    lang: str = "en"
) -> dict:

    if len(search_query) < min_query_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("search_query_too_short", lang)
        )

    if search_fields is None:
        search_fields = ['course_name']

    search_term = f"%{search_query}%"
    query = db.query(models.Course)

    filters = []
    for field in search_fields:
        if hasattr(models.Course, field):
            if fuzzy_match:
                filters.append(func.similarity(getattr(models.Course, field), search_query) > 0.3)
            else:
                filters.append(getattr(models.Course, field).ilike(search_term))

    if not filters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("no_valid_search_fields", lang)
        )

    query = query.filter(or_(*filters))
    total = query.count()
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
