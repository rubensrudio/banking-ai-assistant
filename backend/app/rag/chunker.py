from app.domain.models import DocumentChunk
from app.rag.cleaner import clean_text, is_meaningful


def chunk_pages(
    pages: list[dict],
    doc_id: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    """
    Convert a list of page dicts into DocumentChunks using a sliding window.

    Args:
        pages: List of {"text": str, "page": int | None, "source": str}
        doc_id: Unique identifier for the parent document
        chunk_size: Target character size per chunk
        chunk_overlap: Character overlap between consecutive chunks

    Returns:
        Flat list of DocumentChunk objects, filtered for meaningful content
    """
    chunks: list[DocumentChunk] = []
    global_index = 0

    for page_dict in pages:
        raw_text = page_dict.get("text", "")
        page_number = page_dict.get("page")
        source_file = page_dict.get("source", "unknown")

        strip_headers = page_dict.get("_strip_headers")
        text = clean_text(raw_text, strip_headers=strip_headers)
        if not text:
            continue

        # Sliding window chunking
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if is_meaningful(chunk_text):
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc_id}-{global_index}",
                        doc_id=doc_id,
                        text=chunk_text,
                        source_file=source_file,
                        page_number=page_number,
                        chunk_index=global_index,
                    )
                )
                global_index += 1

            # Move forward by (chunk_size - overlap), minimum 1 to avoid infinite loop
            step = max(chunk_size - chunk_overlap, 1)
            start += step

    return chunks
