import os
from pydantic_settings import BaseSettings
from pydantic import EmailStr, Field

class Settings(BaseSettings):
    # Core settings
    DEBUG: bool = Field(default=False, env='DEBUG')
    PROJECT_NAME: str = "MediMind AI"
    VERSION: str = "0.1.0"

    # Database
    POSTGRES_USER: str = Field(..., env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field(..., env='POSTGRES_PASSWORD')
    POSTGRES_HOST: str = Field(..., env='POSTGRES_HOST')
    POSTGRES_PORT: str = Field(..., env='POSTGRES_PORT')
    POSTGRES_DB: str = Field(..., env='POSTGRES_DB')
    # Optional full URL; if not provided we build it from host/port
    DATABASE_URL: str | None = None

    # JWT
    JWT_SECRET_KEY: str = Field(..., env='JWT_SECRET_KEY')
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Additional optional settings (allow extra to avoid validation errors)
    API_V1_STR: str = Field('/api/v1', env='API_V1_STR')

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL:
            # Build URL from host and port
            server = f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{server}/{self.POSTGRES_DB}"
            )

settings = Settings()
