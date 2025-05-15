from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status
from database.models import Course, Document, Feedback, User  # Import User if needed
from utils.email import send_email  # Your email sending function
from sqlalchemy.orm import joinedload

async def create_feedback_for_course(db: Session, course_id: int) -> Feedback:
    # Get course with all necessary relationships loaded
    course = db.query(Course).options(
        joinedload(Course.document).joinedload(Document.user)
    ).filter(Course.id_course == course_id).first()
    
    if not course or not course.quizzes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quizzes found for course ID {course_id}"
        )

    # Check if feedback already exists for the course
    existing_feedback = db.query(Feedback).filter(Feedback.course_id == course_id).first()
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feedback already exists for course ID {course_id}"
        )

    # Calculate results
    total = len(course.quizzes)
    correct = sum(1 for q in course.quizzes if q.correct_answer.strip().lower() == q.user_answer.strip().lower())
    rating = round((correct / total) * 100)
    
    # Generate feedback comment
    comment = generate_feedback_comment(rating)

    # Create feedback record
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

def generate_feedback_comment(rating: int) -> str:
    """Generate feedback comment based on rating percentage"""
    if rating < 10:
        return "📉 Very poor performance. You need to review all the course materials."
    elif rating < 20:
        return "😞 Extremely weak. Consider revisiting the basics."
    # ... (rest of your comment logic)
    else:
        return "🏆 Outstanding! Perfect or near-perfect performance."

async def send_feedback_email(user: User, course: Course, rating: int, correct: int, total: int):
    """Send feedback email to user"""
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #2c3e50;">📚 Course Feedback Results</h2>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <p><strong>Course:</strong> {course.course_name}</p>
            <p><strong>Score:</strong> <span style="font-weight: bold; color: {'#e74c3c' if rating < 50 else '#27ae60'}">
                {rating}% ({correct}/{total})
            </span></p>
            <p><strong>Feedback:</strong> {generate_feedback_comment(rating)}</p>
        </div>
    </body>
    </html>
    """

    try:
        await send_email(
            recipient=user.email,
            subject=f"📊 Your {course.course_name} Feedback",
            body=email_body,
            button_url="https://yourapp.com/dashboard",
            button_text="View Results"
        )
    except Exception as e:
        print(f"Failed to send feedback email: {str(e)}")


def get_feedback_by_course_id(db: Session, course_id: int) -> Feedback:
    feedback = db.query(Feedback).filter(Feedback.course_id == course_id).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No feedback found for course ID {course_id}"
        )
    return feedback
