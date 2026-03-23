import re
import unicodedata


def clean_text(text: str, strip_headers: list[str] | None = None) -> str:
    """
    Normalize and clean raw text extracted from documents.
    Handles common artifacts from PDF/DOCX extraction.

    Args:
        text: Raw text to clean.
        strip_headers: Optional list of repeated header/footer strings to remove
                       (e.g. PDF page headers). Matching is case-insensitive.
    """
    if not text:
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFC", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable control characters (keep \n and \t)
    text = re.sub(r"[^\S\n\t]+", " ", text)  # collapse horizontal whitespace
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Remove repeated page headers/footers if provided
    if strip_headers:
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if any(stripped.lower() == h.lower() for h in strip_headers):
                continue
            cleaned_lines.append(line)
        text = "\n".join(cleaned_lines)

    # Collapse 3+ consecutive newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


def is_meaningful(text: str, min_chars: int = 50) -> bool:
    """
    Return True if the text contains enough meaningful content to be indexed.
    Filters out page numbers, headers, and table-of-contents artifacts.
    """
    stripped = text.strip()

    if len(stripped) < min_chars:
        return False

    # Mostly digits/punctuation (page numbers, TOC dotted lines, etc.)
    alpha_count = sum(1 for c in stripped if c.isalpha())
    if alpha_count < len(stripped) * 0.3:
        return False

    return True
