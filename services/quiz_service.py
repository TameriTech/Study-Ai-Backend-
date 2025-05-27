from collections import defaultdict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, List
import database.models as models
from database.models import Quiz as QuizModel, Course, Document
from database.schemas import QuizCreate, Quiz
import json
import re
from utils.gemini_api import generate_gemini_response, quiz_validate_and_parse_json


import time
from typing import Optional

def get_ai_response_with_retry(quiz_prompt: str, retries: int = 2) -> Optional[str]:
    """Helper function to get a valid AI response with retries"""
    attempt = 0
    while attempt < retries:
        try:
            response = generate_gemini_response(
                prompt=quiz_prompt,
                response_type="json",
                system_prompt="You are a JSON-only assistant. Only output valid JSON"
            )
            
            # Debug: Log the raw response
            # print(f"Attempt {attempt + 1}: Raw response from AI:\n{response}")
            
            # Validate the response, if it fails, retry
            if not response:
                raise ValueError("Empty response from AI")

            return response  # Return valid response if successful
        except Exception as e:
            # Log the error and retry
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(2)  # Optional: Add a delay before retrying
    
    # If all retries fail, return None
    return None


def create_quiz(db: Session, quiz_data: QuizCreate) -> Quiz:
    # Verify the course exists
    course = db.query(Course).filter(Course.id_course == quiz_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {quiz_data.course_id} not found"
        )
    
    # Check if quizzes already exist for the course
    existing_quizzes = db.query(QuizModel).filter(QuizModel.course_id == quiz_data.course_id).first()
    if existing_quizzes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A set of quizzes already exists for course ID {quiz_data.course_id}. You cannot create another set."
        )

    # Update the course details if quiz instruction is provided
    if quiz_data.quiz_instruction:
        course.quiz_instruction = quiz_data.quiz_instruction
        course.level_of_difficulty = quiz_data.level_of_difficulty
        db.commit()
        db.refresh(course)
    
    # Construct the quiz prompt for OpenRouter
    quiz_prompt = f"""
        from this text I quiz with this criteria:
        level of difficulty: {quiz_data.level_of_difficulty}
        quiz type: {quiz_data.quiz_type}, 
        Number of questions: {quiz_data.number_of_questions}
        additional instruction: {quiz_data.quiz_instruction}

        Make sure the correct answer matches the right option 
        because it will be used to rate the quiz.
        Return ONLY a JSON array formatted like this:
        Questions: [
        {{
            "question": "questions",
            "choices": {{"A": "answer A", "B": "answer B", "C": "answer C", "D": "answer D"}},
            "correct_answer": "correct letter from choices e.g C"
        }}
        ]
        Remember "choice is a dictionary".
        ---
        {course.original_text}
        ---
        """
    
    # Retry getting a valid response from AI
    response = get_ai_response_with_retry(quiz_prompt)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to generate valid quiz questions after multiple attempts."
        )

    # Parse the questions from the response
    questions = quiz_validate_and_parse_json(response)
    # print(f"Parsed response of questions:\n{questions}")

    # If no valid questions are found, raise an error
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid questions found in input text"
        )
    
    # Initialize a list to hold the created quizzes
    quizzes = []
    
    # Loop over each question to save it in the database
    for q in questions:
        # Format choices as {"Option A": "text"} instead of {"A": "text"}
        formatted_choices = {f"Option {key}": text for key, text in q['choices'].items()}
        
        # Create a new QuizModel object
        db_quiz = QuizModel(
            course_id=quiz_data.course_id,
            question=q['question'],
            correct_answer=q['correct_answer'],
            user_answer="",  # Initialize with an empty string for user_answer
            choices=formatted_choices,  # Store choices in the new format
            quiz_type=quiz_data.quiz_type,
            level_of_difficulty=quiz_data.level_of_difficulty,
            number_of_questions=quiz_data.number_of_questions,  # Total number of questions in this batch
            created_at=datetime.utcnow()  # Store the current time as creation time
        )
        
        # Add the new quiz to the database session
        db.add(db_quiz)
        quizzes.append(db_quiz)
    
    # Commit the changes to the database
    db.commit()
    db.refresh(quizzes[0])  # Refresh the first quiz to get its ID
    course = db.query(Course).filter(Course.id_course == quiz_data.course_id).first()
    
    return Quiz(
        id_quiz=quizzes[0].id_quiz,
        course_id=quizzes[0].course_id,
        question=quizzes[0].question,
        correct_answer=quizzes[0].correct_answer,
        user_answer=quizzes[0].user_answer,
        choices=quizzes[0].choices,
        quiz_type=quizzes[0].quiz_type,
        level_of_difficulty=quizzes[0].level_of_difficulty,
        number_of_questions=quizzes[0].number_of_questions,
        created_at=quizzes[0].created_at,
        course_name=course.course_name
    )

