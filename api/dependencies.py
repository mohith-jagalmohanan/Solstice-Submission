# api/dependencies.py
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from core.config import config
from data_access.vector_store import MilvusVectorStore, VectorStore
from core.ingestion_service import IngestionService
from core.rag_service import RAGService

# Use lru_cache to ensure these are singletons
@lru_cache(maxsize=None)
def get_embedding_function():
    return HuggingFaceEmbeddings(model_name=config.embedding_model_name)

@lru_cache(maxsize=None)
def get_vector_store() -> VectorStore:
    return MilvusVectorStore(embedding_fn=get_embedding_function())

@lru_cache(maxsize=None)
def get_ingestion_service() -> IngestionService:
    return IngestionService(vector_store=get_vector_store())

@lru_cache(maxsize=None)
def get_rag_service() -> RAGService:
    # Note: RAGService needs an initialized retriever. This assumes ingestion has happened.
    # In a real app, you might have a health check to confirm this.
    return RAGService(vector_store=get_vector_store())