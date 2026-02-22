import json
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from chroma_client import DEFAULT_COLLECTION
from rag_agent import get_graph

app = FastAPI(title="LangGraph RAG + Chroma Cloud")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    collection: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]


def _format_sources(docs: list[Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for doc in docs:
        meta = doc.metadata or {}
        sources.append(
            {
                "source": meta.get("source"),
                "chunk": meta.get("chunk"),
                "id": meta.get("id"),
            }
        )
    return sources


@app.get("/")
async def root():
    return {"status": "ok", "service": "langgraph-rag"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    collection = request.collection or DEFAULT_COLLECTION
    graph = get_graph(collection)
    result = await graph.ainvoke({"question": request.message})
    return ChatResponse(
        answer=result.get("answer", ""),
        sources=_format_sources(result.get("docs", [])),
    )


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    collection = request.collection or DEFAULT_COLLECTION
    graph = get_graph(collection)

    async def event_generator():
        async for chunk in graph.astream(
            {"question": request.message}, stream_mode="custom"
        ):
            if isinstance(chunk, dict) and chunk.get("type") == "token":
                payload = json.dumps(chunk)
                yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
