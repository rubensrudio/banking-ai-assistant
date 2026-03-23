"""
Sprint 3 Tests — RAGService orchestration (unit tests, no external services).
Embedding provider, vector store, and LLM are all mocked.
"""
import pytest
from unittest.mock import MagicMock, call

from app.domain.models import RAGResponse, RetrievedChunk
from app.services.rag_service import RAGService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_retrieved_chunk(score: float = 0.85, source: str = "banking.pdf") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="c0",
        doc_id="doc",
        text="Savings account offers 4.5% APY with no monthly fees.",
        source_file=source,
        page_number=1,
        score=score,
    )


def make_service(chunks: list[RetrievedChunk], llm_answer: str = "The APY is 4.5%."):
    embedding = MagicMock()
    embedding.embed_query.return_value = [0.1] * 384

    store = MagicMock()
    store.search.return_value = chunks

    llm = MagicMock()
    llm.complete.return_value = llm_answer
    llm.stream.return_value = iter(["The ", "APY ", "is ", "4.5%."])

    return RAGService(embedding=embedding, store=store, llm=llm), embedding, store, llm


# ---------------------------------------------------------------------------
# RAGService.ask() tests
# ---------------------------------------------------------------------------


class TestRAGServiceAsk:
    def test_returns_rag_response(self):
        svc, *_ = make_service([make_retrieved_chunk()])
        result = svc.ask("What is the APY?")
        assert isinstance(result, RAGResponse)

    def test_answer_matches_llm_output(self):
        svc, *_ = make_service([make_retrieved_chunk()], llm_answer="The rate is 4.5%.")
        result = svc.ask("What is the rate?")
        assert result.answer == "The rate is 4.5%."

    def test_sources_match_retrieved_chunks(self):
        chunks = [make_retrieved_chunk(score=0.90)]
        svc, *_ = make_service(chunks)
        result = svc.ask("query")
        assert result.sources == chunks

    def test_embed_query_called_once_with_query(self):
        svc, embedding, store, llm = make_service([make_retrieved_chunk()])
        svc.ask("What is the minimum deposit?")
        embedding.embed_query.assert_called_once_with("What is the minimum deposit?")

    def test_store_search_called_with_embedded_vector(self):
        svc, embedding, store, llm = make_service([make_retrieved_chunk()])
        embedding.embed_query.return_value = [0.5] * 384
        svc.ask("query")
        call_args = store.search.call_args
        assert call_args[0][0] == [0.5] * 384

    def test_llm_complete_called_once(self):
        svc, _, _, llm = make_service([make_retrieved_chunk()])
        svc.ask("query")
        llm.complete.assert_called_once()

    def test_llm_receives_two_messages(self):
        svc, _, _, llm = make_service([make_retrieved_chunk()])
        svc.ask("query")
        messages_arg = llm.complete.call_args[0][0]
        assert len(messages_arg) == 2

    def test_confidence_high_for_high_score_chunks(self):
        chunks = [make_retrieved_chunk(score=0.92)]
        svc, *_ = make_service(chunks)
        result = svc.ask("query")
        assert result.confidence == "high"

    def test_confidence_insufficient_when_no_chunks(self):
        svc, *_ = make_service([])
        result = svc.ask("query")
        assert result.confidence == "insufficient"

    def test_context_used_contains_chunk_text(self):
        chunk = make_retrieved_chunk()
        svc, *_ = make_service([chunk])
        result = svc.ask("query")
        assert chunk.text in result.context_used

    def test_context_used_says_no_docs_when_empty(self):
        svc, *_ = make_service([])
        result = svc.ask("query")
        assert "No relevant documents found" in result.context_used


# ---------------------------------------------------------------------------
# RAGService.ask_stream() tests
# ---------------------------------------------------------------------------


class TestRAGServiceAskStream:
    def test_yields_tokens(self):
        svc, *_ = make_service([make_retrieved_chunk()])
        tokens = list(svc.ask_stream("query"))
        assert len(tokens) > 0

    def test_concatenated_tokens_form_answer(self):
        svc, _, _, llm = make_service([make_retrieved_chunk()])
        llm.stream.return_value = iter(["Hello ", "world."])
        tokens = list(svc.ask_stream("query"))
        assert "".join(tokens) == "Hello world."

    def test_embed_query_called_in_stream(self):
        svc, embedding, _, _ = make_service([make_retrieved_chunk()])
        list(svc.ask_stream("streaming query"))
        embedding.embed_query.assert_called_once_with("streaming query")

    def test_llm_stream_called_not_complete(self):
        svc, _, _, llm = make_service([make_retrieved_chunk()])
        list(svc.ask_stream("query"))
        llm.stream.assert_called_once()
        llm.complete.assert_not_called()
