# Knowledge Base Chat Application

A FastAPI-based Retrieval-Augmented Generation (RAG) project that lets you:

- Ingest PDF documents
- Store document chunk embeddings in Qdrant
- Store document and chunk metadata in SQL Server
- Ask questions over ingested content using Ollama LLMs

The app exposes REST endpoints for ingestion and chat, with interactive API docs via Swagger.

## Tech Stack

- Python + FastAPI
- Qdrant (vector database)
- SQL Server (metadata storage)
- Ollama (local embeddings + chat model)
- LangChain text splitting + PDF loader

## Project Structure

- app/main.py: FastAPI app and endpoints
- app/ingest.py: PDF ingestion, chunking, embedding, storage
- app/retriever.py: Semantic retrieval from Qdrant
- app/ollama_client.py: Embedding and chat calls to Ollama
- app/db.py: SQL Server initialization and queries
- app/config.py: Runtime settings (DB, models, Qdrant URL)
- docker-compose.yml: Qdrant service definition

## Prerequisites

1. Python 3.10+
2. Docker Desktop (for Qdrant)
3. SQL Server running locally (localhost)
4. Microsoft ODBC Driver 17 for SQL Server
5. Ollama installed and running

## Configuration

The app uses static config from app/config.py:

- QDRANT_URL = http://localhost:6333
- COLLECTION_NAME = kb_chat
- EMBEDDING_MODEL = nomic-embed-text
- CHAT_MODEL = llama3.2
- SQL Server connection string uses:
  - SERVER=localhost
  - DATABASE=KnowledgeBase
  - Trusted_Connection=yes

Make sure a KnowledgeBase database exists in your local SQL Server instance.

## Install and Run

Open PowerShell in the project root and run:

### 1) Start Qdrant

```powershell
docker compose up -d
```

### 2) Create and activate virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```powershell
pip install fastapi uvicorn pyodbc qdrant-client ollama langchain-community langchain-text-splitters pypdf python-docx reportlab
```

### 4) Pull Ollama models

```powershell
ollama pull nomic-embed-text
ollama pull llama3.2
```

### 5) Run the API

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- GET / : Health/info route
- POST /ingest : Ingest one PDF file
- POST /chat : Ask questions over indexed content
- GET /docs : Swagger UI

Swagger URL:

- http://127.0.0.1:8000/docs

## Example Requests

### Ingest a PDF

POST /ingest

```json
{
  "file_path": "D:\\path\\to\\document.pdf"
}
```

### Ask a question

POST /chat

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

Then ingest that generated PDF using the /ingest endpoint.

## Stop Services

To stop Qdrant container:

```powershell
docker compose down
```