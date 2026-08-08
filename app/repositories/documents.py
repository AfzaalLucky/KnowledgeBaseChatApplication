from app.db import get_conn

_COLUMNS = "id, filename, file_type, file_size_bytes, status, chunk_count, error_message, uploaded_at, updated_at, stored_path"


def _row_to_dict(cursor, row) -> dict:
    columns = [c[0] for c in cursor.description]
    return dict(zip(columns, row))


def create_document(filename: str, file_type: str, file_size_bytes: int, stored_path: str) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Documents (filename, file_type, file_size_bytes, stored_path, status)
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, 'pending')
        """,
        (filename, file_type, file_size_bytes, stored_path),
    )
    doc_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return doc_id


def list_documents(search: str | None = None) -> list[dict]:
    conn = get_conn()
    cursor = conn.cursor()
    if search:
        cursor.execute(
            f"SELECT {_COLUMNS} FROM Documents WHERE filename LIKE ? ORDER BY uploaded_at DESC",
            (f"%{search}%",),
        )
    else:
        cursor.execute(f"SELECT {_COLUMNS} FROM Documents ORDER BY uploaded_at DESC")
    rows = [_row_to_dict(cursor, row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_document(doc_id: int) -> dict | None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {_COLUMNS} FROM Documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row) if row else None
    conn.close()
    return result


def update_document_status(
    doc_id: int,
    status: str,
    chunk_count: int | None = None,
    error_message: str | None = None,
) -> None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Documents
        SET status = ?, chunk_count = ?, error_message = ?, updated_at = GETDATE()
        WHERE id = ?
        """,
        (status, chunk_count, error_message, doc_id),
    )
    conn.commit()
    conn.close()


def get_chunk_qdrant_ids(doc_id: int) -> list[str]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT qdrant_id FROM Chunks WHERE doc_id = ?", (doc_id,))
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids


def delete_document(doc_id: int) -> None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Chunks WHERE doc_id = ?", (doc_id,))
    cursor.execute("DELETE FROM Documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
