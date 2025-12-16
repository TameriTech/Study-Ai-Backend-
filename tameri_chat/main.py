# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from fastapi.staticfiles import StaticFiles  # Add this import
# from models import Base
# from database import engine
# import routers

# # Create database tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI()

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include all routers
# app.include_router(routers.router)
# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/", StaticFiles(directory="static", html=True), name="static_html")