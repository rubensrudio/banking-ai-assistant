from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.domain.models import DocumentChunk
from app.rag.cleaner import clean_text, is_meaningful


def chunk_pages(
    pages: list[dict],
    doc_id: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    """
    Convert a list of page dicts into DocumentChunks using LangChain's
    RecursiveCharacterTextSplitter, which splits on paragraph/sentence/word
    boundaries where possible instead of a fixed character offset.

    Args:
        pages: List of {"text": str, "page": int | None, "source": str}
        doc_id: Unique identifier for the parent document
        chunk_size: Target character size per chunk
        chunk_overlap: Character overlap between consecutive chunks

    Returns:
        Flat list of DocumentChunk objects, filtered for meaningful content
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

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

        for chunk_text in splitter.split_text(text):
            chunk_text = chunk_text.strip()

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

    return chunks
