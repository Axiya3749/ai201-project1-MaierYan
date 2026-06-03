import os

DOCS_PATH = "documents"

def load_documents():
    """Load all .txt files from the documents folder."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({
                "filename": filename,
                "text": text,
            })
    print(f"Loaded {len(documents)} document(s)")
    return documents


def clean_document(text):
    """Remove unwanted content from document text."""
    # Remove extra whitespace and blank lines
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:  # skip empty lines
            cleaned_lines.append(line)
    return " ".join(cleaned_lines)


def chunk_document(text, filename):
    """Split document into 300-character chunks with 50-character overlap."""
    chunk_size = 300
    overlap = 50
    min_length = 50

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


if __name__ == "__main__":
    documents = load_documents()
    all_chunks = []

    for doc in documents:
        cleaned = clean_document(doc["text"])
        chunks = chunk_document(cleaned, doc["filename"])
        all_chunks.extend(chunks)
        print(f"{doc['filename']}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")

    # Print 5 sample chunks to inspect
    print("\n--- 5 SAMPLE CHUNKS ---")
    for chunk in all_chunks[:5]:
        print(f"\n[{chunk['source']}] ID: {chunk['chunk_id']}")
        print(chunk['text'])
        print("-" * 40)