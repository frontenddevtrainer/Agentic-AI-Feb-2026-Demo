from typing import List
import streamlit as st
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from chroma_client import DEFAULT_COLLECTION, get_vectorstore

st.set_page_config(page_title="Chroma Cloud Ingest", layout="wide")

st.title("Chroma Cloud Ingest")
st.caption("Upload or paste content to build a RAG index.")

with st.sidebar:
    st.subheader("Collection")
    collection_name = st.text_input("Collection name", DEFAULT_COLLECTION)
    st.subheader("Chunking")
    chunk_size = st.number_input("Chunk size", min_value=200, max_value=4000, value=900)
    chunk_overlap = st.number_input("Chunk overlap", min_value=0, max_value=1000, value=150)


st.subheader("Paste text")
text_source = st.text_input("Source label", value="manual")
raw_text = st.text_area("Paste content", height=200)

st.subheader("Upload files")
uploaded_files = st.file_uploader(
    "Supported types: .txt, .md, .pdf",
    type=["txt", "md", "pdf"],
    accept_multiple_files=True,
)

def _documents_from_uploads(files) -> List[Document]:
    documents: List[Document] = []
    for uploaded in files:
        name = uploaded.name
        if name.lower().endswith(".pdf"):
            reader = PdfReader(uploaded)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            content = uploaded.getvalue()
            text = content.decode("utf-8", errors="ignore")
        if text.strip():
            documents.append(Document(page_content=text, metadata={"source": name}))
    return documents


def _documents_from_text(text: str, source: str) -> List[Document]:
    if not text.strip():
        return []
    return [Document(page_content=text, metadata={"source": source})]

if st.button("Ingest into Chroma"):
    documents: List[Document] = []
    documents.extend(_documents_from_text(raw_text, text_source))
    documents.extend(_documents_from_uploads(uploaded_files or []))

    if not documents:
        st.warning("Add some text or upload files before ingesting.")
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(chunk_size),
            chunk_overlap=int(chunk_overlap),
        )
        chunks = splitter.split_documents(documents)
        for idx, doc in enumerate(chunks, start=1):
            doc.metadata["chunk"] = idx

        vectorstore = get_vectorstore(collection_name)
        vectorstore.add_documents(chunks)

        st.success(f"Ingested {len(chunks)} chunks into '{collection_name}'.")
        with st.expander("Preview chunks", expanded=False):
            for doc in chunks[:5]:
                st.markdown(f"**{doc.metadata.get('source', 'unknown')}**")
                st.write(doc.page_content[:500])