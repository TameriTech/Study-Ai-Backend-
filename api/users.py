from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from requests import request
from sqlalchemy.orm import Session
from database import schemas
from database.db import get_db
import services.users_services as users_services
from utils.general_utils import create_access_token
from database.schemas import FacebookToken, LoginRequest, SocialLoginResponse, TokenResponse, UserBase
from fastapi.security import OAuth2PasswordBearer
from services.google_auth import verify_google_token, get_or_create_user
from database.schemas import GoogleToken, PasswordResetRequest
from database.db import get_db
from database.schemas import FacebookToken, SocialLoginResponse
from services.facebook_auth import FacebookAuthService
from utils.general_utils import create_access_token
import os
from utils.email import send_email  # you'll need to implement this

router = APIRouter(prefix="/api")
# Initialize Facebook service
facebook_auth = FacebookAuthService(
    app_id=os.getenv("FACEBOOK_APP_ID"),
    app_secret=os.getenv("FACEBOOK_APP_SECRET")
)

@router.post("/register", response_model=schemas.User, tags=["Auth"])
async def register_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return await users_services.create_user(db, user)

@router.post("/login", response_model=TokenResponse, tags=["Auth"])
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

@router.post("/login/facebook", response_model=SocialLoginResponse, tags=["Auth"])
async def login_with_facebook(
    fb_token: FacebookToken, 
    db: Session = Depends(get_db)
):
    try:
        # Verify token and get user info
        fb_user = await facebook_auth.verify_facebook_token(fb_token.access_token)
        
        # Get or create local user
        user = facebook_auth.get_or_create_user(db, fb_user)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
            "provider": "facebook"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post("/login/google", response_model=schemas.TokenResponse, tags=["Auth"])
async def login_with_google(google_token: schemas.GoogleToken, db: Session = Depends(get_db)):
    try:
        google_user = await verify_google_token(google_token.id_token)
        user = get_or_create_user(db, google_user)
        access_token = create_access_token(data={"sub": user.email})
        
        return JSONResponse({
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "fullName": user.fullName
                # Include other required user fields
            }
        })
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
            headers={"Content-Type": "application/json"}
        )

@router.get("/get-users", response_model=list[schemas.User], tags=["User"]) 
def get_all_users(db: Session = Depends(get_db)):
    return users_services.get_users(db)

@router.get("/get-user/{id}", response_model=schemas.User, tags=["User"])
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user_queryset = users_services.get_user(db, id)
    if user_queryset:
        return user_queryset
    raise HTTPException(status_code=404, detail="Invalid user id provided!")

@router.put("/user/update/{id}", response_model=schemas.User, tags=["User"])
def update_user(id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_update = users_services.update_user(db, user, id)
    if not db_update:
        raise HTTPException(status_code=404, detail="User not found!")
    return db_update

@router.delete("/delete/user/{id}", response_model=schemas.User, tags=["User"])
def delete_user(id:int, db: Session = Depends(get_db)):
    delete_entry = users_services.delete_user(db, id) 
    if delete_entry:
        return delete_entry
    raise HTTPException(status_code=404, detail="User not found!")

@router.post("/reset-password", tags=["User"])
async def reset_password(request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    return await users_services.reset_and_email_password(db, request.email)

@router.post("/send-email", tags=["User"])
async def test_email(email: str = Body(..., embed=True)):
    """Test endpoint for email sending"""
    test_result = await send_email(
        recipient=email,
        subject="Test Email",
        body="This is a test email from the server",
        button_url="https://yourapp.com/dashboard",
        button_text="Start Learning"
    )
    return {"success": test_result}