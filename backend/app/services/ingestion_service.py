import uuid
from pathlib import Path

from app.core.config import get_settings
from app.core.logger import get_logger
from app.providers.base_embedding import BaseEmbeddingProvider
from app.rag.chunker import chunk_pages
from app.rag.loaders import DocumentLoaderFactory
from app.rag.vector_store import PineconeVectorStore

logger = get_logger(__name__)


class IngestionService:
    """
    Orchestrates the full document ingestion pipeline:
    Load → Clean → Chunk → Embed → Upsert to Pinecone
    """

    def __init__(
        self,
        embedding: BaseEmbeddingProvider,
        store: PineconeVectorStore,
    ):
        self._embedding = embedding
        self._store = store
        self._settings = get_settings()

    def ingest_file(self, file_path: Path) -> dict:
        """
        Ingest a single document file into the vector store.

        Returns:
            {
                "doc_id": str,
                "file": str,
                "chunks_indexed": int,
                "status": "indexed" | "empty" | "error"
            }
        """
        doc_id = str(uuid.uuid4())
        logger.info(f"Starting ingestion: {file_path.name} (doc_id={doc_id})")

        loader = DocumentLoaderFactory.get_loader(file_path)
        pages = loader.load(file_path)

        chunks = chunk_pages(
            pages,
            doc_id=doc_id,
            chunk_size=self._settings.rag_chunk_size,
            chunk_overlap=self._settings.rag_chunk_overlap,
        )

        if not chunks:
            logger.warning(f"No meaningful chunks extracted from {file_path.name}")
            return {
                "doc_id": doc_id,
                "file": file_path.name,
                "chunks_indexed": 0,
                "status": "empty",
            }

        texts = [c.text for c in chunks]
        vectors = self._embedding.embed_texts(texts)

        count = self._store.upsert_chunks(chunks, vectors)
        logger.info(f"Ingested {count} chunks from {file_path.name}")

        return {
            "doc_id": doc_id,
            "file": file_path.name,
            "chunks_indexed": count,
            "status": "indexed",
        }

    def ingest_directory(self, dir_path: Path) -> list[dict]:
        """Ingest all supported files in a directory."""
        supported = DocumentLoaderFactory.supported_extensions()
        results = []
        for file in sorted(dir_path.iterdir()):
            if file.suffix.lower() in supported:
                try:
                    result = self.ingest_file(file)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to ingest {file.name}: {e}")
                    results.append({
                        "doc_id": "",
                        "file": file.name,
                        "chunks_indexed": 0,
                        "status": "error",
                    })
        return results
