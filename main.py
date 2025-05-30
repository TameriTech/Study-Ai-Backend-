import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import websockets
from api import users, courses, documents, vocabulary, segments, feedback, quiz, comment, email, websocket
from fastapi.middleware.cors import CORSMiddleware
from chatbot.routers import chat, documentsegments
from database.db import create_tables, drop_tables

app = FastAPI()
CREATE_TABLES =  drop_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
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

@app.get("/")
async def root():
    return {"message": "Welcome Tameri Study AI"}


