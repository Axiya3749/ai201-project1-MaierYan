# The Unofficial Guide — Project 1

---

## Domain

This system helps nurses and healthcare workers quickly find answers to clinical questions. Sources like the CDC, NIH, WHO, and ANA have great information, but their guidelines are long and not easy to search through during a busy shift. This system lets you type a plain English question and get a cited answer right away.

The knowledge here is important because clinical accuracy matters. A nurse who needs to know the right escalation threshold or metformin side effects mid-shift doesn't have time to skim through a 20-page PDF. This system is built to make that faster.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | CDC | Handwashing guidelines | cdc.gov — `documents/Handwash 1.txt` |
| 2 | WHO | Handwashing technique | who.int — `documents/Handwash 2.txt` |
| 3 | MedlinePlus | Metformin side effects | medlineplus.gov — `documents/Metformin 1.txt` |
| 4 | NIH | Metformin usage | nih.gov — `documents/Metformin 2.txt` |
| 5 | ANA | Nurse escalation protocol | nursingworld.org — `documents/Nurse 1.txt` |
| 6 | NIH | When to escalate care | nih.gov — `documents/Nurse 2.txt` |
| 7 | NIAMS | Osteoporosis overview | niams.nih.gov — `documents/Osteoporosis 1.txt` |
| 8 | NIH | Osteoporosis symptoms | nih.gov — `documents/Osteoporosis 2.txt` |
| 9 | ANA | Pain assessment for non-verbal patients | nursingworld.org — `documents/Pain 1.txt` |
| 10 | NIH | Pain scales and tools | nih.gov — `documents/Pain 2.txt` |

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**
Medical guidelines are usually short and to the point. One recommendation is often just one or two sentences. I chose 300 characters because it's big enough to hold one complete idea without accidentally combining two unrelated topics. The 50 character overlap means that if a sentence gets cut across two chunks, it will still show up fully in at least one of them. The documents were plain text files so no special preprocessing was needed beyond basic cleaning.

**Final chunk count:** Varies across the 10 source files. The ChromaDB collection prints the total when the app starts up.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, run locally through ChromaDB.

**Production tradeoff reflection:**
I used `all-MiniLM-L6-v2` because it runs locally, it's fast, and it works well for a prototype. The downside is that it was trained on general web text, not medical content, so it might not understand clinical terms as well as a specialized model would. If this were a real hospital tool, I'd look into something like `BiomedBERT` or OpenAI's `text-embedding-3-large` for better accuracy on medical language. Those options come with higher cost and API latency though, which would be a real concern in a high-volume clinical setting. Multilingual support would also matter for hospitals serving patients who don't speak English.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt I passed to `llama-3.3-70b-versatile` via Groq says:

> *"You are a medical information assistant. Answer using only the text provided below. Do not use any knowledge from your training data. Do not guess or fill in gaps. If the answer is not explicitly in the provided text, say exactly: 'I don't have enough information in the loaded documents to answer that question.' Always start your answer with 'According to [source name]...' to cite your source."*

This does three things: it tells the model to only use the retrieved text, gives it an exact phrase to say when it doesn't have enough info, and forces it to start every answer with a source citation.

**How source attribution is surfaced in the response:**
Before sending chunks to the LLM, I filter out any chunk with a cosine distance above 0.7. This removes low-quality matches so the model isn't working with irrelevant text. Each chunk is also labeled with `[Source: filename]` so the model knows where it came from. In the Gradio app, sources are shown separately in a "Retrieved from" box below the answer.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are the signs and symptoms of osteoporosis? | Silent disease, no symptoms until a bone breaks; vertebral fracture causes back pain, height loss, kyphosis | Correctly said osteoporosis is a "silent" disease, cited Osteoporosis 1.txt, and described back pain, height loss, and stooped posture from vertebral fractures | Relevant | Accurate |
| 2 | What is the proper handwashing technique? | Wet hands, apply soap, scrub for 20 seconds including backs and between fingers, rinse, dry; use 60% alcohol sanitizer if no soap | Cited Handwash 2.txt and mentioned singing "Happy Birthday" twice for timing, but said "a more detailed step-by-step guide is not provided" even though the full CDC steps were in Handwash 1.txt | Partially relevant | Partially accurate |
| 3 | When should a nurse escalate a patient's condition? | Abnormal vital signs, unexpected deterioration, signs of cardiorespiratory arrest; activate rapid response early | Cited Nurse 2.txt and mentioned Early Warning Systems (EWS) protocols, but said exact escalation thresholds were "not explicitly stated in the provided text" | Partially relevant | Partially accurate |
| 4 | What are the side effects of metformin? | Diarrhea, nausea, stomach issues, fatigue, headache, nail changes, muscle pain, rash; chest pain is serious | Cited both Metformin 1.txt and 2.txt, listed GI side effects, taste disturbance, dizziness, liver injury, and chest pain | Relevant | Accurate |
| 5 | How should a nurse assess pain in a non-verbal patient? | Use NVPS, BPS, or DOLOPLUS2; observe facial expressions and movement; use physiologic indicators as supplement only | Cited Pain 1.txt, mentioned observational tools, facial expressions, and correctly said physiologic indicators like heart rate variability should supplement but not replace behavioral tools | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** *What is the proper handwashing technique?*

