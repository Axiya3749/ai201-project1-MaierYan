import chromadb
from chromadb.utils import embedding_functions
from ingest import load_documents, clean_document, chunk_document

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = "./chroma_db"
CHROMA_COLLECTION = "medical_guides"
N_RESULTS = 5

# Initialize embedding function and ChromaDB
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def embed_and_store(chunks):
    """Embed chunks and store in ChromaDB."""
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} chunks in vector database.")


def retrieve(query, n_results=N_RESULTS):
    """Search for most relevant chunks for a query."""
    if _collection.count() == 0:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i]
        })

    return chunks


if __name__ == "__main__":
    # Load and store chunks if collection is empty
    if _collection.count() == 0:
        print("Loading and embedding documents...")
        documents = load_documents()
        all_chunks = []
        for doc in documents:
            cleaned = clean_document(doc["text"])
            chunks = chunk_document(cleaned, doc["filename"])
            all_chunks.extend(chunks)
        embed_and_store(all_chunks)

    # Test retrieval with 3 queries
    test_queries = [
        "What are the signs and symptoms of osteoporosis?",
        "What is the proper handwashing technique?",
        "What are the side effects of metformin?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        results = retrieve(query)
        for chunk in results:
            print(f"[{chunk['source']}] (dist: {chunk['distance']:.3f}) {chunk['text'][:80]}...")