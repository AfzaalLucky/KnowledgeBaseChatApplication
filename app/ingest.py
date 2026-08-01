import uuid

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.db import get_conn
from app.qdrant_client import get_client
from app.ollama_client import embed
from app.config import COLLECTION_NAME


def ingest_file(file_path: str):
    """
    Reads a PDF, splits it into chunks, stores metadata in SQL Server,
    and stores embeddings in Qdrant.
    """

    # ----------------------------
    # Load PDF
    # ----------------------------
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    print("=" * 60)
    print(f"PDF Pages Loaded : {len(documents)}")

    # ----------------------------
    # Split into chunks
    # ----------------------------
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    print(f"Chunks Created   : {len(chunks)}")
    print("=" * 60)

    # ----------------------------
    # Database
    # ----------------------------
    conn = get_conn()
    cursor = conn.cursor()

    doc_name = file_path.split("\\")[-1].split("/")[-1]

    cursor.execute(
        """
        INSERT INTO Documents (filename)
        OUTPUT INSERTED.id
        VALUES (?)
        """,
        doc_name
    )

    doc_id = cursor.fetchone()[0]

    # ----------------------------
    # Qdrant
    # ----------------------------
    qdrant = get_client()

    points = []

    # ----------------------------
    # Process each chunk
    # ----------------------------
    for i, chunk in enumerate(chunks, start=1):

        chunk_text = chunk.page_content

        print(f"\nChunk {i}")
        print(f"Length : {len(chunk_text)}")
        print(chunk_text[:150])
        print("-" * 40)

        vector = embed(chunk_text)

        qdrant_id = str(uuid.uuid4())

        points.append(
            {
                "id": qdrant_id,
                "vector": vector,
                "payload": {
                    "text": chunk_text,
                    "page": chunk.metadata.get("page", 0),
                    "document": doc_name
                }
            }
        )

        cursor.execute(
            """
            INSERT INTO Chunks
            (doc_id, content, qdrant_id)
            VALUES (?, ?, ?)
            """,
            (
                doc_id,
                chunk_text,
                qdrant_id
            )
        )

    # ----------------------------
    # Upload all vectors at once
    # ----------------------------
    if points:
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "document": doc_name,
        "pages": len(documents),
        "chunks": len(chunks)
    }