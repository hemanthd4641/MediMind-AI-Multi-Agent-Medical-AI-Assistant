from backend.app.config import settings
import os

PINECONE_API_KEY = getattr(settings, "PINECONE_API_KEY", "")
PINECONE_INDEX = getattr(settings, "PINECONE_INDEX", "medimid-ai-index")
PINECONE_ENVIRONMENT = getattr(settings, "PINECONE_REGION", "us-east-1")
PINECONE_NAMESPACE_MEDICAL_KNOWLEDGE = getattr(settings, "PINECONE_NAMESPACE", "medical-knowledge")
PINECONE_NAMESPACE_PATIENT_REPORTS = os.getenv("PINECONE_NAMESPACE_PATIENT_REPORTS", "patient-reports")

# Configurable embedding dimension if we don't dynamically check
EMBEDDING_DIMENSION = 768 # Default for BAAI/bge-base-en-v1.5
