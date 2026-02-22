# ChromaDB Cloud Demo

A Streamlit application that lets you ingest documents (PDF, text, markdown) into a **ChromaDB Cloud** vector store to build a RAG (Retrieval-Augmented Generation) index using LangChain and OpenAI embeddings.

---

## Project Structure

```
ChromaDB Demo/
├── chroma_client.py       # Shared client: ChromaDB Cloud, OpenAI embeddings & LLM setup
├── upload_document.py     # Streamlit UI for ingesting documents into ChromaDB
├── requirements.txt       # Python dependencies
└── README.md
```

---

## What is ChromaDB?

[ChromaDB](https://www.trychroma.com/) is an open-source vector database designed for AI applications. It stores document embeddings and supports fast similarity search, making it ideal for RAG pipelines.

**ChromaDB Cloud** is the hosted version — no local server required. You connect via an API key, tenant, and database identifier obtained from the [Chroma Dashboard](https://www.trychroma.com/).

---

## Prerequisites

- Python 3.10+
- A [ChromaDB Cloud](https://www.trychroma.com/) account
- An [OpenAI](https://platform.openai.com/) API key

---

## Setup

### 1. Clone / navigate to the project

```bash
cd "ChromaDB Demo"
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the root `.env.example` to a `.env` file inside the project root and fill in your credentials:

```bash
cp ../.env.example ../.env
```

Then edit `.env`:

```env
OPENAI_API_KEY=sk-...           # Required — used for embeddings & LLM
CHROMA_API_KEY=...              # From ChromaDB Cloud dashboard
CHROMA_TENANT=...               # Your ChromaDB tenant ID
CHROMA_DATABASE=...             # Your ChromaDB database name
```

**Optional overrides:**

| Variable                  | Default                    | Description                          |
|---------------------------|----------------------------|--------------------------------------|
| `CHROMA_COLLECTION`       | `edureka-session-demo`     | Default collection name              |
| `CHROMA_TOP_K`            | `4`                        | Number of results returned per query |
| `OPENAI_EMBEDDINGS_MODEL` | `text-embedding-3-small`   | OpenAI embedding model               |
| `OPENAI_MODEL`            | `gpt-4o-mini`              | OpenAI chat model                    |

---

## Running the App

```bash
streamlit run upload_document.py
```

The app will open at `http://localhost:8501`.

---

## Using the App

1. **Sidebar** — set the collection name and chunking parameters:
   - **Chunk size**: number of characters per chunk (default 900)
   - **Chunk overlap**: overlap between consecutive chunks (default 150)

2. **Paste text** — enter a source label and paste raw content directly.

3. **Upload files** — upload one or more `.txt`, `.md`, or `.pdf` files.

4. Click **Ingest into Chroma** to split documents into chunks and add them to your ChromaDB Cloud collection.

5. Expand **Preview chunks** to inspect the first 5 ingested chunks.

---

## How It Works

```
User input (text / files)
        │
        ▼
RecursiveCharacterTextSplitter   ← configurable chunk size & overlap
        │
        ▼
OpenAIEmbeddings                 ← text-embedding-3-small (default)
        │
        ▼
ChromaDB Cloud                   ← vectors stored in your collection
```

- `chroma_client.py` provides cached singletons (`get_client`, `get_embeddings`, `get_llm`, `get_vectorstore`) used across the project.
- All credentials are loaded from environment variables via `python-dotenv`.

---

## Getting ChromaDB Cloud Credentials

1. Sign up at [https://www.trychroma.com/](https://www.trychroma.com/)
2. Create a **database** in your dashboard
3. Copy your **API key**, **tenant**, and **database** name into your `.env` file

---

## Dependencies

| Package                    | Purpose                              |
|----------------------------|--------------------------------------|
| `chromadb`                 | ChromaDB client                      |
| `langchain-chroma`         | LangChain ↔ ChromaDB integration     |
| `langchain-openai`         | OpenAI embeddings & chat models      |
| `langchain-text-splitters` | Document chunking                    |
| `pypdf`                    | PDF text extraction                  |
| `streamlit`                | Web UI                               |
| `python-dotenv`            | `.env` file loading                  |
