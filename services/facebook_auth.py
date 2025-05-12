import requests
from typing import Optional
from sqlalchemy.orm import Session
from database.schemas import UserCreate, FacebookToken
from utils.general_utils import hash_password
from database.models import User


class FacebookAuthService:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
    
    async def verify_facebook_token(self, access_token: str) -> dict:
        """Verify Facebook access token and return user info"""
        # Step 1: Verify token validity
        debug_url = f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={self.app_id}|{self.app_secret}"
        debug_res = requests.get(debug_url)
        debug_data = debug_res.json()
        
        if not debug_res.ok or not debug_data.get('data', {}).get('is_valid'):
            raise ValueError("Invalid Facebook token")
        
        # Step 2: Get user profile
        profile_url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}"
        profile_res = requests.get(profile_url)
        profile_data = profile_res.json()
        
        if not profile_res.ok:
            raise ValueError("Could not fetch Facebook profile")
        
        return profile_data
    
    def get_or_create_user(self, db: Session, fb_data: dict) -> User:
        """Get existing user or create new one from Facebook data"""
        user = db.query(User).filter(User.email == fb_data.get('email')).first()
        
        if not user:
            if not fb_data.get('email'):
                raise ValueError("Facebook account must have an email address")
                
            new_user = UserCreate(
                fullName=fb_data['name'],
                email=fb_data['email'],
                class_level="",
                password=hash_password("facebook_auth"),  # Dummy password
                best_subjects="",
                learning_objectives="",
                academic_level="",
                statistic=0
            )
            from services.users_services import create_user
            user = create_user(db, new_user)
        
        return user