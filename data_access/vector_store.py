# data_access/vector_store.py
from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore as LangChainVectorStore
from langchain_milvus import Milvus
from core.config import config

class VectorStore(ABC):
    """Abstract base class for a vector store."""
    @abstractmethod
    def add_documents(self, documents: List[Document]):
        raise NotImplementedError

    @abstractmethod
    def as_retriever(self):
        raise NotImplementedError

class MilvusVectorStore(VectorStore):
    """Milvus implementation of the VectorStore interface."""
    def __init__(self, embedding_fn: Embeddings):
        self._embedding_fn = embedding_fn
        # Initialize or connect to the vector store on creation
        # This is a simplified approach. In prod, connection management is key.
        self._client: LangChainVectorStore = self._get_or_create_store()

    def _get_or_create_store(self) -> LangChainVectorStore:
        # A simple way to check if a collection exists would be needed here.
        # For this example, we assume we can connect if the URI is valid.
        try:
            # Connect to an existing Milvus store
            store = Milvus(
                embedding_function=self._embedding_fn,
                connection_args={"uri": config.persisted_db_uri},
                collection_name="rag_documents" # Use a consistent collection name
            )
        except Exception:
            # This is a simplification. A real check for collection existence is better.
            # Here we assume an error means we need to create it (by adding docs).
            # Returning a placeholder or handling differently might be necessary.
             store = None
        return store


    def add_documents(self, documents: List[Document]):
        """Adds documents to Milvus, creating the store if it's the first time."""
        print(f"Adding {len(documents)} document chunks to Milvus.")
        self._client = Milvus.from_documents(
            documents=documents,
            embedding=self._embedding_fn,
            connection_args={"uri": config.persisted_db_uri},
            collection_name="rag_documents",
            index_params={
                "metric_type": config.similarity_metric,
                "index_type": config.retrieval_algorithm,
            }
        )
        print("Ingestion to Milvus completed.")

    def as_retriever(self):
        if not self._client:
            raise ValueError("Vector store not initialized. Ingest documents first.")
        return self._client.as_retriever(
            search_type="similarity",
            search_kwargs={"k": config.top_k_retrieval}
        )