import structlog
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.rag_models import MedicalDocument
from backend.app.rag.loader.document_loader import DocumentLoader
from backend.app.rag.chunker.semantic_chunker import SemanticChunker
from backend.app.embeddings.service import embedding_service
from backend.app.vector_store.service import vector_store_service
from backend.app.ai.services.document_classifier import document_classifier_service
import time
import uuid
import datetime

logger = structlog.get_logger(__name__)

class IngestionPipeline:
    """
    Coordinates loading, chunking, embedding, and storing documents.
    """

    def __init__(self, db: Session):
        self.db = db
        self.chunker = SemanticChunker()

    async def ingest_document(self, file_bytes: bytes, file_name: str, title: str, user_id: str, category: str = None) -> MedicalDocument:
        t0 = time.perf_counter()
        
        # 1. Load
        logger.info("Loading document", file_name=file_name)
        pages = DocumentLoader.load(file_bytes, file_name)
        
        if not pages:
            raise ValueError("No text could be extracted from the document.")

        # 2. Classify Document
        first_page_text = pages[0].get("text", "")
        classification = await document_classifier_service.classify(file_name, category, first_page_text)
        logger.info("Document classified", document_type=classification.document_type, namespace=classification.namespace, confidence=classification.confidence)
        
        # 3. Chunk
        logger.info("Chunking document", pages=len(pages))
        chunks_data = self.chunker.chunk_document(pages)
        
        # 4. Embed
        logger.info("Generating embeddings", total_chunks=len(chunks_data))
        t_embed = time.perf_counter()
        texts_to_embed = [c["content"] for c in chunks_data]
        embeddings = embedding_service.batch_embed(texts_to_embed)
        embed_time = time.perf_counter() - t_embed
        logger.info("Embeddings generated", elapsed_ms=round(embed_time * 1000))

        # 5. Store in DB
        doc = MedicalDocument(
            title=title,
            category=classification.document_type,
            file_name=file_name,
            source="User Upload"
        )
        self.db.add(doc)
        self.db.flush() # get doc.id

        # 6. Store in Vector DB
        t_store = time.perf_counter()
        vectors_to_upsert = []
        upload_time = datetime.datetime.utcnow().isoformat()
        
        for i, c_data in enumerate(chunks_data):
            chunk_id = str(uuid.uuid4())
            metadata = {
                "document_id": str(doc.id),
                "document_name": doc.title,
                "document_type": classification.document_type,
                "namespace": classification.namespace,
                "patient_id": user_id,
                "page_number": c_data.get("page_number", 1),
                "chunk_number": i,
                "upload_time": upload_time,
                "content": c_data["content"]
            }
            # Optional extra metadata from chunker
            metadata.update(c_data.get("metadata", {}))
            
            vectors_to_upsert.append({
                "id": chunk_id,
                "values": embeddings[i],
                "metadata": metadata
            })

        vector_store_service.upsert_batch(vectors_to_upsert, namespace=classification.namespace)
        
        self.db.commit()
        
        total_time = time.perf_counter() - t0
        logger.info("Document ingestion complete", file_name=file_name, chunks=len(vectors_to_upsert), namespace=classification.namespace, total_ms=round(total_time * 1000))
        
        return doc
