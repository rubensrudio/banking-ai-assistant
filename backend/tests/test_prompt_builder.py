"""
Sprint 3 Tests — Prompt builder and confidence assessment.
No external services required.
"""
import pytest

from app.domain.models import RetrievedChunk
from app.rag.prompt_builder import SYSTEM_PROMPT, assess_confidence, build_rag_prompt


def make_chunk(
    chunk_id: str = "doc-0",
    source_file: str = "banking.pdf",
    page_number: int | None = 1,
    score: float = 0.85,
    text: str = "Savings account offers 4.5% APY.",
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        doc_id="doc",
        text=text,
        source_file=source_file,
        page_number=page_number,
        score=score,
    )


class TestBuildRagPrompt:
    def test_returns_two_messages(self):
        messages = build_rag_prompt("What is the APY?", [make_chunk()])
        assert len(messages) == 2

    def test_first_message_is_system(self):
        messages = build_rag_prompt("query", [make_chunk()])
        assert messages[0]["role"] == "system"

    def test_second_message_is_user(self):
        messages = build_rag_prompt("query", [make_chunk()])
        assert messages[1]["role"] == "user"

    def test_system_prompt_contains_only_rule(self):
        # Anti-hallucination enforcement
        assert "ONLY" in SYSTEM_PROMPT

    def test_system_prompt_contains_fallback_instruction(self):
        assert "don't have enough information" in SYSTEM_PROMPT.lower() or \
               "I don't have enough information" in SYSTEM_PROMPT

    def test_user_message_contains_chunk_text(self):
        chunk = make_chunk(text="The minimum deposit is five hundred dollars.")
        messages = build_rag_prompt("What is the minimum deposit?", [chunk])
        assert "five hundred dollars" in messages[1]["content"]

    def test_user_message_contains_source_filename(self):
        chunk = make_chunk(source_file="terms_and_conditions.pdf")
        messages = build_rag_prompt("query", [chunk])
        assert "terms_and_conditions.pdf" in messages[1]["content"]

    def test_user_message_contains_page_number_when_present(self):
        chunk = make_chunk(page_number=7)
        messages = build_rag_prompt("query", [chunk])
        assert "page 7" in messages[1]["content"]

    def test_user_message_omits_page_when_none(self):
        chunk = make_chunk(page_number=None)
        messages = build_rag_prompt("query", [chunk])
        # Should not include "(page None)" or similar
        assert "page None" not in messages[1]["content"]

    def test_user_message_contains_question(self):
        messages = build_rag_prompt("What are the loan requirements?", [make_chunk()])
        assert "What are the loan requirements?" in messages[1]["content"]

    def test_empty_chunks_produces_no_relevant_documents_message(self):
        messages = build_rag_prompt("any question", [])
        assert "No relevant documents found" in messages[1]["content"]

    def test_multiple_chunks_all_sources_included(self):
        chunks = [
            make_chunk(chunk_id="c1", source_file="doc1.pdf"),
            make_chunk(chunk_id="c2", source_file="doc2.pdf"),
            make_chunk(chunk_id="c3", source_file="doc3.txt"),
        ]
        messages = build_rag_prompt("query", chunks)
        content = messages[1]["content"]
        assert "doc1.pdf" in content
        assert "doc2.pdf" in content
        assert "doc3.txt" in content

    def test_multiple_chunks_numbered_sequentially(self):
        chunks = [make_chunk(chunk_id=f"c{i}") for i in range(3)]
        messages = build_rag_prompt("query", chunks)
        content = messages[1]["content"]
        assert "Source 1:" in content
        assert "Source 2:" in content
        assert "Source 3:" in content


class TestAssessConfidence:
    def test_empty_list_returns_insufficient(self):
        assert assess_confidence([]) == "insufficient"

    def test_high_scores_return_high(self):
        chunks = [make_chunk(score=0.90), make_chunk(score=0.92)]
        assert assess_confidence(chunks) == "high"

    def test_medium_scores_return_medium(self):
        chunks = [make_chunk(score=0.75), make_chunk(score=0.78)]
        assert assess_confidence(chunks) == "medium"

    def test_low_scores_return_low(self):
        chunks = [make_chunk(score=0.65), make_chunk(score=0.60)]
        assert assess_confidence(chunks) == "low"

    def test_single_high_score_chunk(self):
        assert assess_confidence([make_chunk(score=0.95)]) == "high"

    def test_boundary_at_0_85_is_high(self):
        assert assess_confidence([make_chunk(score=0.85)]) == "high"

    def test_boundary_below_0_85_is_medium(self):
        assert assess_confidence([make_chunk(score=0.84)]) == "medium"

    def test_boundary_at_0_70_is_medium(self):
        assert assess_confidence([make_chunk(score=0.70)]) == "medium"

    def test_boundary_below_0_70_is_low(self):
        assert assess_confidence([make_chunk(score=0.69)]) == "low"
