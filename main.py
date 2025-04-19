from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, APIRouter, HTTPException
import services.users_services as users_services, database.models as models, database.schemas as schemas
from database.db import get_db, engine
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status
from utils.general_utils import create_access_token
from database.schemas import LoginRequest, TokenResponse
from fastapi.security import OAuth2PasswordBearer
from utils.general_utils import get_current_user
from utils.ollama_utils import generate_from_ollama, summarize_with_ollama
from utils.video_utils import save_video_temporarily, extract_audio, transcribe_audio, cleanup_files
from utils.pdf_utils import summarize_pdf, generate_mcqs_from_pdf, extract_pdf_text
from utils.image_utils import extract_text_from_image, summarize_image_text, generate_mcqs_from_image_text


app = FastAPI()

@app.post("/api/register", response_model=schemas.User)
def register_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return users_services.create_user(db, user)


@app.post("/api/login", response_model=TokenResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = users_services.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/get-users", response_model=list[schemas.User]) 
def get_all_users(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  # 👈 required!
):
    return users_services.get_users(db)


@app.get("/api/get-user/{id}", response_model=schemas.User)
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  # 👈 required!
):
    user_queryset = users_services.get_user(db, id)
    if user_queryset:
        return user_queryset
    raise HTTPException(status_code=404, detail="Invalid user id provided!")


@app.put("/api/user/update/{id}", response_model=schemas.User)
def update_user(user: schemas.UserCreate, id:int, db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)):
    db_update = users_services.update_user(db, user, id)
    if not db_update:
        raise HTTPException(status_code=404, detail="Book not found!")
    return db_update

@app.delete("/api/delete/user/{id}", response_model=schemas.User)
def delete_user(id:int, db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user) ):
    delete_entry = users_services.delete_user(db, id) 
    if delete_entry:
        return delete_entry
    raise HTTPException(status_code=404, detail="Usernot found!")


@app.post("/api/extract-pdf-text")
async def upload_pdf(file: UploadFile = File(...)):
    return await extract_pdf_text(file)


@app.post("/api/summarize-pdf")
async def summarize_pdf_route(file: UploadFile = File(...)):
    return await summarize_pdf(file)


@app.post("/api/generate-mcqs-from-pdf/")
async def generate_mcqs_route(file: UploadFile = File(...)):
    return await generate_mcqs_from_pdf(file)


@app.post("/api/extract-text-from-image/")
async def extract_text_from_image_route(file: UploadFile = File(...)):
    return await extract_text_from_image(file)


@app.post("/api/summarize-imgae-text")
async def summarize_image_route(file: UploadFile = File(...)):
    return await summarize_image_text(file)


@app.post("/api/generate-mcqs-from-image-text/")
async def generate_mcqs_image_route(file: UploadFile = File(...)):
    return await generate_mcqs_from_image_text(file)


@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    video_data = await file.read()
    
    video_path = save_video_temporarily(video_data)
    audio_path = extract_audio(video_path)
    transcription = transcribe_audio(audio_path)
    cleanup_files(video_path, audio_path)

    summary = summarize_with_ollama(transcription)

    return {
        "transcription": transcription,
        "summary_and_questions": summary,
    }


# uvicorn main:app --reload
# http://127.0.0.1:8000/docs 
 