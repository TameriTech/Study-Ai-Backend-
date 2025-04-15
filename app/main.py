from fastapi import FastAPI
from app.routers.pdf_router import router as pdf_router

app = FastAPI()

app.include_router(pdf_router, prefix="/pdf", tags=["PDF"])
