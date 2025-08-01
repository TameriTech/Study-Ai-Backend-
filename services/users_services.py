import string
import secrets
from database.models import User
from sqlalchemy.orm import Session
from database.schemas import UserCreate, UserUpdate
from utils.general_utils import hash_password
from utils.general_utils import verify_password
from utils.email import send_email  # you'll need to implement this
from fastapi import HTTPException, status
import logging
from utils.i18n import translate

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.password):
        return user
    return None

def error_response(code: str, message: str, status_code: int = 400):
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message}
    )

async def create_user(db: Session, data: UserCreate, lang: str = "en"):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        error_response("registration_error", translate("email_exists", lang))

    # Hash password and create user instance
    hashed_pwd = hash_password(data.password)
    user_instance = User(
        fullName=data.fullName,
        class_level=data.class_level,
        email=data.email,
        password=hashed_pwd,
        best_subjects=data.best_subjects,
        learning_objectives=data.learning_objectives,
        academic_level=data.academic_level,
        statistic=data.statistic
    )

    db.add(user_instance)
    db.commit()
    db.refresh(user_instance)

    # Prepare welcome email
    welcome_subject = f"🎉 Welcome to Tameri Study AI, {data.fullName.split()[0]}!"
    
    welcome_body = f"""
    <h2>🌟 Welcome Aboard!</h2>
    <p>Dear {data.fullName},</p>
    <p>We're thrilled to have you join our learning community! Here's what you can do now:</p>
    <ul>
        <li>📚 Access personalized study materials</li>
        <li>🧠 Take smart quizzes tailored to your level</li>
        <li>📈 Track your learning progress</li>
    </ul>
    <p>Start your learning journey now!</p>
    <img src="https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif" alt="Celebration GIF" style="max-width: 300px;">
    <p>Happy Learning,<br>
    The Study AI Team 🚀</p>
    """

    # Send welcome email
    await send_email(
        recipient=data.email,
        subject=welcome_subject,
        body=welcome_body,
        button_url="https://yourapp.com/dashboard",
        button_text="Start Learning"
    )

    return user_instance



def get_users(db: Session):
    return db.query(User).all()

def get_user(db: Session, user_id:int):
    return db.query(User).filter(User.id == user_id).first()


def calculate_user_feedback_statistics(db: Session, user_id: int):
    """
    Calculate the user's average rating as a percentage (0-100%)
    based on all feedback ratings across all their courses.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    total_rating = 0
    feedback_count = 0
    
    # Get all feedbacks for all courses created by this user
    for document in user.documents:
        for course in document.courses:
            for feedback in course.feedbacks:
                total_rating += feedback.rating
                feedback_count += 1

    if feedback_count == 0:
        user.statistic = 0
    else:
        percentage = (total_rating / feedback_count) 
        print("total_rating", percentage)
        user.statistic = round(percentage, 2)
    
    db.commit()
    return user.statistic

def update_user(db: Session, user_data: UserUpdate, user_id: int):
    user_queryset = db.query(User).filter(User.id == user_id).first()
    if user_queryset:
        update_data = user_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            # Skip updating if value is an empty string
            if value == "":
                continue
            setattr(user_queryset, key, value)
        db.commit()
        db.refresh(user_queryset)
    return user_queryset


def delete_user(db: Session, user_id:int):
    user_queryset = db.query(User).filter(User.id == user_id).first()
    if user_queryset:
        db.delete(user_queryset)
        db.commit()
    return user_queryset

def generate_random_password(length=12):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


async def reset_and_email_password(db: Session, email: str):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            

        new_password = generate_random_password()
        user.password = hash_password(new_password)
        db.commit()

        email_body = f"""
🌟 <strong>Hi {user.fullName.split()[0]}!</strong> 🌟<br><br>

🔐 <strong>Your new temporary password:</strong><br>
<span style="font-size: 18px; color: #FF6B6B; background: #FFF5F5; padding: 8px 12px; border-radius: 4px; display: inline-block; margin: 8px 0;">
    {new_password}
</span><br><br>

📝 <em>Quick steps to get back to learning:</em><br>
1️⃣ 🖱️ <strong>Login</strong> with this temporary password<br>
2️⃣ 🔄 <strong>Change</strong> to a new password<br>
3️⃣ 🎉 <strong>Continue</strong> your learning journey!<br><br>

⏰ <span style="color: #6B7280;">This password expires in 24 hours</span><br><br>

💡 <strong>Pro Tip:</strong> Use a password manager like Bitwarden or 1Password!<br><br>

<img src="https://media.giphy.com/media/L95W4wv8nnb9K/giphy.gif" alt="Lock animation" style="max-width: 200px; border-radius: 8px; margin: 10px 0;"><br><br>

<hr style="border: 1px dashed #E5E7EB; margin: 20px 0;">

<small>🤖 <em>Automated message from Tameri Study AI Bot</em><br>
Need help? Reply to this email!</small>
"""
        reset_link = "https://study.tameri.tech/docs"
        # Properly await the coroutine
        email_sent = await send_email(
            recipient=user.email,
            subject="Your New Password",
            body=email_body,
            button_url=reset_link,
            button_text="Reset Password"
        )

        if not email_sent:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to send email")

        return {"message": "New password sent to your email"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def update_user_password(db: Session, user_id: int, old_password: str, new_password: str, confirm_password: str):
    try:
        # Retrieve the user from the database
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(old_password, user.password):
            raise HTTPException(status_code=400, detail="Old password is incorrect")

        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="New password and confirmation do not match")
        
        hashed_new_password = hash_password(new_password)
        user.password = hashed_new_password
        db.commit()
        return {"message": "Password updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating the password: " + str(e))
    
    