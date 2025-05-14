# config/email_config.py
from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field

class EmailSettings(BaseSettings):
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USERNAME: str = Field(default="tameri.tech25@gmail.com")
    SMTP_PASSWORD: SecretStr = Field(default="xvzi wxvd cceq oixh")
    SMTP_FROM: str = Field(default="tameri.tech25@gmail.com")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'

email_settings = EmailSettings()