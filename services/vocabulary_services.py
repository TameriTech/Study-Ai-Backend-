import json
import time
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any, Optional
from database import models, schemas
from utils.gemini_api import generate_gemini_response
from fastapi import HTTPException


def create_vocabulary_entry(course_id: int, db: Session) -> schemas.Vocabulary:
    course = db.query(models.Course).filter(models.Course.id_course == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="course_not_found")

    existing_vocabulary = db.query(models.Vocabulary).filter(models.Vocabulary.course_id == course_id).first()
    if existing_vocabulary:
        raise HTTPException(
            status_code=400,
            detail="vocab_already_exists"
        )

    vocabulary_prompt = f"""
    Extract important terms and their definitions from this course text, make sure the text language is respected while giving the terms and definitions:
    ---
    {course.original_text}
    ---
    Return ONLY a valid JSON object with this exact structure:
    {{
        "words": [
            {{
                "term": "exact term",
                "definition": "clear and clean definition"
            }}
        ]
    }}
    IMPORTANT:
    - Do NOT include any markdown, bullet points, or explanatory text.
    - Do NOT include unescaped double quotes (") or characters like `?` in Big O examples. Use `O(n^2)` instead of `O(n?)`, and avoid malformed examples like `O(2")` instead of `O(n^2)`.
    - Your entire output must be valid JSON, starting with {{ and parsable using json.loads().
    """

    max_retries = 2
    attempt = 0
    while attempt < max_retries:
        try:
            response = generate_gemini_response(
                prompt=vocabulary_prompt,
                response_type="json",
                system_prompt="You are a JSON-only assistant. Only output valid JSON"
            )
            try:
                result = json.loads(response)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail="invalid_json_response"
                )
            if not isinstance(result, dict) or "words" not in result or not isinstance(result["words"], list):
                raise HTTPException(
                    status_code=400,
                    detail="invalid_response_structure"
                )

            for word in result["words"]:
                if not word.get("term") or not word.get("definition"):
                    raise HTTPException(
                        status_code=400,
                        detail="missing_term_or_definition"
                    )

            db_vocabulary = models.Vocabulary(
                course_id=course_id,
                words=result["words"],
                created_at=datetime.utcnow()
            )
            db.add(db_vocabulary)
            db.commit()
            db.refresh(db_vocabulary)
            return db_vocabulary

        except Exception as e:
            attempt += 1
            if attempt >= max_retries:
                raise HTTPException(
                    status_code=500,
                    detail="server_error_after_retries"
                )
            time.sleep(2)


def get_vocabulary_words_by_course(course_id: int, db: Session) -> List[Dict[str, Any]]:
    vocabulary = db.query(models.Vocabulary).filter(models.Vocabulary.course_id == course_id).first()
    if not vocabulary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="vocab_not_found"
        )
    return vocabulary.words


def search_word_in_course(
    db: Session,
    course_id: int,
    search_term: str,
    exact_match: bool = False,
    search_definitions: bool = False,
    skip: int = 0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    vocabulary = db.query(models.Vocabulary).filter(models.Vocabulary.course_id == course_id).first()
    if not vocabulary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="vocab_not_found"
        )
    if not vocabulary.words:
        return []

    search_term_lower = search_term.lower()
    matches = []

    for word in vocabulary.words:
        term = word.get("term", "").lower()
        definition = word.get("definition", "").lower()

        if exact_match:
            if term == search_term_lower:
                matches.append(word)
        else:
            term_match = search_term_lower in term
            definition_match = search_definitions and (search_term_lower in definition)
            if term_match or definition_match:
                matches.append(word)

    return matches[skip:skip+limit]
