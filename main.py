from fastapi import FastAPI
from api import users, courses, documents, vocabulary, segments, quiz, feedback

app = FastAPI()

app.include_router(users.router)
app.include_router(documents.router)
app.include_router(courses.router)
app.include_router(vocabulary.router)
