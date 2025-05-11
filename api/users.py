from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import schemas
from database.db import get_db
import services.users_services as users_services
from utils.general_utils import create_access_token
from database.schemas import LoginRequest, TokenResponse, UserBase

router = APIRouter(prefix="/api", tags=["User"])

@router.post("/register", response_model=schemas.User)
def register_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return users_services.create_user(db, user)

@router.post("/login", response_model=TokenResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = users_services.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user  # SQLAlchemy model will be auto-converted by Pydantic if compatible
    }

@router.get("/get-users", response_model=list[schemas.User]) 
def get_all_users(db: Session = Depends(get_db)):
    return users_services.get_users(db)

@router.get("/get-user/{id}", response_model=schemas.User)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user_queryset = users_services.get_user(db, id)
    if user_queryset:
        return user_queryset
    raise HTTPException(status_code=404, detail="Invalid user id provided!")

@router.put("/user/update/{id}", response_model=schemas.User)
def update_user(user: schemas.UserCreate, id:int, db: Session = Depends(get_db)):
    db_update = users_services.update_user(db, user, id)
    if not db_update:
        raise HTTPException(status_code=404, detail="Book not found!")
    return db_update

@router.delete("/delete/user/{id}", response_model=schemas.User)
def delete_user(id:int, db: Session = Depends(get_db)):
    delete_entry = users_services.delete_user(db, id) 
    if delete_entry:
        return delete_entry
    raise HTTPException(status_code=404, detail="User not found!")