import json
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any
from fastapi import status
from database import schemas
from database.db import get_db
from database import models
from utils.general_utils import parse_vocabulary_response
from utils.ollama_utils import text_generate_from_ollama
from utils.open_router import ask_openrouter  # Import the ask_openrouter function
import re
import json
from typing import List, Dict
from utils.gemini_api import generate_gemini_response
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import json
import re

def create_vocabulary_entry(course_id: int, db: Session) -> schemas.Vocabulary:
    # Step 1: Check if course exists
    course = db.query(models.Course).filter(models.Course.id_course == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Step 2: Check if vocabulary already exists for the course
    existing_vocabulary = db.query(models.Vocabulary).filter(models.Vocabulary.course_id == course_id).first()
    if existing_vocabulary:
        raise HTTPException(
            status_code=400,
            detail=f"Vocabulary entry already exists for course ID {course_id}. You cannot create another one."
        )

    # Step 3: Create a clean and strict prompt
    vocabulary_prompt = f"""
    Extract important terms and their definitions from this course text:
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

    try:
        # Step 4: Get AI response
        raw_response = ask_openrouter(
            vocabulary_prompt,
            system_prompt="You are a JSON-only assistant."
        )
        print(f"RAW RESPONSE >>>{raw_response}<<<")

        # Step 5: Extract and clean response text
        response = generate_gemini_response(
            prompt=vocabulary_prompt,
            response_type="json",
            system_prompt="You are a JSON-only assistant. Only output valid JSON"
        )

        # Step 6: Parse JSON safely
        try:
            result = json.loads(response)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON response from AI: {str(e)}"
            )

        # Step 7: Validate the structure
        if not isinstance(result, dict) or "words" not in result or not isinstance(result["words"], list):
            raise HTTPException(
                status_code=400,
                detail="AI response missing required 'words' list or invalid structure."
            )

        words_list = result["words"]

        # Optional: Sanitize each word (skip if your model is well-trained)
        for word in words_list:
            if not word.get("term") or not word.get("definition"):
                raise HTTPException(
                    status_code=400,
                    detail="Each word must include 'term' and 'definition'."
                )

        # Step 8: Save to DB
        db_vocabulary = models.Vocabulary(
            course_id=course_id,
            words=words_list,  # Ensure this field in your DB is of type JSON
            created_at=datetime.utcnow()
        )
        db.add(db_vocabulary)
        db.commit()
        db.refresh(db_vocabulary)

        return db_vocabulary

    except HTTPException as http_ex:
        raise http_ex  # Pass through known errors

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )
    
def get_vocabulary_words_by_course(course_id: int, db: Session) -> List[Dict[str, Any]]:
    vocabulary = db.query(models.Vocabulary).filter(
        models.Vocabulary.course_id == course_id
    ).first()
    
    if not vocabulary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary not found for this course"
        )
    
    return vocabulary.words

def search_word_in_course(
    db: Session,  # Now db is the first parameter
    course_id: int,
    search_term: str,
    exact_match: bool = False,
    search_definitions: bool = False,
    skip: int = 0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    vocabulary = db.query(models.Vocabulary).filter(
        models.Vocabulary.course_id == course_id
    ).first()
    
    if not vocabulary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary not found for this course"
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
    
    # Apply pagination
    return matches[skip:skip+limit]