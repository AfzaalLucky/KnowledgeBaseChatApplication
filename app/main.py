from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.qdrant_client import init_qdrant
from app.routers import chat, documents
from app.schemas import HealthResponse
from app.settings import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
init_qdrant()

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok")


@app.get("/")
def home():
    return {
        "message": "Knowledge Base Chat API is running",
        "docs": "/docs",
    }
