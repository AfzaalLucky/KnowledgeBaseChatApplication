import pyodbc

from app.settings import settings


def get_conn():
    return pyodbc.connect(settings.sql_connection)


def _add_column_if_missing(cursor, table: str, column: str, ddl: str):
    cursor.execute(
        """
        IF NOT EXISTS (
            SELECT * FROM sys.columns
            WHERE object_id = OBJECT_ID(?) AND name = ?
        )
        EXEC(?)
        """,
        (table, column, f"ALTER TABLE {table} ADD {ddl}"),
    )


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Documents')
    CREATE TABLE Documents (
        id INT IDENTITY PRIMARY KEY,
        filename NVARCHAR(255),
        uploaded_at DATETIME DEFAULT GETDATE()
    )
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Chunks')
    CREATE TABLE Chunks (
        id INT IDENTITY PRIMARY KEY,
        doc_id INT,
        content NVARCHAR(MAX),
        qdrant_id NVARCHAR(255)
    )
    """)

    _add_column_if_missing(cursor, "Documents", "file_type", "file_type NVARCHAR(20) NULL")
    _add_column_if_missing(cursor, "Documents", "file_size_bytes", "file_size_bytes BIGINT NULL")
    _add_column_if_missing(cursor, "Documents", "status", "status NVARCHAR(20) NOT NULL DEFAULT 'pending'")
    _add_column_if_missing(cursor, "Documents", "chunk_count", "chunk_count INT NULL")
    _add_column_if_missing(cursor, "Documents", "error_message", "error_message NVARCHAR(MAX) NULL")
    _add_column_if_missing(cursor, "Documents", "updated_at", "updated_at DATETIME NULL")
    _add_column_if_missing(cursor, "Documents", "stored_path", "stored_path NVARCHAR(1000) NULL")

    conn.commit()
    conn.close()
