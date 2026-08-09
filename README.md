# Knowledge Base Chat Application

A FastAPI + React Retrieval-Augmented Generation (RAG) project that lets you:

- Upload PDF, DOCX, and TXT documents through the web UI
- Chunk, embed, and store documents in Qdrant, with metadata in SQL Server
- Ask questions over ingested content using Ollama LLMs, with streaming answers

The backend exposes a REST API under `/api`, with interactive docs via Swagger. The frontend is a React + TypeScript SPA in `frontend/`.

## Tech Stack

- Python + FastAPI (backend)
- React + TypeScript + Vite + TanStack Query + Tailwind CSS (frontend)
- Qdrant (vector database)
- SQL Server (metadata storage)
- Ollama (local embeddings + chat model)
- LangChain document loaders + text splitting

## Project Structure

- `app/main.py`: FastAPI app, CORS, router mounting
- `app/routers/documents.py`: upload / list / get / delete documents
- `app/routers/chat.py`: `/api/chat` and `/api/chat/stream`
- `app/ingest.py`: multi-format ingestion (PDF/DOCX/TXT), chunking, embedding, storage
- `app/retriever.py`: semantic retrieval from Qdrant
- `app/storage.py`: upload validation (extension allow-list, size cap, magic bytes)
- `app/repositories/documents.py`: SQL Server CRUD for the `Documents`/`Chunks` tables
- `app/ollama_client.py`: embedding and chat calls to Ollama (streaming + non-streaming)
- `app/settings.py`: `pydantic-settings` config, sourced from `.env`
- `frontend/`: React + TypeScript SPA (Documents page, Chat page)
- `docker-compose.yml`: Qdrant service definition

## Prerequisites

1. Python 3.10+
2. Node.js / bun (for the frontend — `bun` is used in these instructions)
3. Docker Desktop (for Qdrant)
4. SQL Server running locally (localhost)
5. Microsoft ODBC Driver 17 for SQL Server
6. Ollama installed and running

## Configuration

Copy `.env.example` to `.env` and adjust as needed. Settings are loaded via `app/settings.py` (`pydantic-settings`):

- `QDRANT_URL`, `COLLECTION_NAME`
- `EMBEDDING_MODEL`, `CHAT_MODEL`, `EMBEDDING_DIM`
- `SQL_CONNECTION`
- `ALLOWED_ORIGINS` — CORS allow-list for the frontend origin
- `UPLOAD_DIR`, `MAX_UPLOAD_MB`, `ALLOWED_EXTENSIONS`
- `MAX_QUESTION_LENGTH`

Make sure a `KnowledgeBase` database exists in your local SQL Server instance.

## Install and Run

Open PowerShell in the project root and run:

### 1) Start Qdrant

```powershell
docker compose up -d
```

### 2) Backend — create venv, install deps, run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull nomic-embed-text
ollama pull llama3.2
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Frontend — install deps, run dev server

```powershell
cd frontend
bun install
bun dev
```

The Vite dev server runs at `http://localhost:5173` and proxies `/api/*` requests to `http://localhost:8000`.

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/documents` | Upload a document (multipart), returns `202` with `status=pending` |
| `GET` | `/api/documents` | List documents (`?search=`) |
| `GET` | `/api/documents/{id}` | Single document detail incl. status/chunk count |
| `DELETE` | `/api/documents/{id}` | Remove a document (SQL rows + Qdrant points + file) |
| `POST` | `/api/chat` | Ask a question, full response with sources |
| `POST` | `/api/chat/stream` | Ask a question, token-by-token streamed response |
| `GET` | `/api/health` | Liveness check |

Swagger UI: http://127.0.0.1:8000/docs

## Example Requests

### Upload a document

```powershell
curl -F "file=@handbook.pdf" http://127.0.0.1:8000/api/documents
```

### Ask a question

POST `/api/chat`

```json
{
  "question": "What does the memo say about password security?"
}
```

## Troubleshooting

- Qdrant connection errors:
  - Check Docker is running
  - Check container is up: docker ps
  - Check port 6333 is available

- SQL connection errors:
  - Verify SQL Server is running on localhost
  - Verify database KnowledgeBase exists
  - Install ODBC Driver 17 for SQL Server

- Ollama/model errors:
  - Ensure Ollama app/service is running
  - Ensure required models are pulled

- Import/module errors:
  - Confirm virtual environment is activated
  - Re-run pip install command

## Optional Helper Data

There is a utility script at app/generate_handbook.py that generates a sample PDF at data/documents/memos-2026.pdf.

Run it with:

```powershell
py app/generate_handbook.py
```

Then upload that generated PDF via the Documents page in the frontend, or `curl -F "file=@data/documents/memos-2026.pdf" http://127.0.0.1:8000/api/documents`.

## Stop Services

To stop Qdrant container:

```powershell
docker compose down
```