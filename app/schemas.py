from datetime import datetime
from typing import Literal

from pydantic import BaseModel

DocumentStatus = Literal["pending", "processing", "completed", "failed"]


class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str | None
    file_size_bytes: int | None
    status: DocumentStatus
    chunk_count: int | None
    error_message: str | None
    uploaded_at: datetime
    updated_at: datetime | None


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    status: DocumentStatus


class ChatRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    document: str
    page: int
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


class HealthResponse(BaseModel):
    status: Literal["ok"]
