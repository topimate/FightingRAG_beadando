
from functools import lru_cache

import chromadb

from src.vector_store import (
    DB_PATH,
    COLLECTION_NAME,
    load_embedding_model,
)


@lru_cache(maxsize=1)
def get_resources():
    """Load model and database once per Python process."""
    model = load_embedding_model()
    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_collection(COLLECTION_NAME)
    return model, collection


def retrieve(
    question: str,
    top_k: int = 6,
    sport: str | None = None,
) -> list[dict]:
    """Search the vector database, optionally filtering by sport."""

    model, collection = get_resources()

    embedding = model.encode(
        ["query: " + question],
        normalize_embeddings=True,
    ).tolist()

    query_args = {
        "query_embeddings": embedding,
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }

    if sport is not None:
        query_args["where"] = {"sport": sport}

    results = collection.query(**query_args)

    passages = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        passages.append({
            "text": text,
            "sport": metadata["sport"],
            "source": metadata["source"],
            "filename": metadata["filename"],
            "document_type": metadata["document_type"],
            "page": metadata["page"],
            "distance": distance,
        })

    return passages


def retrieve_sport_aware(
    question: str,
    top_k: int = 6,
) -> list[dict]:
    """Retrieve passages separately from the relevant sports."""
    from src.sport_detector import detect_sports

    sports = detect_sports(question)

    if not sports:
        return retrieve(question, top_k=top_k)

    base_count, remainder = divmod(top_k, len(sports))

    passages = []

    for index, sport in enumerate(sports):
        count = base_count + (1 if index < remainder else 0)

        if count > 0:
            passages.extend(
                retrieve(question, top_k=count, sport=sport)
            )

    return passages
