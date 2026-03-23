"""
Sprint 2 Tests — IngestionService (unit tests, no external services required).
Pinecone and embedding model are mocked.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.services.ingestion_service import IngestionService
from app.domain.models import DocumentChunk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_mock_embedding(dimension: int = 384):
    """Return a mock embedding provider that returns zero-vectors."""
    mock = MagicMock()
    mock.dimension = dimension
    mock.embed_texts.side_effect = lambda texts: [[0.0] * dimension for _ in texts]
    mock.embed_query.side_effect = lambda text: [0.0] * dimension
    return mock


def make_mock_store():
    """Return a mock vector store that records calls."""
    mock = MagicMock()
    mock.upsert_chunks.side_effect = lambda chunks, vectors: len(chunks)
    return mock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def txt_file(tmp_path: Path) -> Path:
    content = (
        "Savings Account — Terms and Conditions\n\n"
        "Our premier savings account offers 4.5% APY with no monthly fees. "
        "Minimum opening deposit of $500 required. Interest is compounded daily "
        "and credited monthly. Early withdrawal penalty of 90 days interest applies "
        "to promotional rate accounts. Online banking and mobile app access included "
        "at no extra charge for all account holders.\n\n"
        "Personal Loan Products\n\n"
        "Fixed-rate personal loans available from $1,000 to $50,000. "
        "Rates from 6.99% APR for qualified borrowers. Terms of 12 to 60 months. "
        "No prepayment penalty. Same-day funding available for approved applications "
        "submitted before 2 PM on business days."
    )
    p = tmp_path / "banking_products.txt"
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture
def empty_txt(tmp_path: Path) -> Path:
    p = tmp_path / "empty.txt"
    p.write_text("  \n  \n  ", encoding="utf-8")
    return p


@pytest.fixture
def service(tmp_path):
    return IngestionService(
        embedding=make_mock_embedding(),
        store=make_mock_store(),
    )


# ---------------------------------------------------------------------------
# IngestionService.ingest_file tests
# ---------------------------------------------------------------------------


class TestIngestFile:
    def test_returns_indexed_status_for_valid_file(self, service, txt_file):
        result = service.ingest_file(txt_file)
        assert result["status"] == "indexed"

    def test_returns_correct_filename(self, service, txt_file):
        result = service.ingest_file(txt_file)
        assert result["file"] == "banking_products.txt"

    def test_returns_nonzero_chunks_for_valid_file(self, service, txt_file):
        result = service.ingest_file(txt_file)
        assert result["chunks_indexed"] > 0

    def test_returns_doc_id_string(self, service, txt_file):
        result = service.ingest_file(txt_file)
        assert isinstance(result["doc_id"], str)
        assert len(result["doc_id"]) > 0

    def test_each_call_generates_unique_doc_id(self, service, txt_file):
        r1 = service.ingest_file(txt_file)
        r2 = service.ingest_file(txt_file)
        assert r1["doc_id"] != r2["doc_id"]

    def test_empty_file_returns_empty_status(self, service, empty_txt):
        result = service.ingest_file(empty_txt)
        assert result["status"] == "empty"
        assert result["chunks_indexed"] == 0

    def test_embed_texts_called_once(self, txt_file):
        mock_embedding = make_mock_embedding()
        mock_store = make_mock_store()
        svc = IngestionService(embedding=mock_embedding, store=mock_store)

        svc.ingest_file(txt_file)

        mock_embedding.embed_texts.assert_called_once()

    def test_embed_texts_called_with_chunk_texts(self, txt_file):
        mock_embedding = make_mock_embedding()
        mock_store = make_mock_store()
        svc = IngestionService(embedding=mock_embedding, store=mock_store)

        svc.ingest_file(txt_file)

        call_args = mock_embedding.embed_texts.call_args[0][0]
        assert isinstance(call_args, list)
        assert all(isinstance(t, str) for t in call_args)

    def test_upsert_chunks_called_once(self, txt_file):
        mock_embedding = make_mock_embedding()
        mock_store = make_mock_store()
        svc = IngestionService(embedding=mock_embedding, store=mock_store)

        svc.ingest_file(txt_file)

        mock_store.upsert_chunks.assert_called_once()

    def test_upsert_chunks_receives_matching_counts(self, txt_file):
        mock_embedding = make_mock_embedding()
        mock_store = make_mock_store()
        svc = IngestionService(embedding=mock_embedding, store=mock_store)

        svc.ingest_file(txt_file)

        chunks_arg, vectors_arg = mock_store.upsert_chunks.call_args[0]
        assert len(chunks_arg) == len(vectors_arg)

    def test_upsert_not_called_for_empty_file(self, empty_txt):
        mock_embedding = make_mock_embedding()
        mock_store = make_mock_store()
        svc = IngestionService(embedding=mock_embedding, store=mock_store)

        svc.ingest_file(empty_txt)

        mock_store.upsert_chunks.assert_not_called()

    def test_unsupported_file_type_raises(self, tmp_path):
        unsupported = tmp_path / "report.xlsx"
        unsupported.write_text("data")
        svc = IngestionService(
            embedding=make_mock_embedding(),
            store=make_mock_store(),
        )
        with pytest.raises(ValueError, match="Unsupported file type"):
            svc.ingest_file(unsupported)


# ---------------------------------------------------------------------------
# IngestionService.ingest_directory tests
# ---------------------------------------------------------------------------


class TestIngestDirectory:
    def test_ingest_directory_processes_txt_files(self, tmp_path):
        for i in range(3):
            f = tmp_path / f"doc{i}.txt"
            f.write_text(
                f"Banking product number {i}. " * 20,
                encoding="utf-8",
            )

        svc = IngestionService(
            embedding=make_mock_embedding(),
            store=make_mock_store(),
        )
        results = svc.ingest_directory(tmp_path)
        assert len(results) == 3
        assert all(r["status"] == "indexed" for r in results)

    def test_ingest_directory_skips_unsupported_files(self, tmp_path):
        (tmp_path / "report.xlsx").write_text("data")
        (tmp_path / "notes.csv").write_text("col1,col2")
        txt = tmp_path / "valid.txt"
        txt.write_text("Valid banking content " * 10, encoding="utf-8")

        svc = IngestionService(
            embedding=make_mock_embedding(),
            store=make_mock_store(),
        )
        results = svc.ingest_directory(tmp_path)
        assert len(results) == 1
        assert results[0]["file"] == "valid.txt"
