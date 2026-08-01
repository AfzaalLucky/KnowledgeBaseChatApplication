from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from app.config import QDRANT_URL, COLLECTION_NAME

client = QdrantClient(url=QDRANT_URL)


def get_client():
    return client


def init_qdrant(vector_size: int = 768):
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        print(f"[QDRANT] Created collection: {COLLECTION_NAME}")
    else:
        print(f"[QDRANT] Collection already exists: {COLLECTION_NAME}")