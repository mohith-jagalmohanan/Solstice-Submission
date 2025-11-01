# core/ingestion_service.py
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.document_loader import DocumentLoader
from data_access.vector_store import VectorStore

class IngestionService:
    def __init__(self, vector_store: VectorStore):
        self._vector_store = vector_store
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    def ingest_directory(self, dir_path: str):
        print(f"Starting ingestion from directory: {dir_path}")
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if os.path.isfile(file_path):
                try:
                    print(f"Processing file: {filename}")
                    loader = DocumentLoader(file_path)
                    documents = loader.load()
                    
                    split_docs = self.text_splitter.split_documents(documents)
                    self._vector_store.add_documents(split_docs)
                except Exception as e:
                    print(f"Failed to process {filename}: {e}") # Graceful error handling [cite: 32]
        print("Directory ingestion complete.")