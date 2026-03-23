from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "AI Banking Assistant"
    api_version: str = "1.0.0"

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index_name: str = "banking-docs"
    pinecone_environment: str = "gcp-starter"

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # LM Studio
    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_api_key: str = "lm-studio"
    lmstudio_chat_model: str = ""

    # RAG parameters
    rag_top_k: int = 5
    rag_chunk_size: int = 1200
    rag_chunk_overlap: int = 200
    rag_min_score: float = 0.70

    model_config = {"env_file": ".env", "case_sensitive": False}

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