def get_quiz_questions_by_course(db: Session, course_id: int) -> List[Quiz]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    quizzes = db.query(models.Quiz).filter(models.Quiz.course_id == course_id).all()
    return [
        Quiz(
            id_quiz=quiz.id_quiz,
            course_id=quiz.course_id,
            question=quiz.question,
            correct_answer=quiz.correct_answer,
            user_answer=quiz.user_answer,
            choices=quiz.choices,
            quiz_type=quiz.quiz_type,
            level_of_difficulty=quiz.level_of_difficulty,
            number_of_questions=quiz.number_of_questions,
            created_at=quiz.created_at,
            course_name=course.course_name
        )
        for quiz in quizzes
    ]

def get_quiz_by_id(db: Session, quiz_id: int) -> Quiz:
    quiz = db.query(models.Quiz).filter(models.Quiz.id_quiz == quiz_id).first()
    if not quiz:
        raise ValueError(f"Quiz with ID {quiz_id} not found")
    
    course = db.query(Course).filter(Course.id_course == quiz.course_id).first()
    return Quiz(
        id_quiz=quiz.id_quiz,
        course_id=quiz.course_id,
        question=quiz.question,
        correct_answer=quiz.correct_answer,
        user_answer=quiz.user_answer,
        choices=quiz.choices,
        quiz_type=quiz.quiz_type,
        level_of_difficulty=quiz.level_of_difficulty,
        number_of_questions=quiz.number_of_questions,
        created_at=quiz.created_at,
        course_name=course.course_name
    )

def get_user_quizzes_grouped_by_course(user_id: int, db: Session) -> Dict[str, List[Quiz]]:
    # Query both Quiz and Course.course_name together
    quiz_results = (
        db.query(models.Quiz, models.Course.course_name)
        .join(models.Course, models.Quiz.course_id == models.Course.id_course)
        .join(models.Document, models.Course.document_id == models.Document.id_document)
        .filter(models.Document.user_id == user_id)
        .all()
    )

    grouped_quizzes: Dict[str, List[Quiz]] = defaultdict(list)

    for quiz_model, course_name in quiz_results:
        # Convert SQLAlchemy model to dictionary
        quiz_dict = {
            "id_quiz": quiz_model.id_quiz,
            "course_id": quiz_model.course_id,
            "question": quiz_model.question,
            "correct_answer": quiz_model.correct_answer,
            "user_answer": quiz_model.user_answer,
            "choices": quiz_model.choices,
            "quiz_type": quiz_model.quiz_type,
            "level_of_difficulty": quiz_model.level_of_difficulty,
            "number_of_questions": quiz_model.number_of_questions,
            "created_at": quiz_model.created_at,
            "course_name": course_name  # Add the course_name
        }
        grouped_quizzes[f"Course_id:{quiz_model.course_id}"].append(Quiz(**quiz_dict))

    return grouped_quizzes

def update_user_answer(db: Session, quiz_id: int, user_answer: str) -> QuizModel:
    quiz = db.query(QuizModel).filter(QuizModel.id_quiz == quiz_id).first()
    if not quiz:
        raise ValueError(f"Quiz with ID {quiz_id} not found")
    
    quiz.user_answer = user_answer
    course = db.query(Course).filter(Course.id_course == quiz.course_id).first()
    quiz.course_name = course.course_name

    db.commit()
    db.refresh(quiz)
    return quiz