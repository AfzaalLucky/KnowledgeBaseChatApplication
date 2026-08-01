import pyodbc
from app.config import SQL_CONNECTION

def get_conn():
    return pyodbc.connect(SQL_CONNECTION)

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

    conn.commit()
    conn.close()