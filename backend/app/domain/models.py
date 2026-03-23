from dataclasses import dataclass, field
from enum import Enum


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


@dataclass
class DocumentChunk:
    """A single chunk of text extracted from a document."""

    chunk_id: str  # "{doc_id}-{chunk_index}"
    doc_id: str
    text: str
    source_file: str
    page_number: int | None
    chunk_index: int
    metadata: dict = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    """A chunk returned by semantic search with its relevance score."""

    chunk_id: str
    doc_id: str
    text: str
    source_file: str
    page_number: int | None
    score: float


@dataclass
class RAGResponse:
    """Full response from the RAG pipeline."""

    answer: str
    sources: list[RetrievedChunk]
    context_used: str
    confidence: str  # "high" | "medium" | "low" | "insufficient"
