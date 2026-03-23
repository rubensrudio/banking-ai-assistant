"""
CLI script to ingest banking documents into Pinecone.

Usage:
    python scripts/ingest.py --path docs/sample.pdf
    python scripts/ingest.py --dir docs/
"""
import argparse
import json
import sys
from pathlib import Path

# Ensure the backend root is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logger import setup_logging
from app.providers.sentence_transformer_embedding import get_embedding_provider
from app.rag.vector_store import get_vector_store
from app.services.ingestion_service import IngestionService


def main() -> None:
    setup_logging("INFO")

    parser = argparse.ArgumentParser(description="Ingest banking documents into Pinecone")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", type=Path, help="Single file to ingest")
    group.add_argument("--dir", type=Path, help="Directory of files to ingest")
    args = parser.parse_args()

    service = IngestionService(
        embedding=get_embedding_provider(),
        store=get_vector_store(),
    )

    if args.path:
        result = service.ingest_file(args.path)
        print(json.dumps(result, indent=2))
    elif args.dir:
        results = service.ingest_directory(args.dir)
        for r in results:
            print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
