# Interview prep: Security RAG API

## 15 questions with short model answers

**1. Why RAG and not fine-tuning?**
Fine-tuning changes *how* a model writes; it is a poor way to add *facts*. Facts
learned in training cannot be cited, are hard to update, and the model may still
mix them up. RAG keeps knowledge in a database: updating it is an upload, every
answer cites its sources, and the model can say "not found". Fine-tuning fits
style, format or narrow skills; RAG fits changing, citable knowledge. They can be
combined.

**2. Why chunk documents, and why overlap?**
An embedding is one vector per text. A whole document becomes a blurry average
that matches nothing well, and would waste prompt tokens. ~500-token chunks give
precise matches and small prompts. Overlap (~50 tokens) means a fact cut at a
chunk boundary still appears whole in the next chunk. Cost: ~10% more storage
and embedding.

**3. Why cosine distance?**
It compares the direction of vectors and ignores their length; for text
embeddings, direction carries meaning. For normalized vectors, cosine, dot
product and Euclidean give the same ranking. pgvector: `<=>` cosine,
`<#>` negative inner product, `<->` L2. The HNSW index must be built with the
matching operator class (`vector_cosine_ops`).

**4. Why pgvector and not Pinecone / Weaviate / Qdrant?**
One system for vectors, text, metadata and relational data (like the techniques
table), with transactions, joins, backups and SQL I already know. HNSW handles
millions of vectors comfortably. A dedicated vector DB is worth it at very large
scale, for very high query rates, or for features like built-in hybrid search and
multi-tenancy at scale. Start simple; move when measurements say so.

**5. How do you reduce hallucination?**
Layers: (1) retrieval grounding; (2) a relevance gate, so there is no LLM call
without evidence; (3) a system prompt that says to answer only from context and
admit gaps; (4) required citations, validated against the retrieved chunk ids;
(5) a `confident` flag; (6) negative questions in the eval set to *measure*
refusals. You never reach zero; you measure and reduce.

**6. How could prompt injection happen through uploaded documents, and how do
you defend against it?**
Indirect prompt injection: a document contains text like "ignore your
instructions and ...". When it is retrieved, that text lands in the prompt.
Defences here: chunks wrapped in tags and labelled untrusted; the system prompt
forbids following instructions in them; the output is bound to a JSON schema; the
only tool is read-only, whitelisted and validates its arguments; the 1 MB upload
limit. Main point: prompt-level defences are never complete, so limit what a
manipulated model *can do* (least privilege for tools).

**7. How does your tool-calling loop work?**
Send the question plus a function declaration (name, description, JSON schema).
If the model replies with a `function_call`, my code (not the model) validates
it, runs `get_technique`, and sends back a `function_response`, keeping the
model's turn unchanged (Gemini 3 thought signatures). Repeat until the model stops
calling tools or 3 rounds are reached. Automatic function calling is disabled so
every step is visible and controlled.

**8. Why is `get_technique` a tool rather than part of the vector store?**
An exact ID lookup should be exact. A primary-key SELECT is always correct;
vector search is approximate and may confuse T1110.003 with T1110.004 because
their texts are similar. Retrieval for fuzzy questions, tools for exact or live
data.

**9. How do you get reliable structured output?**
The API is given a JSON schema generated from a Pydantic model, so generation is
constrained. I still validate: Pydantic checks the shape, and my code checks that
cited ids were really retrieved. On failure I retry once, then return a clear 502.
Model output is untrusted input.

**10. How do you evaluate the system?**
A fixed set of 28 questions with expected sources and required keywords, including
tool questions and off-topic negatives. Two separate metrics: retrieval hit rate
(was the right document in the top 5?) and answer correctness (keywords present,
or a correct refusal). Separating them shows whether a failure is in search or in
generation. The script exits non-zero under 80%, so it gates changes.

**11. What are the weaknesses of your eval?**
It is small (one question is ~3.6 points), I wrote it myself after reading the
documents, and keyword matching misses paraphrases and can be fooled. Next steps:
more questions written by others, a held-out set I do not tune on, and
LLM-as-judge alongside the keyword check.

**12. How do you test code that calls an LLM?**
Split deterministic logic from the model call and fake the client. My tests use a
real Postgres + pgvector and a fake Gemini client that returns real SDK objects
from a script and records requests. Tests check behaviour (retry, tool loop,
gate, error mapping, what was sent), not answer quality. Quality is the eval's
job. 38 tests run in under a second with no API key.

**13. How did you choose the relevance threshold?**
I logged the cosine distances for in-scope and off-topic questions and set
`MAX_DISTANCE` between the two groups, then checked with the eval: negatives
measure whether it is too loose, `rag` questions whether it is too strict. It is
config, not code, because it depends on the embedding model and the data.

**14. What would you change for production?**
Ingestion in a background queue with retries; Alembic migrations; structure-aware
chunking with metadata; hybrid search plus a reranker; auth and per-user document
access; rate limiting; a read-only database role for tools; tracing of every LLM
call (prompt, latency, tokens, cost); caching of query embeddings; storing the
embedding model name with each vector so re-embedding is manageable.

**15. Why no LangChain?**
For a project of this size, a framework hides the parts I wanted to understand
and control: chunking, the prompt, the tool loop, validation and retries. Each is
a few dozen lines. Without the abstraction, debugging is reading my own code, and
SDK changes (like Gemini's embedding API merging a list of strings into one
vector) are visible instead of buried. I would consider a framework when a team
needs its integrations or standard patterns.

---

## Resume bullets

- Built a Retrieval-Augmented Generation API (FastAPI, PostgreSQL/pgvector, Google
  Gemini) that answers security questions from uploaded MITRE ATT&CK notes and
  incident response playbooks with chunk-level citations; hand-wrote chunking,
  embedding, HNSW cosine search and prompt construction without orchestration frameworks.
- Implemented a hand-written LLM tool-calling loop (read-only ATT&CK lookup) and
  schema-constrained JSON output validated with Pydantic, retry-on-failure and a
  relevance gate that refuses off-topic questions without calling the model.
- Created a 28-question evaluation suite reaching **[XX]% top-5 retrieval hit rate** and
  **[XX]% answer correctness**, run as a regression gate in GitHub Actions alongside 38
  Pytest tests (mocked LLM, real pgvector), all packaged with Docker Compose.
