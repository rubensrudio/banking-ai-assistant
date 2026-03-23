from functools import lru_cache

from app.core.config import get_settings
from app.core.logger import get_logger
from app.providers.base_embedding import BaseEmbeddingProvider

logger = get_logger(__name__)


class SentenceTransformerEmbedding(BaseEmbeddingProvider):
    """
    Local embedding provider using Sentence Transformers.
    Default model: all-MiniLM-L6-v2 (384 dims, runs on CPU, ~80MB).
    No API key required.
    """

    def __init__(self, model_name: str | None = None):
        from sentence_transformers import SentenceTransformer

        settings = get_settings()
        name = model_name or settings.embedding_model
        logger.info(f"Loading embedding model: {name}")
        self._model = SentenceTransformer(name)
        self._dim: int = self._model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model ready — dimension: {self._dim}")

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            batch_size=32,
        )
        return [e.tolist() for e in embeddings]

    def embed_query(self, query: str) -> list[float]:
        return self.embed_texts([query])[0]


@lru_cache(maxsize=1)
def get_embedding_provider() -> BaseEmbeddingProvider:
    """Singleton embedding provider. Model is loaded once and cached."""
    return SentenceTransformerEmbedding()
