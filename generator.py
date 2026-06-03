import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
LLM_MODEL = "llama-3.3-70b-versatile"


def generate_response(query, retrieved_chunks):
    """Generate a grounded answer from retrieved chunks."""
    if not retrieved_chunks:
        return {
            "answer": "I don't have enough information in the loaded documents to answer that question.",
            "sources": []
        }

    # Format chunks with source labels
    context = ""
    sources = []
    for chunk in retrieved_chunks:
        if chunk["distance"] < 0.7:
            context += f"[Source: {chunk['source']}]\n{chunk['text']}\n---\n"
            if chunk["source"] not in sources:
                sources.append(chunk["source"])

    if not context:
        return {
            "answer": "I don't have enough information in the loaded documents to answer that question.",
            "sources": []
        }

    system_message = """You are a medical information assistant. 
Answer using only the text provided below. 
Do not use any knowledge from your training data. 
Do not guess or fill in gaps. 
If the answer is not explicitly in the provided text, say exactly: 
"I don't have enough information in the loaded documents to answer that question."
Always start your answer with "According to [source name]..." to cite your source."""

    user_message = f"Documents:\n{context}\nQuestion: {query}"

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": sources
    }