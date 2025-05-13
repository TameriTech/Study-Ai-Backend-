from database.models import User
from sqlalchemy.orm import Session
from database.schemas import UserCreate, UserUpdate
from utils.general_utils import hash_password
from utils.general_utils import verify_password
from fastapi import HTTPException, status

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.password):
        return user
    return None

def create_user(db: Session, data: UserCreate):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # If not, create the user
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
    return user_instance


def get_users(db: Session):
    return db.query(User).all()

def get_user(db: Session, user_id:int):
    return db.query(User).filter(User.id == user_id).first()

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

