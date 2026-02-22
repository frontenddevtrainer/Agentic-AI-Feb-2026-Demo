from __future__ import annotations

from functools import lru_cache
from typing import List, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from chroma_client import DEFAULT_COLLECTION, DEFAULT_TOP_K, get_llm, get_vectorstore

SYSTEM_PROMPT = (
    "You are a helpful RAG assistant. Use the provided context to answer the question. "
    "If the context does not contain the answer, say you don't know and suggest what to "
    "ingest to answer better."
)

class RAGState(TypedDict):
    question: str
    docs: List[Document]
    answer: str

def _format_context(docs: List[Document]) -> str:
    if not docs:
        return ""
    chunks = []
    for idx, doc in enumerate(docs, start=1):
        source = (doc.metadata or {}).get("source", "unknown")
        chunks.append(f"[{idx}] Source: {source}\n{doc.page_content}")
    return "\n\n".join(chunks)

@lru_cache(maxsize=8)
def get_graph(collection_name: str = DEFAULT_COLLECTION):
    retriever = get_vectorstore(collection_name).as_retriever(
        search_kwargs={"k": DEFAULT_TOP_K}
    )
    llm = get_llm()

    def retrieve(state: RAGState):
        docs = retriever.invoke(state["question"])
        return {"docs": docs}

    async def generate(state: RAGState):
        writer = get_stream_writer()
        context = _format_context(state.get("docs", []))
        question = state["question"]
        user_prompt = (
            f"Question: {question}\n\n"
            f"Context:\n{context if context else '[no context retrieved]'}"
        )
        messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(user_prompt)]

        parts: List[str] = []
        async for chunk in llm.astream(messages):
            if chunk.content:
                parts.append(chunk.content)
                writer({"type": "token", "content": chunk.content})

        return {"answer": "".join(parts)}

    graph = StateGraph(RAGState)
    
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()

