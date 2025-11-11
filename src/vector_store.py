# src/vector_store.py
import os
import time
from typing import List, Dict
import chromadb
from chromadb import PersistentClient
from src.config import CHROMA_DIR, EMBED_BATCH
from src.embeddings_client import embed_texts

# ---------------------------------------------------------------------
# Initialize Chroma persistent client
# ---------------------------------------------------------------------
# This creates a local persisted vector DB inside CHROMA_DIR
client = PersistentClient(path=CHROMA_DIR)


# ---------------------------------------------------------------------
# Utility: Chunk long schema text into smaller pieces
# ---------------------------------------------------------------------
def chunk_text(text: str, max_chars: int = 2000) -> List[str]:
    chunks = []
    for i in range(0, len(text), max_chars):
        chunks.append(text[i:i + max_chars])
    return chunks


# ---------------------------------------------------------------------
# Upsert (insert/update) schema docs into vector store
# ---------------------------------------------------------------------
def upsert_table_docs(table_docs: List[Dict], collection_name: str = None):
    """
    Upserts schema table documentation (text + metadata) into Chroma vector DB.
    Automatically handles embeddings via `embed_texts`.

    Args:
        table_docs: list of dicts from schema_fetcher.extract_all()
        collection_name: override for Chroma collection (default: schema_<DB_NAME>)
    """
    if not table_docs:
        return {"collection": collection_name, "count": 0}

    # default collection name like: schema_demo_db
    collection_name = collection_name or f"schema_{table_docs[0]['db']}"

    # -----------------------------------------------------------------
    # Smart collection handling: reuse if exists, else create
    # -----------------------------------------------------------------
    existing_collections = [c.name for c in client.list_collections()]
    if collection_name in existing_collections:
        col = client.get_collection(collection_name)
    else:
        col = client.create_collection(name=collection_name)

    ids, metadatas, documents = [], [], []

    # -----------------------------------------------------------------
    # Flatten each table into text chunks with metadata
    # -----------------------------------------------------------------
    for td in table_docs:
        base_meta = {
            "table": td["table"],
            "db": td["db"],
            "schema_hash": td["schema_hash"],
            "created_at": td["created_at"]
        }

        chunks = chunk_text(td["text"], max_chars=2000)
        for i, c in enumerate(chunks):
            doc_id = f"{td['db']}::{td['table']}::chunk{i}::{td['schema_hash'][:8]}"
            ids.append(doc_id)
            metadatas.append({**base_meta, "chunk_index": i})
            documents.append(c)

    # -----------------------------------------------------------------
    # Compute embeddings in batches (using your local model)
    # -----------------------------------------------------------------
    all_embeddings = []
    for i in range(0, len(documents), EMBED_BATCH):
        batch = documents[i:i + EMBED_BATCH]
        emb = embed_texts(batch)
        all_embeddings.extend(emb)
        time.sleep(0.05)  # prevent CPU burst

    # -----------------------------------------------------------------
    # Add/update embeddings in vector DB
    # -----------------------------------------------------------------
    col.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=all_embeddings
    )

    # client.persist()

    return {"collection": collection_name, "count": len(documents)}


# ---------------------------------------------------------------------
# Semantic similarity search (RAG lookup)
# ---------------------------------------------------------------------
def similarity_search(query: str, collection_name: str = None, k: int = 4):
    """
    Performs a semantic search in the vector DB to retrieve relevant schema chunks.

    Args:
        query: natural language question
        collection_name: defaults to schema_<DB_NAME>
        k: number of top relevant chunks to return
    """
    collection_name = collection_name or f"schema_{os.getenv('DB_NAME')}"
    col = client.get_collection(collection_name)

    # embed the query using same embedding model
    q_emb = embed_texts([query])[0]

    results = col.query(
        query_embeddings=[q_emb],
        n_results=k,
        include=["metadatas", "documents"]
    )

    # Convert Chroma format into list[{"text": str, "metadata": dict}]
    out = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        out.append({"text": doc, "metadata": meta})

    return out
