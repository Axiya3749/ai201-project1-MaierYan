import gradio as gr
from retriever import retrieve, _collection, embed_and_store
from generator import generate_response
from ingest import load_documents, clean_document, chunk_document


def setup():
    """Load and embed documents if not already done."""
    if _collection.count() == 0:
        print("Loading and embedding documents...")
        documents = load_documents()
        all_chunks = []
        for doc in documents:
            cleaned = clean_document(doc["text"])
            chunks = chunk_document(cleaned, doc["filename"])
            all_chunks.extend(chunks)
        embed_and_store(all_chunks)
        print("Ready!")


def handle_query(question):
    if not question.strip():
        return "", ""
    chunks = retrieve(question)
    result = generate_response(question, chunks)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


# Run setup
setup()

with gr.Blocks(title="Medical Guide") as demo:
    gr.HTML("<h1>🏥 Medical Unofficial Guide</h1>")
    gr.HTML("<p>Ask questions about handwashing, osteoporosis, metformin, nursing escalation, and pain assessment.</p>")

    inp = gr.Textbox(label="Your question", placeholder='e.g. "What are the side effects of metformin?"')
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()