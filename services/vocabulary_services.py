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

import re
import json
from typing import List, Dict

def create_vocabulary_entry(course_id: int, db: Session) -> schemas.Vocabulary:
    course = db.query(models.Course).filter(models.Course.id_course == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Improved prompt with strict JSON formatting
    vocabulary_prompt = f"""
    Extract important terms and their definitions from this course text:
    ---
    {course.original_text}
    ---
    Return ONLY a valid JSON array with this exact structure:
    {{
        "words": [
            {{
                "term": "exact term",
                "definition": "clear definition"
            }}
        ]
    }}
    Do not include any additional text, explanations, or markdown formatting.
    The response must be parseable by json.loads().
    """
    
    try:
        response = text_generate_from_ollama(vocabulary_prompt)
        print(f"Ollama response:\n{response}")
        
        # Directly parse the JSON (assuming Ollama returns proper JSON)
        result = json.loads(response)
        words_list = result["words"]
        
        db_vocabulary = models.Vocabulary(
            course_id=course_id,
            words=words_list,
            created_at=datetime.utcnow()
        )
        db.add(db_vocabulary)
        db.commit()
        return db_vocabulary
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON response from AI: {str(e)}"
        )
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail="AI response missing required 'words' field"
        )
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