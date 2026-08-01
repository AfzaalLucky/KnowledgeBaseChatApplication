from fastapi import FastAPI
from pydantic import BaseModel

from app.retriever import search
from app.ollama_client import chat
from app.ingest import ingest_file
from app.db import init_db
from app.qdrant_client import init_qdrant

app = FastAPI()

init_db()
init_qdrant()

class Query(BaseModel):
    question: str

@app.get("/")
def home():
    return {
        "message": "Knowledge Base Chat API is running",
        "endpoints": ["/docs", "/chat", "/ingest"]
    }

@app.post("/chat")
def chat_endpoint(query: Query):
    docs = search(query.question)

    context = "\n\n".join(docs)

    answer = chat(context, query.question)

    return {
        "answer": answer,
        "sources": docs
    }

# @app.post("/ingest")
# def ingest_endpoint(file_path: str):
#     return ingest_file(file_path)

class IngestRequest(BaseModel):
    file_path: str
    
@app.post("/ingest")
def ingest_endpoint(req: IngestRequest):
    return ingest_file(req.file_path)