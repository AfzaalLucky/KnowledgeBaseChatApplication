import ollama

from app.settings import settings


def embed(text: str):
    response = ollama.embeddings(
        model=settings.embedding_model,
        prompt=text
    )
    return response["embedding"]


def chat(context: str, question: str):
    response = ollama.chat(
        model=settings.chat_model,
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


def chat_stream(context: str, question: str):
    stream = ollama.chat(
        model=settings.chat_model,
        messages=[
            {
                "role": "system",
                "content": "Answer ONLY using the provided context."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ],
        stream=True,
    )
    for part in stream:
        content = part["message"]["content"]
        if content:
            yield content
