from fastapi import FastAPI
from api import users, courses, documents, vocabulary, segments, feedback, quiz

app = FastAPI()

app.include_router(users.router)
app.include_router(documents.router)
app.include_router(courses.router)
app.include_router(vocabulary.router)
app.include_router(quiz.router)
app.include_router(feedback.router)


