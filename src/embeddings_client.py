# src/embeddings_client.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts):
    """Generate local embeddings using sentence-transformers."""
    return model.encode(texts, convert_to_numpy=True).tolist()
