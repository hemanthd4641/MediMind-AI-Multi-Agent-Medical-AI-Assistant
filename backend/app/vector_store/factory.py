from backend.app.vector_store.base import VectorStore
from backend.app.vector_store.pinecone_store import PineconeVectorStore

class VectorStoreFactory:
    """Factory to instantiate the appropriate VectorStore."""

    @staticmethod
    def get_store() -> VectorStore:
        # In the future, this can be driven by a config variable (e.g. VECTOR_STORE_PROVIDER)
        # For now, we are fully migrating to Pinecone as per requirements.
        return PineconeVectorStore()
