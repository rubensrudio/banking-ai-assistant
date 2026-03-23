# Phase 1 Progress — Local RAG Engine

## Overview
Goal: Build a working local RAG pipeline: **Question → Retrieve Context → Generate Answer**

## Sprint 1 — Project Scaffold + Document Loaders
**Status: ✅ COMPLETED**
**Date: 2026-03-23**

### Files Created
- [x] `backend/requirements.txt` — All dependencies pinned
- [x] `backend/.env.example` — Environment variable template
- [x] `backend/app/core/config.py` — Pydantic Settings with @lru_cache singleton
- [x] `backend/app/core/logger.py` — JSON + console dual logging
- [x] `backend/app/domain/models.py` — DocumentChunk, RetrievedChunk, RAGResponse
- [x] `backend/app/rag/cleaner.py` — Text normalization + meaningful-content filter
- [x] `backend/app/rag/loaders.py` — PDFLoader, DOCXLoader, TXTLoader + Factory
- [x] `backend/app/rag/chunker.py` — Sliding window chunker → DocumentChunk list
- [x] `backend/tests/test_loaders.py` — Full test suite (no external deps)
- [x] `backend/pytest.ini` — pytest config with integration marker
- [x] `backend/Makefile` — Dev commands: install, run, test, lint, format, ingest, ask

### Local Test Command
```bash
cd banking-ai-assistant/backend
pip install -r requirements.txt
pytest tests/test_loaders.py -v
```

### Expected Output
All tests green. No network calls, no API keys needed.

---

## Sprint 2 — Embeddings + Pinecone
**Status: ✅ COMPLETED**
**Date: 2026-03-23**

### Files Created
- [x] `backend/app/providers/base_embedding.py` — Abstract embedding interface
- [x] `backend/app/providers/sentence_transformer_embedding.py` — Local embeddings (all-MiniLM-L6-v2, 384 dims)
- [x] `backend/app/rag/vector_store.py` — PineconeVectorStore (upsert, search, delete)
- [x] `backend/app/services/ingestion_service.py` — Full pipeline: Load→Clean→Chunk→Embed→Upsert
- [x] `backend/scripts/ingest.py` — CLI script for document ingestion
- [x] `backend/tests/test_ingestion.py` — 14 unit tests (mocked Pinecone/embedding)

### Local Test Command (no Pinecone needed)
```bash
pytest tests/test_ingestion.py -v
```

### Manual CLI Test (requires .env with PINECONE_API_KEY)
```bash
python scripts/ingest.py --path docs/sample.txt
# Output: {"doc_id": "...", "chunks_indexed": 5, "status": "indexed"}
```

### Plan
- [ ] `backend/app/providers/base_embedding.py` — Abstract embedding interface
- [ ] `backend/app/providers/sentence_transformer_embedding.py` — Local embeddings (all-MiniLM-L6-v2)
- [ ] `backend/app/rag/vector_store.py` — PineconeVectorStore (upsert, search, delete)
- [ ] `backend/app/services/ingestion_service.py` — Full pipeline: Load→Clean→Chunk→Embed→Upsert
- [ ] `backend/scripts/ingest.py` — CLI script for document ingestion
- [ ] `backend/tests/test_ingestion.py` — Unit tests (mocked Pinecone)
- [ ] `backend/tests/test_vector_store.py` — Integration tests (requires Pinecone key)

### Prerequisites
- Pinecone account (free Starter tier works)
- `PINECONE_API_KEY` in `.env`

### Local Test Command
```bash
# Unit tests (no Pinecone needed)
pytest tests/test_ingestion.py -v

# Integration (requires PINECONE_API_KEY)
pytest tests/ -v -m integration

# Manual CLI ingestion
python scripts/ingest.py --path docs/sample.txt
```

---

## Sprint 3 — Retrieval + LM Studio
**Status: ✅ COMPLETED**
**Date: 2026-03-23**

### Files Created
- [x] `backend/app/providers/base_llm.py` — Abstract LLM interface (complete + stream)
- [x] `backend/app/providers/lmstudio_provider.py` — LM Studio via OpenAI-compatible API
- [x] `backend/app/rag/prompt_builder.py` — Anti-hallucination prompt + confidence scoring
- [x] `backend/app/services/rag_service.py` — RAG orchestration (embed → retrieve → generate)
- [x] `backend/scripts/ask.py` — CLI smoke test for end-to-end RAG
- [x] `backend/tests/test_prompt_builder.py` — 17 tests
- [x] `backend/tests/test_rag_service.py` — 18 tests

### Local Test Command (no LM Studio / Pinecone needed)
```bash
pytest tests/ -v -m "not integration"
# 81/81 passing
```

### End-to-End CLI Test (requires LM Studio + Pinecone)
```bash
# 1. Load a model in LM Studio and start the server (port 1234)
# 2. Set LMSTUDIO_CHAT_MODEL in .env to the model name
# 3. Ingest a document
python scripts/ingest.py --path docs/sample.txt
# 4. Ask a question
python scripts/ask.py "What is the interest rate for savings accounts?"
python scripts/ask.py --stream "What are the loan terms?"
```

### Plan
- [ ] `backend/app/providers/base_llm.py` — Abstract LLM interface
- [ ] `backend/app/providers/lmstudio_provider.py` — LM Studio (OpenAI-compatible API)
- [ ] `backend/app/rag/prompt_builder.py` — Anti-hallucination prompt construction
- [ ] `backend/app/services/rag_service.py` — RAG orchestration (embed → retrieve → generate)
- [ ] `backend/scripts/ask.py` — CLI smoke test for end-to-end RAG
- [ ] `backend/tests/test_prompt_builder.py`
- [ ] `backend/tests/test_rag_service.py`

### Prerequisites
- Sprint 2 completed
- LM Studio installed and running on port 1234
- A model loaded in LM Studio (e.g., Llama 3.1 8B Instruct)

### Local Test Command
```bash
# Unit tests (no LM Studio needed)
pytest tests/ -v -m "not integration"

# End-to-end CLI (requires LM Studio + Pinecone)
python scripts/ask.py "What are the requirements for a savings account?"
```

---

## Phase 1 Completion Checklist
- [x] Sprint 1 tests pass — 30/30 ✅
- [x] Sprint 2 tests pass — 14/14 ✅
- [x] Sprint 3 tests pass — 37/37 ✅
- [x] Total: **81/81 tests passing** ✅
- [ ] End-to-end CLI works (ingest a PDF → ask a question → get a sourced answer)
  - Requires: Pinecone API key + LM Studio running with a model loaded
- [ ] Anti-hallucination verified (question outside documents returns "insufficient" response)

## Phase 2 — Production API (Next Steps)
See `docs/PHASE2_PROGRESS.md` when starting Phase 2.

Files to create:
- `backend/app/api/schemas.py` — Pydantic request/response models
- `backend/app/api/dependencies.py` — FastAPI Depends() wiring
- `backend/app/api/routes/health.py` — GET /api/v1/health
- `backend/app/api/routes/ask.py` — POST /api/v1/ask (+ streaming)
- `backend/app/api/routes/ingest.py` — POST /api/v1/ingest (UploadFile)
- `backend/app/main.py` — FastAPI app factory
- `backend/Dockerfile`
- `docker-compose.yml`
