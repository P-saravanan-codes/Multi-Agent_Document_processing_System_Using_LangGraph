"""Chroma vector store for RAG."""

import hashlib
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from config.settings import CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE
from utils.embeddings import get_embeddings


def _collection_name(file_path: str) -> str:
    digest = hashlib.md5(Path(file_path).name.encode()).hexdigest()[:12]
    return f"doc_{digest}"


def build_vector_store(text: str, file_path: str) -> Chroma:
    """Chunk document text and persist to Chroma."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    if not chunks:
        chunks = [text[:CHUNK_SIZE] if text else "empty document"]

    collection = _collection_name(file_path)
    persist_dir = str(CHROMA_DIR / collection)

    return Chroma.from_texts(
        texts=chunks,
        embedding=get_embeddings(),
        collection_name=collection,
        persist_directory=persist_dir,
    )


def load_vector_store(file_path: str) -> Chroma | None:
    """Load an existing Chroma collection for a document."""
    collection = _collection_name(file_path)
    persist_dir = CHROMA_DIR / collection
    if not persist_dir.exists():
        return None
    return Chroma(
        collection_name=collection,
        embedding_function=get_embeddings(),
        persist_directory=str(persist_dir),
    )
