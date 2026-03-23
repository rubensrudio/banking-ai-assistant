"""
Sprint 1 Tests — Document loaders, cleaner, and chunker.
No external services required.
"""
import pytest
from pathlib import Path

from app.rag.cleaner import clean_text, is_meaningful
from app.rag.loaders import DocumentLoaderFactory, TXTLoader, DOCXLoader
from app.rag.chunker import chunk_pages
from app.domain.models import DocumentChunk


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_txt(tmp_path: Path) -> Path:
    content = (
        "Banking Products Overview\n\n"
        "Our savings account offers a competitive interest rate of 4.5% per annum. "
        "Customers can open an account with a minimum deposit of $500. "
        "There are no monthly maintenance fees for balances above $1,000.\n\n"
        "Loan products include personal loans, home equity lines, and auto financing. "
        "Rates vary based on credit score and loan term."
    )
    p = tmp_path / "sample.txt"
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture
def sample_docx(tmp_path: Path) -> Path:
    import docx

    doc = docx.Document()
    doc.add_heading("Checking Account Terms", level=1)
    doc.add_paragraph(
        "The standard checking account provides unlimited transactions. "
        "Overdraft protection is available for an annual fee of $25. "
        "Interest is calculated on the daily average balance."
    )
    doc.add_paragraph(
        "Minimum opening deposit is $100. No monthly fee if balance stays above $500."
    )
    path = tmp_path / "sample.docx"
    doc.save(str(path))
    return path


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    from pypdf import PdfWriter

    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)

    # pypdf does not support drawing text easily without reportlab;
    # use add_annotation workaround or just test with a real minimal PDF bytes.
    # We'll write a minimal valid PDF manually for testing.
    path = tmp_path / "sample.pdf"

    # Create a minimal valid PDF with one page and simple content stream
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj

4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 72 720 Td (Banking FAQ) Tj ET
endstream
endobj

5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000266 00000 n
0000000360 00000 n

trailer
<< /Size 6 /Root 1 0 R >>
startxref
441
%%EOF"""
    path.write_bytes(pdf_content)
    return path


# ---------------------------------------------------------------------------
# clean_text tests
# ---------------------------------------------------------------------------


class TestCleanText:
    def test_empty_string(self):
        assert clean_text("") == ""

    def test_strips_leading_trailing_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_normalizes_line_endings(self):
        result = clean_text("line1\r\nline2\rline3")
        assert "\r" not in result
        assert "line1" in result
        assert "line2" in result

    def test_collapses_multiple_blank_lines(self):
        result = clean_text("a\n\n\n\n\nb")
        assert "\n\n\n" not in result

    def test_removes_control_characters(self):
        result = clean_text("hello\x00world\x07")
        assert "\x00" not in result
        assert "\x07" not in result

    def test_preserves_newlines_and_content(self):
        text = "Paragraph one.\n\nParagraph two."
        result = clean_text(text)
        assert "Paragraph one." in result
        assert "Paragraph two." in result


class TestIsMeaningful:
    def test_short_text_is_not_meaningful(self):
        assert is_meaningful("Hi") is False

    def test_mostly_digits_is_not_meaningful(self):
        assert is_meaningful("1234567890 . . . . . . . . . . . 42") is False

    def test_normal_sentence_is_meaningful(self):
        text = "The savings account offers competitive interest rates for all customers."
        assert is_meaningful(text) is True

    def test_below_min_chars_threshold(self):
        assert is_meaningful("Short text", min_chars=50) is False

    def test_meets_min_chars_threshold(self):
        text = "a" * 51
        assert is_meaningful(text, min_chars=50) is True


# ---------------------------------------------------------------------------
# DocumentLoaderFactory tests
# ---------------------------------------------------------------------------


class TestDocumentLoaderFactory:
    def test_unsupported_extension_raises(self, tmp_path):
        fake = tmp_path / "file.xlsx"
        fake.write_text("data")
        with pytest.raises(ValueError, match="Unsupported file type"):
            DocumentLoaderFactory.get_loader(fake)

    def test_txt_extension_returns_txt_loader(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("content")
        loader = DocumentLoaderFactory.get_loader(f)
        assert isinstance(loader, TXTLoader)

    def test_supported_extensions_includes_pdf_docx_txt(self):
        exts = DocumentLoaderFactory.supported_extensions()
        assert ".pdf" in exts
        assert ".docx" in exts
        assert ".txt" in exts


# ---------------------------------------------------------------------------
# TXTLoader tests
# ---------------------------------------------------------------------------


class TestTXTLoader:
    def test_load_returns_list_of_dicts(self, sample_txt):
        loader = TXTLoader()
        pages = loader.load(sample_txt)
        assert isinstance(pages, list)
        assert len(pages) == 1

    def test_load_returns_correct_structure(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        assert "text" in pages[0]
        assert "page" in pages[0]
        assert "source" in pages[0]

    def test_load_page_number_is_none(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        assert pages[0]["page"] is None

    def test_load_source_is_filename(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        assert pages[0]["source"] == "sample.txt"

    def test_load_text_contains_content(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        assert "savings account" in pages[0]["text"]


# ---------------------------------------------------------------------------
# DOCXLoader tests
# ---------------------------------------------------------------------------


class TestDOCXLoader:
    def test_load_returns_list(self, sample_docx):
        pages = DOCXLoader().load(sample_docx)
        assert isinstance(pages, list)
        assert len(pages) == 1

    def test_load_text_is_string(self, sample_docx):
        pages = DOCXLoader().load(sample_docx)
        assert isinstance(pages[0]["text"], str)
        assert len(pages[0]["text"]) > 0

    def test_load_source_is_filename(self, sample_docx):
        pages = DOCXLoader().load(sample_docx)
        assert pages[0]["source"] == "sample.docx"


# ---------------------------------------------------------------------------
# Chunker tests
# ---------------------------------------------------------------------------


class TestChunkPages:
    def test_returns_list_of_document_chunks(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        chunks = chunk_pages(pages, doc_id="test-001")
        assert isinstance(chunks, list)
        assert all(isinstance(c, DocumentChunk) for c in chunks)

    def test_chunk_ids_are_unique(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        chunks = chunk_pages(pages, doc_id="test-001")
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_ids_include_doc_id(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        chunks = chunk_pages(pages, doc_id="my-doc")
        for chunk in chunks:
            assert chunk.chunk_id.startswith("my-doc-")

    def test_doc_id_propagated_to_chunks(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        chunks = chunk_pages(pages, doc_id="abc-123")
        for chunk in chunks:
            assert chunk.doc_id == "abc-123"

    def test_source_file_propagated(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        chunks = chunk_pages(pages, doc_id="test-001")
        for chunk in chunks:
            assert chunk.source_file == "sample.txt"

    def test_empty_pages_returns_empty_list(self):
        chunks = chunk_pages([], doc_id="empty")
        assert chunks == []

    def test_chunk_size_respected(self, sample_txt):
        pages = TXTLoader().load(sample_txt)
        chunks = chunk_pages(pages, doc_id="test", chunk_size=100, chunk_overlap=0)
        for chunk in chunks:
            assert len(chunk.text) <= 100

    def test_meaningful_filter_applied(self):
        # Pages with only noise should produce no chunks
        pages = [{"text": "1 . . . 2 . . .", "page": 1, "source": "noise.txt"}]
        chunks = chunk_pages(pages, doc_id="test")
        assert len(chunks) == 0
