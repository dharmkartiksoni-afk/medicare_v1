# Medical Chapter Knowledge Graph

Generate structured study notes, embeddings, and an interactive graph UI for medical textbook chapters.

## Prerequisites

- Python 3.11+
- Node 20+ (for local frontend dev)
- Docker & Docker Compose (for containerized setup)
- `.env` containing `OPENAI_API_KEY` (and optional overrides `SUMMARY_MODEL`, `EMBEDDING_MODEL`)

## Python Pipeline

Create the virtual environment of your choice and install dependencies:

```bash
pip install -r requirements.txt
```

Generate artifacts for the sample chapter:

```bash
python -m pipeline.cli chapter1 --source data/input/chapter1.txt
```

Output JSON is saved to `data/output/chapter1.json` containing:

- Chunk summaries with key points and flashcards
- Extracted relation triples
- Graph nodes & edges
- OpenAI embeddings for semantic search

## FastAPI Backend

Run locally after installing requirements:

```bash
uvicorn api.main:app --reload --port 8000
```

Key endpoints:

- `POST /ingest` – queue chapter processing (`{"chapter_id": "chapter1"}`)
- `GET /graph/{chapter_id}` – graph data and chunk summaries
- `POST /search` – semantic search across summaries
- `GET /healthz` – health check

## React Frontend

Install and start Vite dev server:

```bash
cd frontend
npm install
npm run dev
```

The UI offers:

- Pipeline trigger and chapter selector
- Force-directed knowledge graph with node highlighting
- Semantic search with chunk preview
- Flashcard-style QA display for each chunk

## Docker Compose Workflow

Build and launch the full stack:

```bash
docker compose build
docker compose up
```

Services:

- `api` (port `8000`) – FastAPI with the OpenAI-powered pipeline
- `frontend` (port `3000`) – Nginx serving the React single-page app

The compose file mounts the repository into the `api` container to keep hot reloads simple. Ensure `.env` is present before starting so the API container receives `OPENAI_API_KEY`.

## Next Steps

- Tune prompts in `pipeline/llm.py` for chapter-specific consistency
- Add persistence beyond JSON (e.g., Postgres + pgvector)
- Extend UI with node filtering, timeline comparisons, or spaced-repetition exports
