import ollama
from app.config import EMBEDDING_MODEL, CHAT_MODEL

def embed(text: str):
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )
    return response["embedding"]

def chat(context: str, question: str):
    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Answer ONLY using the provided context."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ]
    )
    return response["message"]["content"]