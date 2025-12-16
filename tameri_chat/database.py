from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


CHAT_SQLALCHEMY_DATABASE_URL = os.getenv("CHAT_SQLALCHEMY_DATABASE_URL")

engine = create_engine(CHAT_SQLALCHEMY_DATABASE_URL, 
                       pool_size=10,        # Increase persistent connections
                        max_overflow=20,     # Increase temp connections allowed
                        pool_timeout=10,     # Keep or adjust based on your needs
                        pool_recycle=3600,
                        pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()