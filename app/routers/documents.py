import os

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile

from app.ingest import ingest_document
from app.qdrant_client import delete_by_doc_id
from app.repositories import documents as documents_repo
from app.schemas import DocumentOut, DocumentUploadResponse
from app.storage import save_upload

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(file: UploadFile, background_tasks: BackgroundTasks):
    stored_path, ext, _size_bytes = save_upload(file)

    doc_id = documents_repo.create_document(
        filename=file.filename or os.path.basename(stored_path),
        file_type=ext.lstrip("."),
        file_size_bytes=_size_bytes,
        stored_path=stored_path,
    )

    background_tasks.add_task(ingest_document, doc_id, stored_path, ext)

    return DocumentUploadResponse(id=doc_id, filename=file.filename or stored_path, status="pending")


@router.get("", response_model=list[DocumentOut])
async def list_documents(search: str | None = None):
    return documents_repo.list_documents(search)


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(doc_id: int):
    doc = documents_repo.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: int):
    doc = documents_repo.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    delete_by_doc_id(doc_id)
    documents_repo.delete_document(doc_id)

    stored_path = doc.get("stored_path")
    if stored_path and os.path.exists(stored_path):
        os.remove(stored_path)
