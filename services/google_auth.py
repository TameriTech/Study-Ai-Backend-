import os
from typing import Optional
import requests
from fastapi import HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from database.schemas import UserBase, UserCreate
from sqlalchemy.orm import Session
from utils.general_utils import hash_password
from . import users_services
from database.models import User


# Google OAuth Configuration
GOOGLE_WEB_CLIENT_ID = os.getenv("GOOGLE_WEB_CLIENT_ID")
GOOGLE_MOBILE_CLIENT_ID = os.getenv("GOOGLE_MOBILE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

async def verify_google_token(token: str) -> dict:
    try:
        # List of acceptable client IDs (web and mobile)
        accepted_client_ids = [
            os.getenv("GOOGLE_WEB_CLIENT_ID"),
            os.getenv("GOOGLE_MOBILE_CLIENT_ID")
        ]
        
        # Verify the token with any of the accepted client IDs
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
        
        # Check that the token is valid for one of your apps
        if idinfo['aud'] not in accepted_client_ids:
            raise ValueError('Invalid client ID.')
            
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return idinfo
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_or_create_user(db: Session, google_user: dict) -> UserBase:
    # Check if user exists by email
    user = db.query(User).filter(User.email == google_user["email"]).first()
    
    if user:
        return user
    
    # Create new user if doesn't exist
    new_user = UserCreate(
        fullName=google_user.get("name", ""),
        email=google_user["email"],
        class_level="",  # You might want to get this from somewhere else
        password=hash_password("google_auth"),  # Dummy password since they'll use Google auth
        best_subjects="",
        learning_objectives="",
        academic_level="",
        statistic=0
    )
    
    # Assuming you have a create_user function in users_services
    return users_services.create_user(db, new_user)