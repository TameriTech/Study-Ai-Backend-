from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from database import schemas
from database.db import get_db
import services.users_services as users_services
from utils.general_utils import create_access_token
from database.schemas import FacebookToken, LoginRequest, SocialLoginResponse, TokenResponse, UserBase
from services.google_auth import verify_google_token, get_or_create_user
from database.schemas import GoogleToken, PasswordResetRequest
from services.facebook_auth import FacebookAuthService
import os
from utils.i18n import translate, get_lang_from_request

router = APIRouter(prefix="/api")

facebook_auth = FacebookAuthService(
    app_id=os.getenv("FACEBOOK_APP_ID"),
    app_secret=os.getenv("FACEBOOK_APP_SECRET")
)

@router.post("/register", tags=["Auth"])
async def register_new_user(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    lang = get_lang_from_request(request)
    try:
        created_user = await users_services.create_user(db, user, lang)
        return JSONResponse(
            content=jsonable_encoder(created_user),
            headers={"Content-Language": lang}
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=translate("registration_error", lang),
            headers={"Content-Language": lang}
        )

@router.post("/login", response_model=TokenResponse, tags=["Auth"])
def login_user(
    request: Request,
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    user = users_services.authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate("invalid_credentials", lang),
            headers={"Content-Language": lang}
        )

    access_token = create_access_token(data={"sub": user.email})

    return JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": jsonable_encoder(user)
        },
        headers={"Content-Language": lang}
    )

@router.post("/login/facebook", response_model=SocialLoginResponse, tags=["Auth"])
async def login_with_facebook(
    request: Request,
    fb_token: FacebookToken,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        fb_user = await facebook_auth.verify_facebook_token(fb_token.access_token)
        user = facebook_auth.get_or_create_user(db, fb_user)
        access_token = create_access_token(data={"sub": user.email})

        return JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "user": jsonable_encoder(user),
                "provider": "facebook"
            },
            headers={"Content-Language": lang}
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=translate("facebook_auth_error", lang),
            headers={"Content-Language": lang}
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=translate("internal_server_error", lang),
            headers={"Content-Language": lang}
        )

@router.post("/login/google", response_model=TokenResponse, tags=["Auth"])
async def login_with_google(
    request: Request,
    google_token: GoogleToken,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    try:
        google_user = await verify_google_token(google_token.id_token)
        user = get_or_create_user(db, google_user)
        access_token = create_access_token(data={"sub": user.email})

        return JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "user": jsonable_encoder({
                    "id": user.id,
                    "email": user.email,
                    "fullName": user.fullName
                })
            },
            headers={"Content-Language": lang}
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=translate("google_auth_error", lang),
            headers={"Content-Language": lang}
        )

@router.get("/get-user/{id}", response_model=schemas.User, tags=["User"])
def get_user_by_id(
    request: Request,
    id: int,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    user_queryset = users_services.get_user(db, id)
    if not user_queryset:
        raise HTTPException(
            status_code=404,
            detail=translate("invalid_user_id", lang),
            headers={"Content-Language": lang}
        )

    users_services.calculate_user_feedback_statistics(db, id)
    db.refresh(user_queryset)

    return JSONResponse(
        content=jsonable_encoder(user_queryset),
        headers={"Content-Language": lang}
    )

@router.put("/user/update/{id}", response_model=schemas.User, tags=["User"])
def update_user(
    request: Request,
    id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    db_update = users_services.update_user(db, user, id)
    if not db_update:
        raise HTTPException(
            status_code=404,
            detail=translate("user_not_found", lang),
            headers={"Content-Language": lang}
        )
    return JSONResponse(
        content=jsonable_encoder(db_update),
        headers={"Content-Language": lang}
    )

@router.delete("/delete/user/{id}", response_model=schemas.User, tags=["User"])
def delete_user(id: int, db: Session = Depends(get_db)):
    delete_entry = users_services.delete_user(db, id)
    if delete_entry:
        return JSONResponse(content=jsonable_encoder(delete_entry))
    raise HTTPException(status_code=404, detail="User not found!")

@router.post("/forgot-password", tags=["Auth"])
async def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    return await users_services.reset_and_email_password(db, request.email)

@router.post("/update-password/", tags=["Auth"])
async def update_password(
    request: Request,
    user_id: int,
    old_password: str,
    new_password: str,
    confirm_password: str,
    db: Session = Depends(get_db)
):
    lang = get_lang_from_request(request)
    result = await users_services.update_user_password(db, user_id, old_password, new_password, confirm_password)
    if result:
        return JSONResponse(
            content={"message": translate("password_updated", lang)},
            headers={"Content-Language": lang}
        )
    raise HTTPException(
        status_code=400,
        detail=translate("password_update_failed", lang),
        headers={"Content-Language": lang}
    )
