import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api import users, courses, documents, vocabulary, segments, feedback, quiz, comment, email, websocket
from fastapi.middleware.cors import CORSMiddleware
from chatbot.routers import chat, documentsegments
from database.db import create_tables, drop_tables
import tameri_chat.routers as routers
from tameri_chat.models import Base
from tameri_chat.database import engine

app = FastAPI()
CREATE_TABLES =  create_tables()
Base.metadata.create_all(bind=engine)
# DROP_TABLES =  drop_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(courses.router)
app.include_router(vocabulary.router)
app.include_router(quiz.router)
app.include_router(feedback.router)
app.include_router(comment.router)
app.include_router(documentsegments.router)
app.include_router(chat.router)
app.include_router(email.router)
app.include_router(websocket.router)
app.include_router(routers.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/tameri_chat/static", StaticFiles(directory="tameri_chat/static"), name="static")


@app.get("/")
async def root():
    return {"message": "Welcome Tameri Study AI"}


