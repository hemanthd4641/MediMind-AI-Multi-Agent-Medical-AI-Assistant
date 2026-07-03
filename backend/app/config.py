import os
from pydantic_settings import BaseSettings
from pydantic import EmailStr, Field

class Settings(BaseSettings):
    # Core settings
    DEBUG: bool = Field(default=False, env='DEBUG')
    PROJECT_NAME: str = "MediMind AI"
    VERSION: str = "0.1.0"

    # Database (Supabase)
    DATABASE_URL: str = Field(..., env='DATABASE_URL')

    # JWT
    JWT_SECRET_KEY: str = Field(..., env='JWT_SECRET_KEY')
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI / Groq settings
    GROQ_API_KEY: str = Field(..., env='GROQ_API_KEY')
    DEFAULT_MODEL: str = Field(default='llama-3.3-70b-versatile', env='DEFAULT_MODEL')
    LLM_TEMPERATURE: float = Field(default=0.2, env='LLM_TEMPERATURE')
    MAX_ITERATIONS: int = Field(default=3, env='MAX_ITERATIONS')

    # Vector Database (Pinecone)
    PINECONE_API_KEY: str = Field(..., env='PINECONE_API_KEY')
    PINECONE_INDEX: str = Field(..., env='PINECONE_INDEX')
    PINECONE_NAMESPACE: str = Field(default='medical-knowledge', env='PINECONE_NAMESPACE')
    PINECONE_REGION: str = Field(default='us-east-1', env='PINECONE_REGION')

    # Embeddings Configuration
    EMBEDDING_PROVIDER: str = Field(default='local', env='EMBEDDING_PROVIDER') # 'local' or 'huggingface_api'
    EMBEDDING_MODEL: str = Field(default='BAAI/bge-base-en-v1.5', env='EMBEDDING_MODEL')
    DEVICE: str = Field(default='auto', env='DEVICE') # 'cpu', 'cuda', or 'auto'
    
    # Hugging Face API Specifics
    HF_TOKEN: str = Field(..., env='HF_TOKEN')
    HF_API_TIMEOUT: int = Field(default=10, env='HF_API_TIMEOUT')
    HF_MAX_RETRIES: int = Field(default=3, env='HF_MAX_RETRIES')

    # Additional optional settings (allow extra to avoid validation errors)
    API_V1_STR: str = Field('/api/v1', env='API_V1_STR')

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()
