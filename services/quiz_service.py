from collections import defaultdict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, List, Optional
import database.models as models
from database.models import Quiz as QuizModel, Course, Document
from database.schemas import QuizCreate, Quiz
import json
import re
from utils.gemini_api import generate_gemini_response, quiz_validate_and_parse_json
import time
from utils.i18n import translate


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
            if not response:
                raise ValueError("Empty response from AI")
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(2)  # delay before retrying
    return None


def create_quiz(db: Session, quiz_data: QuizCreate, lang: str = "en") -> Quiz:
    course = db.query(Course).filter(Course.id_course == quiz_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("course_not_found", lang)
        )
    
    if course.has_quiz:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("quiz_already_exists", lang)
        )
    
    quiz_prompt = f"""
        from this text create quiz with this criteria:
        level of difficulty: {quiz_data.level_of_difficulty}
        quiz type: {quiz_data.quiz_type}, 
        Number of questions: {quiz_data.number_of_questions}
        additional instruction: {quiz_data.quiz_instruction}
        Make sure let it be in the language of the course content.

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
    
    response = get_ai_response_with_retry(quiz_prompt)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("quiz_generation_failed", lang)
        )
    
    questions = quiz_validate_and_parse_json(response)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("no_valid_questions", lang)
        )
    
    quizzes = []
    for q in questions:
        formatted_choices = {f"Option {key}": text for key, text in q['choices'].items()}
        db_quiz = QuizModel(
            course_id=quiz_data.course_id,
            question=q['question'],
            correct_answer=q['correct_answer'],
            user_answer="",
            choices=formatted_choices,
            quiz_type=quiz_data.quiz_type,
            level_of_difficulty=quiz_data.level_of_difficulty,
            number_of_questions=quiz_data.number_of_questions,
            created_at=datetime.utcnow()
        )
        db.add(db_quiz)
        quizzes.append(db_quiz)
    
    course.has_quiz = True
    db.add(course)
    db.commit()
    db.refresh(quizzes[0])
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


def get_quiz_questions_by_course(db: Session, course_id: int, lang: str = "en") -> List[Quiz]:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("course_not_found", lang)
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


def get_quiz_by_id(db: Session, quiz_id: int, lang: str = "en") -> Quiz:
    quiz = db.query(models.Quiz).filter(models.Quiz.id_quiz == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("quiz_not_found", lang)
        )
    
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
    quiz_results = (
        db.query(models.Quiz, models.Course.course_name)
        .join(models.Course, models.Quiz.course_id == models.Course.id_course)
        .join(models.Document, models.Course.document_id == models.Document.id_document)
        .filter(models.Document.user_id == user_id)
        .all()
    )

    grouped_quizzes: Dict[str, List[Quiz]] = defaultdict(list)

    for quiz_model, course_name in quiz_results:
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
            "course_name": course_name
        }
        grouped_quizzes[f"Course_id:{quiz_model.course_id}"].append(Quiz(**quiz_dict))

    return grouped_quizzes


def update_user_answer(db: Session, quiz_id: int, user_answer: str, lang: str = "en") -> QuizModel:
    quiz = db.query(QuizModel).filter(QuizModel.id_quiz == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("quiz_not_found", lang)
        )
    
    quiz.user_answer = user_answer
    course = db.query(Course).filter(Course.id_course == quiz.course_id).first()
    quiz.course_name = course.course_name

    db.commit()
    db.refresh(quiz)
    return quiz
