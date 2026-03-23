import time
from functools import lru_cache

from app.core.config import get_settings
from app.core.logger import get_logger
from app.domain.models import DocumentChunk, RetrievedChunk

logger = get_logger(__name__)

# Pinecone batch size limit
_UPSERT_BATCH_SIZE = 100


class PineconeVectorStore:
    """
    Pinecone vector store for banking document chunks.
    Uses cosine similarity. Index is created automatically on first use.
    """

    def __init__(self):
        from pinecone import Pinecone, ServerlessSpec

        settings = get_settings()
        self._pc = Pinecone(api_key=settings.pinecone_api_key)
        self._index_name = settings.pinecone_index_name
        self._dim = settings.embedding_dimension
        self._min_score = settings.rag_min_score
        self._ensure_index(ServerlessSpec)

    def _ensure_index(self, ServerlessSpec) -> None:
        existing = [idx.name for idx in self._pc.list_indexes()]
        if self._index_name not in existing:
            logger.info(f"Creating Pinecone index '{self._index_name}' (dim={self._dim})")
            self._pc.create_index(
                name=self._index_name,
                dimension=self._dim,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            # Wait until ready
            for _ in range(30):
                status = self._pc.describe_index(self._index_name).status
                if status.get("ready"):
                    break
                time.sleep(2)
            logger.info(f"Index '{self._index_name}' is ready")
        else:
            logger.debug(f"Index '{self._index_name}' already exists")

        self._index = self._pc.Index(self._index_name)

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        vectors: list[list[float]],
    ) -> int:
        """
        Upsert document chunks with their embeddings.
        Returns the number of vectors upserted.
        """
        if not chunks:
            return 0

        records = []
        for chunk, vector in zip(chunks, vectors):
            records.append(
                {
                    "id": chunk.chunk_id,
                    "values": vector,
                    "metadata": {
                        "doc_id": chunk.doc_id,
                        "source_file": chunk.source_file,
                        "page_number": chunk.page_number if chunk.page_number is not None else -1,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text[:1000],  # Pinecone metadata limit
                    },
                }
            )

        # Batch upserts
        upserted = 0
        for i in range(0, len(records), _UPSERT_BATCH_SIZE):
            batch = records[i : i + _UPSERT_BATCH_SIZE]
            self._index.upsert(vectors=batch)
            upserted += len(batch)
            logger.debug(f"Upserted batch {i // _UPSERT_BATCH_SIZE + 1}: {len(batch)} vectors")

        return upserted

    def search(
        self,
        query_vector: list[float],
        top_k: int,
        filter_doc_id: str | None = None,
    ) -> list[RetrievedChunk]:
        """
        Semantic search. Returns chunks with score >= min_score, sorted by score desc.
        """
        query_filter = None
        if filter_doc_id:
            query_filter = {"doc_id": {"$eq": filter_doc_id}}

        result = self._index.query(
            vector=query_vector,
            top_k=top_k,
            filter=query_filter,
            include_metadata=True,
        )

        chunks = []
        for match in result.matches:
            if match.score < self._min_score:
                continue
            meta = match.metadata or {}
            page = meta.get("page_number")
            chunks.append(
                RetrievedChunk(
                    chunk_id=match.id,
                    doc_id=meta.get("doc_id", ""),
                    text=meta.get("text", ""),
                    source_file=meta.get("source_file", ""),
                    page_number=None if page == -1 else page,
                    score=match.score,
                )
            )

        return sorted(chunks, key=lambda c: c.score, reverse=True)

    def delete_document(self, doc_id: str) -> None:
        """Remove all chunks belonging to a document."""
        self._index.delete(filter={"doc_id": {"$eq": doc_id}})
        logger.info(f"Deleted all chunks for doc_id={doc_id}")


@lru_cache(maxsize=1)
def get_vector_store() -> PineconeVectorStore:
    """Singleton vector store. Pinecone client initialized once."""
    return PineconeVectorStore()
