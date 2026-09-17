"""
Chunker tests — LangChain RecursiveCharacterTextSplitter integration.
No external services required.
"""
from app.rag.chunker import chunk_pages


def make_page(text: str, page: int | None = 1, source: str = "doc.pdf") -> dict:
    return {"text": text, "page": page, "source": source}


class TestChunkPages:
    def test_returns_chunks_for_short_text(self):
        text = "The savings account offers a 4.5% APY, compounded monthly on the full balance."
        chunks = chunk_pages([make_page(text)], doc_id="doc")
        assert len(chunks) == 1
        assert chunks[0].text == text

    def test_splits_long_text_into_multiple_chunks(self):
        long_text = "This is a sentence about banking terms. " * 100
        chunks = chunk_pages(
            [make_page(long_text)], doc_id="doc", chunk_size=200, chunk_overlap=20
        )
        assert len(chunks) > 1

    def test_chunk_ids_are_sequential_per_document(self):
        long_text = "This is a sentence about banking terms. " * 100
        chunks = chunk_pages(
            [make_page(long_text)], doc_id="doc42", chunk_size=200, chunk_overlap=20
        )
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_id == f"doc42-{i}"
            assert chunk.chunk_index == i

    def test_chunks_respect_source_and_page(self):
        text = "Loan terms and conditions apply to all fixed-rate mortgage products offered."
        chunks = chunk_pages(
            [make_page(text, page=3, source="terms.pdf")],
            doc_id="doc",
        )
        assert chunks[0].source_file == "terms.pdf"
        assert chunks[0].page_number == 3

    def test_empty_page_text_produces_no_chunks(self):
        chunks = chunk_pages([make_page("")], doc_id="doc")
        assert chunks == []

    def test_multiple_pages_are_concatenated_into_flat_list(self):
        pages = [
            make_page("First page content about checking and savings accounts.", page=1),
            make_page("Second page content about personal and mortgage loans.", page=2),
        ]
        chunks = chunk_pages(pages, doc_id="doc")
        assert len(chunks) == 2
        assert chunks[0].page_number == 1
        assert chunks[1].page_number == 2

    def test_overlap_produces_repeated_content_across_chunks(self):
        long_text = "Sentence number %d about banking. " * 1
        text = "".join(f"Sentence number {i} about banking regulations and terms. " for i in range(60))
        chunks = chunk_pages([make_page(text)], doc_id="doc", chunk_size=200, chunk_overlap=50)
        assert len(chunks) > 1
