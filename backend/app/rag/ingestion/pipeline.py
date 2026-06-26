import structlog
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.rag_models import MedicalDocument, DocumentChunk
from backend.app.rag.loader.document_loader import DocumentLoader
from backend.app.rag.chunker.semantic_chunker import SemanticChunker
from backend.app.rag.embedder.embedding_service import embedding_service
import time

logger = structlog.get_logger(__name__)

class IngestionPipeline:
    """
    Coordinates loading, chunking, embedding, and storing documents.
    """

    def __init__(self, db: Session):
        self.db = db
        self.chunker = SemanticChunker()

    def ingest_document(self, file_bytes: bytes, file_name: str, title: str, category: str = None) -> MedicalDocument:
        t0 = time.perf_counter()
        
        # 1. Load
        logger.info("Loading document", file_name=file_name)
        pages = DocumentLoader.load(file_bytes, file_name)
        
        # 2. Chunk
        logger.info("Chunking document", pages=len(pages))
        chunks_data = self.chunker.chunk_document(pages)
        
        # 3. Embed
        logger.info("Generating embeddings", total_chunks=len(chunks_data))
        t_embed = time.perf_counter()
        texts_to_embed = [c["content"] for c in chunks_data]
        embeddings = embedding_service.embed_texts(texts_to_embed)
        embed_time = time.perf_counter() - t_embed
        logger.info("Embeddings generated", elapsed_ms=round(embed_time * 1000))

        # 4. Store
        doc = MedicalDocument(
            title=title,
            category=category,
            file_name=file_name,
            source="User Upload"
        )
        self.db.add(doc)
        self.db.flush() # get doc.id

        db_chunks = []
        for i, c_data in enumerate(chunks_data):
            db_chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=c_data["chunk_index"],
                content=c_data["content"],
                embedding=embeddings[i],
                page_number=c_data["page_number"],
                token_count=c_data["token_count"],
                metadata_=c_data["metadata"]
            )
            db_chunks.append(db_chunk)

        self.db.add_all(db_chunks)
        self.db.commit()
        
        total_time = time.perf_counter() - t0
        logger.info("Document ingestion complete", file_name=file_name, chunks=len(db_chunks), total_ms=round(total_time * 1000))
        
        return doc
