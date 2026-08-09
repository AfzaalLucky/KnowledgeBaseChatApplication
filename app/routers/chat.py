import httpx
from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse

from app.ollama_client import chat, chat_stream
from app.retriever import search
from app.schemas import ChatRequest, ChatResponse, SourceChunk
from app.settings import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

_NO_DOCS_ANSWER = "No documents have been indexed yet. Upload a document before asking questions."


def _validate_question(question: str) -> str:
    question = question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty")
    if len(question) > settings.max_question_length:
        raise HTTPException(
            status_code=400,
            detail=f"Question exceeds {settings.max_question_length} character limit",
        )
    return question


@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    question = _validate_question(req.question)

    try:
        hits = search(question)
    except (httpx.ConnectError, ConnectionError) as e:
        raise HTTPException(status_code=503, detail="Ollama is unreachable") from e

    if not hits:
        return ChatResponse(answer=_NO_DOCS_ANSWER, sources=[])

    context = "\n\n".join(h["text"] for h in hits)

    try:
        answer = chat(context, question)
    except (httpx.ConnectError, ConnectionError) as e:
        raise HTTPException(status_code=503, detail="Ollama is unreachable") from e

    return ChatResponse(
        answer=answer,
        sources=[SourceChunk(document=h["document"], page=h["page"], text=h["text"]) for h in hits],
    )


@router.post("/stream")
async def chat_stream_endpoint(req: ChatRequest):
    question = _validate_question(req.question)

    try:
        hits = search(question)
    except (httpx.ConnectError, ConnectionError) as e:
        raise HTTPException(status_code=503, detail="Ollama is unreachable") from e

    if not hits:
        def empty_gen():
            yield _NO_DOCS_ANSWER
        return StreamingResponse(empty_gen(), media_type="text/plain")

    context = "\n\n".join(h["text"] for h in hits)

    def generate():
        try:
            for token in chat_stream(context, question):
                yield token
        except (httpx.ConnectError, ConnectionError):
            yield "\n\n[Error: Ollama is unreachable]"

    return StreamingResponse(generate(), media_type="text/plain")
