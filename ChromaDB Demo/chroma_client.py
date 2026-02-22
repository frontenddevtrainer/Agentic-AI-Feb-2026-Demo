import os
from functools import lru_cache

import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

DEFAULT_COLLECTION = os.getenv("CHROMA_COLLECTION", "edureka-session-demo")
DEFAULT_TOP_K = int(os.getenv("CHROMA_TOP_K", "4"))


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Set it in a .env file or your shell."
        )
    return value


@lru_cache(maxsize=1)
def get_client() -> chromadb.CloudClient:
    return chromadb.CloudClient(
        api_key=_require_env("CHROMA_API_KEY"),
        tenant=_require_env("CHROMA_TENANT"),
        database=_require_env("CHROMA_DATABASE"),
    )


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    _require_env("OPENAI_API_KEY")
    return OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
    )


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    _require_env("OPENAI_API_KEY")
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.2,
    )


def get_vectorstore(collection_name: str | None = None) -> Chroma:
    return Chroma(
        client=get_client(),
        collection_name=collection_name or DEFAULT_COLLECTION,
        embedding_function=get_embeddings(),
    )
