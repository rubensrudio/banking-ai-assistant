from abc import ABC, abstractmethod
from collections.abc import Iterator


class BaseLLMProvider(ABC):
    """Abstract interface for LLM completion providers."""

    @abstractmethod
    def complete(self, messages: list[dict], temperature: float = 0.1) -> str:
        """
        Synchronous chat completion.
        Returns the full response content as a string.
        """

    @abstractmethod
    def stream(self, messages: list[dict], temperature: float = 0.1) -> Iterator[str]:
        """
        Streaming chat completion.
        Yields string tokens as they are generated.
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The model identifier used for completions."""
