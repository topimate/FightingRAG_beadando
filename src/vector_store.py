
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


from src.config import (
    CHUNKS_PATH,
    DB_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)


def load_embedding_model():
    """Load the local multilingual embedding model."""
    return SentenceTransformer(EMBEDDING_MODEL)


def load_chunks():
    """Read processed chunks from JSONL."""
    with CHUNKS_PATH.open(encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def build_vector_store():
    """Create and persist the vector database."""
    chunks = load_chunks()
    model = load_embedding_model()

    client = chromadb.PersistentClient(path=str(DB_PATH))

    # Recreate the collection to avoid stale chunks.
    try:
        client.delete_collection(COLLECTION_NAME)
    except chromadb.errors.NotFoundError:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 32

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]

        texts = [
            "passage: " + chunk["text"]
            for chunk in batch
        ]

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        collection.add(
            ids=[chunk["id"] for chunk in batch],
            embeddings=embeddings.tolist(),
            documents=[chunk["text"] for chunk in batch],
            metadatas=[
                {
                    "sport": chunk["sport"],
                    "document_type": chunk["document_type"],
                    "source": chunk["source"],
                    "filename": chunk["filename"],
                    "page": chunk["page"],
                }
                for chunk in batch
            ],
        )

        print(
            f"Indexed {min(start + batch_size, len(chunks))}"
            f"/{len(chunks)} chunks"
        )

    print(f"\nCollection: {COLLECTION_NAME}")
    print(f"Total indexed chunks: {collection.count()}")


if __name__ == "__main__":
    build_vector_store()
