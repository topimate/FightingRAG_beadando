
import chromadb

from src.vector_store import (
    DB_PATH,
    COLLECTION_NAME,
    load_embedding_model,
)


def search(question: str, top_k: int = 5):
    model = load_embedding_model()

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    query_embedding = model.encode(
        ["query: " + question],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    for index, (document, metadata, distance) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ),
        start=1,
    ):
        print(f"\n{'=' * 60}")
        print(f"RESULT {index}")
        print(f"Sport: {metadata['sport']}")
        print(f"Source: {metadata['source']}")
        print(f"Page: {metadata['page']}")
        print(f"Cosine distance: {distance:.4f}")
        print("-" * 60)
        print(document[:900])


if __name__ == "__main__":
    question = (
        "What protective equipment is required "
        "for WAKO K-1 competitions?"
    )

    print(f"QUESTION: {question}")
    search(question)
