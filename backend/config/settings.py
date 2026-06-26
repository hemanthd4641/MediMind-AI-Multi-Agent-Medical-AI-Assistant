from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    # Application settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MediMind AI"
    VERSION: str = "1.0.0"

    # Database settings
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")

    # JWT settings
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        env_file_encoding = "utf-8"

# Singleton instance
settings = Settings()
