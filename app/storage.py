import os
import re
import uuid

from fastapi import HTTPException, UploadFile

from app.settings import settings

_MAGIC_BYTES: dict[str, bytes] = {
    ".pdf": b"%PDF-",
}

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    name = os.path.basename(filename).strip()
    name = _SAFE_NAME_RE.sub("_", name)
    return name or "upload"


def save_upload(upload: UploadFile) -> tuple[str, str, int]:
    """Validates and streams an upload to disk.

    Returns (stored_path, extension, size_bytes). Raises HTTPException on
    any validation failure (bad extension, oversized file, bad magic bytes).
    """
    original_name = upload.filename or "upload"
    ext = os.path.splitext(original_name)[1].lower()

    if ext not in settings.allowed_extensions:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {ext or 'unknown'}")

    os.makedirs(settings.upload_dir, exist_ok=True)

    stored_name = f"{uuid.uuid4()}_{sanitize_filename(original_name)}"
    stored_path = os.path.join(settings.upload_dir, stored_name)

    max_bytes = settings.max_upload_mb * 1024 * 1024
    chunk_size = 1024 * 1024
    size = 0
    magic = _MAGIC_BYTES.get(ext)
    first_chunk_checked = False

    try:
        with open(stored_path, "wb") as out:
            while True:
                chunk = upload.file.read(chunk_size)
                if not chunk:
                    break

                if not first_chunk_checked:
                    if magic and not chunk.startswith(magic):
                        raise HTTPException(status_code=415, detail="File content does not match its extension")
                    first_chunk_checked = True

                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_mb}MB limit")

                out.write(chunk)
    except HTTPException:
        if os.path.exists(stored_path):
            os.remove(stored_path)
        raise
    except OSError as e:
        if os.path.exists(stored_path):
            os.remove(stored_path)
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}") from e

    return stored_path, ext, size