**What the system returned:**
The system cited Handwash 2.txt and mentioned the "Happy Birthday" song as a timing trick, plus rinsing and drying with a paper towel. Then it said "a more detailed, step-by-step guide is not provided in the given documents." That's wrong. The full CDC step-by-step technique is in Handwash 1.txt, but the system never retrieved it.

**Root cause (tied to a specific pipeline stage):**
This is a chunking problem that caused a retrieval failure. The CDC steps in Handwash 1.txt are written as a numbered list: wet hands, apply soap, lather, scrub for 20 seconds, rinse, dry. With a 300 character chunk size, each step got split into its own chunk. Each individual chunk was too short and lacked enough context to score well against the full query "what is the proper handwashing technique." Meanwhile, the WHO source (Handwash 2.txt) had a more complete-sounding sentence about the "Happy Birthday" timing trick, so that chunk ranked higher. The model got the WHO chunk but not the CDC steps, and honestly reported that a complete guide wasn't in the text it received.

**What you would change to fix it:**
I would increase the chunk size to around 500 characters so numbered list steps stay together in one chunk instead of being split up. I'd also consider adding metadata filters so a query that mentions "CDC" retrieves from Handwash 1.txt specifically, regardless of which source scores higher on semantic similarity.

---

## Spec Reflection

**One way the spec helped you during implementation:**
Writing out the chunking strategy in planning.md before touching any code was actually really useful. I had already decided on 300 characters with 50 character overlap and written down exactly why before I started coding. That made it easy to just implement what I had planned instead of guessing at a number mid-build. It also helped when I was prompting Claude to write the chunking function because I could paste in the spec section and get back exactly what I wanted.

**One way your implementation diverged from the spec, and why:**
The spec said top-k of 3 to 5 chunks, but I ended up setting `N_RESULTS = 5` in retriever.py. When I tested with only 3 chunks, questions that needed information from two different source files (like pain assessment, which uses both Pain 1.txt and Pain 2.txt) weren't getting full answers. Going up to 5 fixed that. The 0.7 distance filter in generator.py made sure low-relevance chunks didn't sneak through even with a higher k.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The chunking strategy section from planning.md, which specified 300 character chunks with 50 character overlap, and asked Claude to implement `chunk_document()` using a sliding window approach.
- *What it produced:* A working function that split text by character count and moved forward by chunk size minus overlap on each step, with source filename attached to each chunk.
- *What I changed or overrode:* It didn't include a `chunk_id` field, which ChromaDB needs to store chunks without creating duplicates. I told Claude to add a deterministic ID using `f"{filename}_chunk_{i}"` and it updated the function.

**Instance 2**

- *What I gave the AI:* The retrieval approach section from planning.md (all-MiniLM-L6-v2, ChromaDB, cosine similarity, top-k=3) and asked it to implement `embed_and_store()` and `retrieve()`.
- *What it produced:* A complete retriever.py with persistent ChromaDB storage and a retrieve function that returned documents and metadata.
- *What I changed or overrode:* The function didn't return the distance score. I needed that so generator.py could filter out chunks that were too far from the query. I asked Claude to add it and updated the threshold logic myself.

**Instance 3**

- *What I gave the AI:* All five source code files and the README template, and asked Claude to write the full Milestone 6 README based on the actual code.
- *What it produced:* A complete README draft with all required sections filled in.
- *What I changed or overrode:* The draft said `N_RESULTS = 6` which was wrong. My code uses 5. I caught it and had Claude fix it. I also ran all 5 test questions in the app and sent screenshots of the real responses so the evaluation table could reflect what the system actually returned, not what was predicted. That changed Q2 (handwashing) from accurate to partially accurate and made it the main failure case.
