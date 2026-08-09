import uuid

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ollama_client import embed
from app.qdrant_client import get_client
from app.repositories import documents as documents_repo
from app.settings import settings

_LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": TextLoader,
}

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " ", ""],
)


def ingest_document(doc_id: int, stored_path: str, ext: str) -> None:
    """Parses, chunks, embeds, and persists an already-uploaded document.

    Runs as a background task after the upload request has returned, so
    failures here are recorded on the Documents row rather than raised
    to an HTTP client.
    """
    try:
        documents_repo.update_document_status(doc_id, "processing")

        doc = documents_repo.get_document(doc_id)
        filename = doc["filename"] if doc else stored_path

        loader_cls = _LOADERS.get(ext)
        if loader_cls is None:
            raise ValueError(f"Unsupported file type: {ext}")

        loaded = loader_cls(stored_path).load()
        chunks = _splitter.split_documents(loaded)

        qdrant = get_client()
        points = []
        chunk_rows = []

        for chunk in chunks:
            chunk_text = chunk.page_content
            if not chunk_text.strip():
                continue

            vector = embed(chunk_text)
            qdrant_id = str(uuid.uuid4())

            points.append({
                "id": qdrant_id,
                "vector": vector,
                "payload": {
                    "text": chunk_text,
                    "page": chunk.metadata.get("page", 0),
                    "document": filename,
                    "doc_id": doc_id,
                },
            })
            chunk_rows.append((doc_id, chunk_text, qdrant_id))

        if points:
            qdrant.upsert(collection_name=settings.collection_name, points=points)
        documents_repo.insert_chunks(chunk_rows)

        documents_repo.update_document_status(doc_id, "completed", chunk_count=len(chunk_rows))
    except Exception as e:
        documents_repo.update_document_status(doc_id, "failed", error_message=str(e))
