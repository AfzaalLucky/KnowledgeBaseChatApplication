from app.ollama_client import embed
from app.qdrant_client import get_client
from app.settings import settings


def search(query: str, top_k: int = 5) -> list[dict]:
    client = get_client()

    query_vector = embed(query)

    results = client.query_points(
        collection_name=settings.collection_name,
        query=query_vector,
        limit=top_k,
        with_payload=True
    )

    return [
        {
            "document": point.payload["document"],
            "page": point.payload.get("page", 0),
            "text": point.payload["text"],
        }
        for point in results.points
    ]
