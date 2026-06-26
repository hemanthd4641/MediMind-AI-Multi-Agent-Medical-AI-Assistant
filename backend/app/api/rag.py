import structlog
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.database import get_db
from backend.app.deps import get_current_user
from backend.app.rag.ingestion.pipeline import IngestionPipeline
from backend.app.models.rag_models import MedicalDocument
from backend.app.rag.retriever.vector_search import VectorSearch

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG Knowledge Base"])

@router.post(
    "/upload",
    summary="Upload Document",
    description="Upload a medical document (PDF, TXT, MD) to the knowledge base.",
)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.get("sub", "unknown")
    logger.info("Uploading document", user_id=user_id, file_name=file.filename)
    
    if not file.filename.lower().endswith((".pdf", ".txt", ".md")):
        raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD files are supported.")
        
    try:
        content = await file.read()
        pipeline = IngestionPipeline(db)
        doc = pipeline.ingest_document(
            file_bytes=content,
            file_name=file.filename,
            title=file.filename,
            category=category
        )
        return {"message": "Document uploaded and processed successfully", "document_id": str(doc.id)}
    except Exception as e:
        logger.error("Failed to ingest document", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")

@router.get(
    "/documents",
    summary="List Documents",
    description="Get a list of all documents in the knowledge base.",
)
def list_documents(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = db.query(MedicalDocument).order_by(MedicalDocument.created_at.desc()).all()
    return [{
        "id": str(d.id),
        "title": d.title,
        "category": d.category,
        "source": d.source,
        "file_name": d.file_name,
        "created_at": d.created_at
    } for d in docs]

@router.delete(
    "/document/{document_id}",
    summary="Delete Document",
    description="Delete a document and all its vector chunks from the knowledge base.",
)
def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(MedicalDocument).filter(MedicalDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}

@router.post(
    "/search",
    summary="Search Knowledge Base",
    description="Perform a vector search against the knowledge base.",
)
def search_documents(
    query: str = Form(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        results = VectorSearch.search(db, query=query, top_k=5)
        return {"query": query, "results": results}
    except Exception as e:
        logger.error("Search failed", error=str(e))
        raise HTTPException(status_code=500, detail="Search failed")
