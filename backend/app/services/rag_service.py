from collections.abc import Iterator

from app.core.config import get_settings
from app.core.logger import get_logger
from app.domain.models import RAGResponse, RetrievedChunk
from app.providers.base_embedding import BaseEmbeddingProvider
from app.providers.base_llm import BaseLLMProvider
from app.rag.prompt_builder import assess_confidence, build_rag_prompt
from app.rag.vector_store import PineconeVectorStore

logger = get_logger(__name__)


class RAGService:
    """
    Orchestrates the full RAG pipeline:
    Embed query → Retrieve chunks → Build prompt → Generate answer
    """

    def __init__(
        self,
        embedding: BaseEmbeddingProvider,
        store: PineconeVectorStore,
        llm: BaseLLMProvider,
    ):
        self._embedding = embedding
        self._store = store
        self._llm = llm
        self._settings = get_settings()

    def ask(self, query: str) -> RAGResponse:
        """
        Full RAG pipeline (synchronous).
        Returns a RAGResponse with answer, sources, and confidence level.
        """
        logger.info(f"RAG query: '{query[:80]}'")

        # 1. Embed the query
        query_vector = self._embedding.embed_query(query)

        # 2. Retrieve relevant chunks from Pinecone
        chunks: list[RetrievedChunk] = self._store.search(
            query_vector, top_k=self._settings.rag_top_k
        )
        logger.debug(f"Retrieved {len(chunks)} chunks above score threshold")

        # 3. Build the anti-hallucination prompt
        messages = build_rag_prompt(query, chunks)

        # 4. Generate answer
        answer = self._llm.complete(messages, temperature=0.1)

        # 5. Assess confidence from retrieval scores
        confidence = assess_confidence(chunks)

        logger.info(
            f"RAG complete — confidence={confidence}, "
            f"chunks={len(chunks)}, answer_len={len(answer)}"
        )

        return RAGResponse(
            answer=answer,
            sources=chunks,
            context_used=messages[-1]["content"],
            confidence=confidence,
        )

    def ask_stream(self, query: str) -> Iterator[str]:
        """
        Streaming variant. Yields answer tokens as they are generated.
        Sources are not returned inline; use ask() if you need them.
        """
        query_vector = self._embedding.embed_query(query)
        chunks = self._store.search(query_vector, top_k=self._settings.rag_top_k)
        messages = build_rag_prompt(query, chunks)
        yield from self._llm.stream(messages, temperature=0.1)
