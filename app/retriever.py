# from app.qdrant_client import get_client
# from app.ollama_client import embed
# from app.config import COLLECTION_NAME

# def search(query: str, top_k: int = 5):
#     qdrant = get_client()

#     query_vector = embed(query)

#     results = qdrant.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=query_vector,
#         limit=top_k
#     )

#     return [r.payload["text"] for r in results]


from app.qdrant_client import get_client
from app.ollama_client import embed
from app.config import COLLECTION_NAME

def search(query: str, top_k: int = 5):
    client = get_client()

    query_vector = embed(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True
    )

    return [point.payload["text"] for point in results.points]