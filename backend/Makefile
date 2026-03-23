.PHONY: install run test test-cov lint format ingest ask docker-build docker-run

install:
	pip install -r requirements.txt

run:
	PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=. pytest tests/ -v -m "not integration"

test-cov:
	PYTHONPATH=. pytest tests/ -v -m "not integration" --cov=app --cov-report=term-missing --cov-report=html

test-integration:
	PYTHONPATH=. pytest tests/ -v

lint:
	black --check app/ tests/
	isort --check-only app/ tests/

format:
	black app/ tests/
	isort app/ tests/

# Ingest documents: make ingest DIR=docs/
ingest:
	PYTHONPATH=. python scripts/ingest.py --dir $(DIR)

# Ask a question: make ask Q="What is the savings rate?"
ask:
	PYTHONPATH=. python scripts/ask.py "$(Q)"

docker-build:
	docker build -t banking-ai-assistant:latest .

docker-run:
	docker run --env-file .env -p 8000:8000 banking-ai-assistant:latest
