"""
Chunking Strategy Comparison — Milestone 6 Stretch Feature
Tests 300-char vs 600-char chunking on the same 5 evaluation queries.
Run this standalone: python chunking_comparison.py
"""

import os
from sentence_transformers import SentenceTransformer
import numpy as np

DOCS_PATH = "documents"
MODEL_NAME = "all-MiniLM-L6-v2"

TEST_QUERIES = [
    "What are the signs and symptoms of osteoporosis?",
    "What is the proper handwashing technique?",
    "When should a nurse escalate a patient's condition?",
    "What are the side effects of metformin?",
    "How should a nurse assess pain in a non-verbal patient?",
]


def load_documents():
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({"filename": filename, "text": text})
    return documents


def clean_document(text):
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return " ".join(cleaned_lines)


def chunk_document(text, filename, chunk_size, overlap=50, min_length=50):
    chunks = []
    prefix = filename.replace(".txt", "").replace(" ", "_").lower()
    counter = 0
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()
        if len(chunk_text) >= min_length:
            chunks.append({
                "text": chunk_text,
                "source": filename,
                "chunk_id": f"{prefix}_{counter}",
            })
            counter += 1
        start += chunk_size - overlap
    return chunks


def embed(texts, model):
    return model.encode(texts, normalize_embeddings=True)


def cosine_similarity(a, b):
    return float(np.dot(a, b))


def retrieve_top3(query, chunks, model):
    query_emb = embed([query], model)[0]
    chunk_texts = [c["text"] for c in chunks]
    chunk_embs = embed(chunk_texts, model)
    scores = [cosine_similarity(query_emb, ce) for ce in chunk_embs]
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
    return [(chunks[i], scores[i]) for i in top_indices]


def run_comparison():
    print("Loading documents...")
    documents = load_documents()

    print("Building chunk sets...")
    chunks_300 = []
    chunks_600 = []
    for doc in documents:
        cleaned = clean_document(doc["text"])
        chunks_300.extend(chunk_document(cleaned, doc["filename"], chunk_size=300))
        chunks_600.extend(chunk_document(cleaned, doc["filename"], chunk_size=600))

    print(f"300-char strategy: {len(chunks_300)} total chunks")
    print(f"600-char strategy: {len(chunks_600)} total chunks")

    print("\nLoading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("\n" + "="*70)
    print("CHUNKING STRATEGY COMPARISON RESULTS")
    print("="*70)

    for query in TEST_QUERIES:
        print(f"\nQUERY: {query}")
        print("-" * 60)

        print("\n[300-char chunks] Top 3 results:")
        results_300 = retrieve_top3(query, chunks_300, model)
        for chunk, score in results_300:
            print(f"  Score: {score:.3f} | Source: {chunk['source']}")
            print(f"  Text: {chunk['text'][:120]}...")

        print("\n[600-char chunks] Top 3 results:")
        results_600 = retrieve_top3(query, chunks_600, model)
        for chunk, score in results_600:
            print(f"  Score: {score:.3f} | Source: {chunk['source']}")
            print(f"  Text: {chunk['text'][:120]}...")

        print()

    print("="*70)
    print("Done. Copy the results above into your README comparison section.")
    print("="*70)


if __name__ == "__main__":
    run_comparison()
    