# Banking AI Assistant

A Retrieval-Augmented Generation (RAG) backend for a banking domain AI assistant. It ingests banking documents (PDF, DOCX, TXT), chunks and embeds them locally, stores the vectors in Pinecone, and answers user questions by retrieving relevant context and generating grounded responses through an OpenAI-compatible LLM (e.g., LM Studio running locally).

## Overview

The project is structured as a FastAPI backend organized around a classic RAG pipeline:

- **Loaders** — extract raw text from PDF, DOCX, and TXT documents.
- **Cleaner & Chunker** — normalize and split documents into overlapping chunks suitable for embedding.
- **Embedding Provider** — generates vector embeddings locally using `sentence-transformers` (no external API key required).
- **Vector Store** — persists and queries embeddings using Pinecone.
- **LLM Provider** — generates answers using an OpenAI-compatible chat completion API (configured by default for a local LM Studio server).
- **RAG Service** — orchestrates retrieval + prompt building + generation to answer user questions.
- **Ingestion Service** — orchestrates the document ingestion pipeline (load → clean → chunk → embed → store).

This is currently **Phase 1** of the project (backend/RAG core). Frontend (Angular) is planned for Phase 3.

## Tech Stack & Libraries

| Category | Library |
|---|---|
| Web framework | FastAPI, Uvicorn |
| Configuration & validation | Pydantic, pydantic-settings, python-dotenv |
| Document parsing | pypdf, python-docx |
| Embeddings | sentence-transformers, torch |
| Vector database | Pinecone |
| Orchestration | LangChain (langchain, langchain-community, langchain-core) |
| LLM client | openai (OpenAI-compatible client, used with LM Studio) |
| HTTP client | httpx |
| Logging | python-json-logger |
| Testing | pytest, pytest-cov, pytest-asyncio |
| Dev tooling | black, isort |

## Prerequisites

- Python 3.11+
- A Pinecone account and API key ([pinecone.io](https://www.pinecone.io/))
- [LM Studio](https://lmstudio.ai/) running locally with a chat model loaded (or any other OpenAI-compatible endpoint)

## Project Structure

```
backend/
├── app/
│   ├── api/routes/        # FastAPI routes
│   ├── core/               # Configuration and logging
│   ├── domain/              # Domain models
│   ├── providers/           # Embedding and LLM provider implementations
│   ├── rag/                 # Loaders, cleaner, chunker, prompt builder, vector store
│   └── services/            # Ingestion and RAG orchestration services
├── scripts/                # CLI scripts (ingest, ask, generate sample docs)
├── tests/                  # Unit and integration tests
├── requirements.txt
├── Makefile
└── .env.example
```

## Setup

1. **Clone the repository and move into the backend folder**

   ```bash
   cd banking-ai-assistant/backend
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   make install
   # or: pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in:
   - `PINECONE_API_KEY` — your Pinecone API key
   - `PINECONE_INDEX_NAME` / `PINECONE_ENVIRONMENT` — your Pinecone index settings
   - `LMSTUDIO_BASE_URL` / `LMSTUDIO_CHAT_MODEL` — your local LM Studio endpoint and model name

5. **Start LM Studio** (or another OpenAI-compatible server) and load the chat model referenced in `LMSTUDIO_CHAT_MODEL`.

## Running the Application

Start the API server:

```bash
make run
```

The API will be available at `http://localhost:8000` (interactive docs at `http://localhost:8000/docs`).

## Ingesting Documents

Place your banking documents (PDF, DOCX, TXT) inside a directory, then run:

```bash
make ingest DIR=docs/
```

This loads, cleans, chunks, embeds, and stores the documents in the configured Pinecone index.

To generate sample documents for testing:

```bash
PYTHONPATH=. python scripts/generate_sample_docs.py
```

## Asking Questions

Query the assistant directly from the CLI:

```bash
make ask Q="What is the savings account interest rate?"
```

Or call the API endpoint directly once the server is running (see `/docs` for the exact route and payload).

## Running Tests

Run the unit test suite (excludes integration tests that require live external services):

```bash
make test
```

Run tests with coverage report:

```bash
make test-cov
```

Run the full suite, including integration tests (requires a configured Pinecone index and a running LM Studio instance):

```bash
make test-integration
```

## Linting & Formatting

```bash
make lint      # check formatting with black and isort
make format    # auto-format code
```

## Docker

Build and run the backend in a container:

```bash
make docker-build
make docker-run
```

## Configuration Reference

Key environment variables (see `backend/.env.example` for the full list):

| Variable | Description |
|---|---|
| `ENVIRONMENT` | `development` / `production` |
| `LOG_LEVEL` | Logging verbosity |
| `API_HOST` / `API_PORT` | API bind address and port |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_INDEX_NAME` | Pinecone index name |
| `PINECONE_ENVIRONMENT` | Pinecone environment/region |
| `EMBEDDING_MODEL` | Local sentence-transformers model used for embeddings |
| `EMBEDDING_DIMENSION` | Embedding vector dimension |
| `LMSTUDIO_BASE_URL` | OpenAI-compatible LLM endpoint |
| `LMSTUDIO_CHAT_MODEL` | Chat model name served by LM Studio |
| `RAG_TOP_K` | Number of chunks retrieved per query |
| `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` | Chunking parameters |
| `RAG_MIN_SCORE` | Minimum similarity score for retrieved chunks |

## Roadmap

- **Phase 1** — RAG backend core (current)
- **Phase 3** — Angular frontend
