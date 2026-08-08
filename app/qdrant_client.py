from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, VectorParams

from app.settings import settings

client = QdrantClient(url=settings.qdrant_url)


def get_client():
    return client


def init_qdrant(vector_size: int = settings.embedding_dim):
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if settings.collection_name not in existing:
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        print(f"[QDRANT] Created collection: {settings.collection_name}")
    else:
        print(f"[QDRANT] Collection already exists: {settings.collection_name}")


def delete_by_doc_id(doc_id: int) -> None:
    client.delete(
        collection_name=settings.collection_name,
        points_selector=Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
        ),
    )
