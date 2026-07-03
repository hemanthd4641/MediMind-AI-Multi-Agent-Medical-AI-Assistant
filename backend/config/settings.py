from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    # Application settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MediMind AI"
    VERSION: str = "1.0.0"

    # Database settings
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # JWT settings
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # AI / Groq settings
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        env_file_encoding = "utf-8"
        extra = "allow"

# Singleton instance
settings = Settings()
