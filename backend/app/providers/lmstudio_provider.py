from collections.abc import Iterator
from functools import lru_cache

from app.core.config import get_settings
from app.core.logger import get_logger
from app.providers.base_llm import BaseLLMProvider

logger = get_logger(__name__)


class LMStudioProvider(BaseLLMProvider):
    """
    LLM provider using LM Studio's OpenAI-compatible local API.

    Requirements:
      - LM Studio installed and running
      - A model loaded in LM Studio
      - Server started on port 1234 (default)
      - LMSTUDIO_CHAT_MODEL set in .env to the loaded model name
    """

    def __init__(self):
        from openai import OpenAI

        settings = get_settings()
        self._client = OpenAI(
            base_url=settings.lmstudio_base_url,
            api_key=settings.lmstudio_api_key,
        )
        self._model = settings.lmstudio_chat_model
        logger.info(f"LMStudio provider initialized — model: {self._model}")

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, messages: list[dict], temperature: float = 0.1) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
        )
        content = response.choices[0].message.content or ""
        logger.debug(f"LMStudio response: {len(content)} chars")
        return content

    def stream(self, messages: list[dict], temperature: float = 0.1) -> Iterator[str]:
        stream = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


@lru_cache(maxsize=1)
def get_llm_provider() -> BaseLLMProvider:
    """Singleton LLM provider. Client initialized once."""
    return LMStudioProvider()
