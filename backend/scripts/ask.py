"""
CLI smoke test for the end-to-end RAG pipeline.

Requirements:
  - .env file with PINECONE_API_KEY and LMSTUDIO_CHAT_MODEL
  - LM Studio running on port 1234 with a model loaded
  - At least one document already ingested via scripts/ingest.py

Usage:
    python scripts/ask.py "What is the interest rate for savings accounts?"
    python scripts/ask.py --stream "What are the loan terms?"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logger import setup_logging
from app.providers.lmstudio_provider import get_llm_provider
from app.providers.sentence_transformer_embedding import get_embedding_provider
from app.rag.vector_store import get_vector_store
from app.services.rag_service import RAGService


def main() -> None:
    setup_logging("INFO")

    parser = argparse.ArgumentParser(description="Ask the banking AI assistant")
    parser.add_argument("query", nargs="+", help="Question to ask")
    parser.add_argument("--stream", action="store_true", help="Stream the response")
    args = parser.parse_args()

    query = " ".join(args.query)

    service = RAGService(
        embedding=get_embedding_provider(),
        store=get_vector_store(),
        llm=get_llm_provider(),
    )

    if args.stream:
        print("\nAnswer (streaming):\n")
        for token in service.ask_stream(query):
            print(token, end="", flush=True)
        print("\n")
    else:
        response = service.ask(query)
        print(f"\nAnswer:\n{response.answer}")
        print(f"\nConfidence: {response.confidence}")
        if response.sources:
            print("\nSources:")
            for src in response.sources:
                page = f" p.{src.page_number}" if src.page_number else ""
                print(f"  - {src.source_file}{page} (score: {src.score:.3f})")
        else:
            print("\nSources: none (no relevant documents found)")


if __name__ == "__main__":
    main()
