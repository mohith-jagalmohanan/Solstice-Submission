# core/config.py
import json
from pydantic import BaseModel, Field
from pathlib import Path

class GenerationLLMConfig(BaseModel):
    provider: str = "ollama"
    model: str = "gemma3:1b"
    temperature: float = 0.7
    max_tokens: int = Field(1024, alias='max_tokens')

class AppConfig(BaseModel):
    persist_files_directory: str = "./Files"
    vector_db: str = "milvus"
    persisted_db_uri: str = Field(..., alias='persisted_db') # Renamed for clarity
    top_k_retrieval: int = 10
    top_k_ranking: int = 5
    embedding_model_name: str = Field(..., alias='embedding_model') # Full name after mapping
    reranker_model: str = "BAAI/bge-reranker-base"
    similarity_metric: str = "L2"
    retrieval_algorithm: str = "AUTOINDEX"
    generation_llm: GenerationLLMConfig

def load_config(config_path="config.json", models_mapping_path="models_mapping.json") -> AppConfig:
    """Loads configuration from JSON files and maps model names."""
    with open(config_path) as f:
        config_data = json.load(f)
    
    with open(models_mapping_path) as f:
        models_mapping = json.load(f)

    # Map the short name to the full HuggingFace model name
    model_short_name = config_data.get("embedding_model", "MiniLM")
    config_data["embedding_model"] = models_mapping.get(model_short_name, "sentence-transformers/all-MiniLM-L6-v2")

    return AppConfig(**config_data)

# Load config globally for easy access in other modules
config = load_config()