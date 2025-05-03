from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import json
from typing import List
from database.models import Quiz as QuizModel, Course
from database.schemas import QuizCreate, Quiz
from utils.general_utils import extract_and_parse_questions
from utils.ollama_utils import generate_from_ollama

import json
import re

def create_quiz(db: Session, quiz_data: QuizCreate) -> Quiz:
    # Verify the course exists
    course = db.query(Course).filter(Course.id_course == quiz_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {quiz_data.course_id} not found"
        )
    
    if quiz_data.quiz_instruction:
        course.quiz_instruction = quiz_data.quiz_instruction
        course.level_of_difficulty = quiz_data.level_of_difficulty
        db.commit()
        db.refresh(course)
    
    quiz_prompt = f"""
from this text I quiz with this criteria:
level of difficulty: {quiz_data.level_of_difficulty}
quiz type: {quiz_data.quiz_type}, 
Number of questions: {quiz_data.number_of_questions}
additiomal instruction: {quiz_data.quiz_instruction}
---
{course.original_text}
---
Make sure the correct answer matches the right option 
because it will be use to rate the quiz.
Return ONLY a JSON array formatted like this:
Questions: [
  {{
    "question": "questions",
    "choices": {{"A": "answer A", "B": "answer B", "C": "answer C", "D": "answer D"}},
    "correct_answer": "correct letter from choices e.g C",
  }}
]
Remember "choice is a dictionary".
"""
    response = generate_from_ollama(quiz_prompt)
    print(f"Raw response:\n{response}")

    questions = extract_and_parse_questions(response)  # Assuming input_text is in QuizCreate
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid questions found in input text"
        )
    
    quizzes = []
    for q in questions:
        formatted_choices = {f"Option {key}": text for key, text in q['choices'].items()}
        
        db_quiz = QuizModel(
            course_id=quiz_data.course_id,
            question=q['question'],
            correct_answer=q['correct_answer'],
            user_answer="",  # Initialize as empty
            choices=formatted_choices,  # Now in {"Option A": "text"} format
            quiz_type=quiz_data.quiz_type,
            level_of_difficulty=quiz_data.level_of_difficulty,
            number_of_questions=quiz_data.number_of_questions,  # Total questions in this batch
            created_at=datetime.utcnow()
        )
        
        db.add(db_quiz)
        quizzes.append(db_quiz)
    
    db.commit()
    db.refresh(quizzes[0])  # Refresh the first quiz to get its ID
    return quizzes[0]  # Return the first quiz (matches response_model=schemas.Quiz)

def get_quiz_questions_by_course(db: Session, course_id: int) -> List[Quiz]:
    # Verify course exists
    if not db.query(Course).filter(Course.id_course == course_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    return db.query(QuizModel).filter(QuizModel.course_id == course_id).all()

def update_user_answer(db: Session, quiz_id: int, user_answer: str) -> QuizModel:
    quiz = db.query(QuizModel).filter(QuizModel.id_quiz == quiz_id).first()
    if not quiz:
        raise ValueError(f"Quiz with ID {quiz_id} not found")
    
    quiz.user_answer = user_answer
    db.commit()
    db.refresh(quiz)
    return quiz

def get_quiz_by_id(db: Session, quiz_id: int) -> QuizModel:
    quiz = db.query(QuizModel).filter(QuizModel.id_quiz == quiz_id).first()
    if not quiz:
        raise ValueError(f"Quiz with ID {quiz_id} not found")
    return quiz
