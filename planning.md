# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

This system makes clinical medical knowledge searchable for nurses and healthcare practitioners. Official guidelines from CDC, NIH, and ANA are comprehensive but long — finding a specific answer mid-shift requires skimming through multiple pages. This system allows practitioners to ask plain-language 
questions and get grounded, cited answers instantly.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | CDC | Handwashing guidelines | cdc.gov | Handwash 1.txt
| 2 | WHO | Handwashing technique  | who.int | Handwash 2.txt
| 3 | MedlinePlus | Metformin side effects | medlineplus.gov | Metformin 1.txt
| 4 | NIH | Metformin usage | nih.gov | Metformin 2.txt
| 5 | ANA | Nurse escalation protocol | nursingworld.org | Nurse 1.txt
| 6 | NIH | When to escalate care | nih.gov | Nurse 2.txt
| 7 | NIAMS | Osteoporosis overview | niams.nih.gov | Osteoporosis 1.txt
| 8 | NIH | Osteoporosis symptoms | nih.gov | Osteoporosis 2.txt
| 9 | ANA | Pain assessment non-verbal | nursingworld.org | Pain 1.txt
| 10 | NIH | Pain scales and tools | nih.gov | Pain 2.txt

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size: 300 characters**

**Overlap: 50 characters**

**Reasoning: Medical guidelines pack a lot of meaning into short passages — one guideline is often 1-3 sentences. 300 characters captures one complete clinical guideline without merging unrelated topics.**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model: all-MiniLM-L6-v2 via sentence-transformers**

**Top-k: 3-5 chunks**

**Production tradeoff reflection: For a production medical system I would consider a larger model like text-embedding-3-large for higher accuracy on clinical text, multilingual support for non-English speaking patients, and 
longer context length to capture complex guidelines. However these come with higher cost and API latency.**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
1 | What are the signs and symptoms of osteoporosis? | Osteoporosis is a silent disease with no symptoms until a bone breaks. Symptoms of vertebral fracture include severe back pain, loss of height, and stooped posture (kyphosis). Bones may become so fragile that fractures occur from minor falls, bending, 
lifting, or even coughing.
2 | What is the proper handwashing technique? | WWet hands with clean running water, apply soap, lather by rubbing hands together including backs, between fingers and 
under nails, scrub for at least 20 seconds, rinse well under clean running water, dry with a clean towel or air dryer. If soap unavailable, use hand sanitizer with at least 60% alcohol.
3 | When should a nurse escalate a patient's condition? | A nurse should escalate when a patient shows abnormal vital signs, unexpected clinical deterioration, or premonitory signs 
of cardiorespiratory arrest. Rapid response systems should be activated early — abnormal vital signs can precede critical deterioration by hours. Early recognition and escalation can 
prevent cardiac arrest and reduce mortality.
4 | What are the side effects of metformin? | Common side effects include diarrhea, nausea, stomach discomfort, gas, indigestion,constipation, lack of energy, weakness, change in taste, headache, flushing, nail changes, 
muscle pain, and rash. Serious side effects include chest pain which requires immediate medical attention.
5 | How should a nurse assess pain in a non-verbal patient? | Use observational tools such as the Nonverbal Pain Scale, Behavioral Pain Scale, or DOLOPLUS2. Assess facial expressions, upper limb movements, fussiness, consolability, and motor control. Physiologic indicators like heart rate variability and 
oxygen saturation can supplement but should not be used alone. A holistic approach using multiple tools is most accurate.
---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Chunks may cut mid-sentence splitting a complete clinical guideline across two chunks, making retrieval incomplete.

2. Medical terms may not embed well with a general-purpose model — "FLACC scale" may not match "pain assessment tool" semantically.

3. Documents contain heavy bullet point formatting which may get split mid-list during chunking, making individual chunks lose context (e.g. a bullet point without its header).

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

## Architecture

Document Ingestion (ingest.py - loads .txt files from /documents)
        ↓
Chunking (ingest.py - character-based sliding window, 300 chars, 50 overlap)
        ↓
Embedding + Vector Store (retriever.py - all-MiniLM-L6-v2 + ChromaDB)
        ↓
Retrieval (retriever.py - cosine similarity semantic search, top-k=3)
        ↓
Generation (generator.py - Groq llama-3.3-70b-versatile)
        ↓
UI (app.py - Gradio web interface)
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking: Give Claude my Chunking Strategy section and ask it to implement chunk_text() with 300 char size and 50 char overlap.**

**Milestone 4 — Embedding and retrieval: Give Claude my Retrieval Approach section and pipeline diagram and ask it to implement embed_and_store() and retrieve() using ChromaDB and sentence-transformers.**

**Milestone 5 — Generation and interface: Give Claude my grounding requirements and ask it to implement generate_response() and a Gradio UI with answer and source fields.**

## Stretch Feature: Chunking Strategy Comparison
Tested 300-char vs 600-char chunking on the same 5 evaluation queries to compare retrieval quality.
