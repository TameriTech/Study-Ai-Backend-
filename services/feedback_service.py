from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status
from database.models import Course, Document, Feedback, User
from utils.email import send_email
from sqlalchemy.orm import joinedload
from utils.i18n import translate  # Import translate to get localized messages

async def create_feedback_for_course(db: Session, course_id: int, lang: str = "en") -> Feedback:
    course = db.query(Course).options(
        joinedload(Course.document).joinedload(Document.user)
    ).filter(Course.id_course == course_id).first()
    
    if not course or not course.quizzes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("no_quizzes_found", lang)
        )

    existing_feedback = db.query(Feedback).filter(Feedback.course_id == course_id).first()
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("feedback_exists", lang)
        )

    total = len(course.quizzes)
    correct = sum(1 for q in course.quizzes if q.correct_answer.strip().lower() == q.user_answer.strip().lower())
    rating = round((correct / total) * 100)
    
    comment = generate_feedback_comment(rating, lang)

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

def generate_feedback_comment(rating: int, lang: str = "en") -> str:
    """Return localized feedback comment based on rating percentage"""
    if rating < 10:
        return translate("rating_very_poor", lang)
    elif rating < 20:
        return translate("rating_extremely_weak", lang)
    elif rating < 40:
        return translate("rating_poor", lang)
    elif rating < 45:
        return translate("rating_below_average", lang)
    elif rating < 50:
        return translate("rating_average", lang)
    elif rating < 60:
        return translate("rating_fair", lang)
    elif rating < 70:
        return translate("rating_good", lang)
    elif rating < 80:
        return translate("rating_very_good", lang)
    elif rating < 90:
        return translate("rating_excellent", lang)
    elif rating <= 100:
        return translate("rating_outstanding", lang)
    else:
        return translate("rating_invalid", lang)

async def send_feedback_email(user: User, course: Course, rating: int, correct: int, total: int, lang: str = "en"):
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #2c3e50;">📚 {translate('course_feedback_results', lang)}</h2>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <p><strong>{translate('course', lang)}:</strong> {course.course_name}</p>
            <p><strong>{translate('score', lang)}:</strong> <span style="font-weight: bold; color: {'#e74c3c' if rating < 50 else '#27ae60'}">
                {rating}% ({correct}/{total})
            </span></p>
            <p><strong>{translate('feedback', lang)}:</strong> {generate_feedback_comment(rating, lang)}</p>
        </div>
    </body>
    </html>
    """

    try:
        await send_email(
            recipient=user.email,
            subject=f"📊 {translate('your_feedback', lang)} - {course.course_name}",
            body=email_body,
            button_url="https://yourapp.com/dashboard",
            button_text=translate("view_results", lang)
        )
    except Exception as e:
        print(f"Failed to send feedback email: {str(e)}")

def get_feedback_by_course_id(db: Session, course_id: int, lang: str = "en") -> Feedback:
    feedback = db.query(Feedback).filter(Feedback.course_id == course_id).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("feedback_not_found", lang)
        )
    return feedback
