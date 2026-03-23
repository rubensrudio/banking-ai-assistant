from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):
    """Abstract interface for text embedding providers."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensionality of the embedding vectors."""

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a batch of texts.
        Returns a list of float vectors, one per input text.
        """

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """
        Embed a single query string.
        May use a different prompt prefix than embed_texts for asymmetric models.
        """
