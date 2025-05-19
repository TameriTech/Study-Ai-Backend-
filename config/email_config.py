# config/email_config.py
import os
from pydantic_settings import BaseSettings
from pydantic import BaseModel, SecretStr, Field
from dotenv import load_dotenv
load_dotenv()

class EmailSettings(BaseSettings):
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")  # Default if not found
    SMTP_PORT: int = os.getenv("SMTP_PORT", 587)
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_FROM: str = os.getenv("SMTP_FROM")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'

email_settings = EmailSettings()

class EmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str
    button_url: str = None
    button_text: str = None