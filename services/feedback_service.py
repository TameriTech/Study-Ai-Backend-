from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status
from database.models import Course, Feedback

def create_feedback_for_course(db: Session, course_id: int) -> Feedback:
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course or not course.quizzes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quizzes found for course ID {course_id}"
        )

    total = len(course.quizzes)
    correct = sum(1 for q in course.quizzes if q.correct_answer.strip().lower() == q.user_answer.strip().lower())
    rating = round((correct / total) * 100)
    comment = ""
    # Auto-generate comment if none provided
    if not comment:
        if rating < 10:
            comment = "Very poor performance. You need to review all the course materials."
        elif rating < 20:
            comment = "Extremely weak. Consider revisiting the basics."
        elif rating < 40:
            comment = "Poor. Make sure to study more and practice quizzes."
        elif rating < 45:
            comment = "Below average. You’re close to improving."
        elif rating < 50:
            comment = "Average. Try to understand where you lost marks."
        elif rating < 60:
            comment = "Fair. You can do better with a bit more effort."
        elif rating < 70:
            comment = "Good. Keep pushing for a higher score!"
        elif rating < 80:
            comment = "Very good. Great job!"
        elif rating < 90:
            comment = "Excellent. You're mastering the course."
        elif rating <= 100:
            comment = "Outstanding! Perfect or near-perfect performance."

    feedback = Feedback(
        course_id=course_id,
        rating=rating,
        comment=comment,
        created_at=datetime.utcnow()
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedback_by_course_id(db: Session, course_id: int) -> Feedback:
    feedback = db.query(Feedback).filter(Feedback.course_id == course_id).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No feedback found for course ID {course_id}"
        )
    return feedback
