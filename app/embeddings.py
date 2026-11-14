from functools import lru_cache

from google import genai
from google.genai import types

from app.config import settings

BATCH_SIZE = 50  # texts per API request


@lru_cache
def get_client() -> genai.Client:
    """Create the Gemini client once, on first use (so importing needs no key)."""
    return genai.Client(api_key=settings.gemini_api_key)


def _embed(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        result = get_client().models.embed_content(
            model=settings.embedding_model,
            # Each text must be its own Content object. A plain list of strings
            # would be merged into ONE embedding by gemini-embedding-2.
            contents=[types.Content(parts=[types.Part.from_text(text=t)]) for t in batch],
            config=types.EmbedContentConfig(output_dimensionality=settings.embedding_dim),
        )
        vectors.extend(e.values for e in result.embeddings)
    return vectors


# gemini-embedding-2 has no task_type parameter. Instead, a text prefix tells the
# model whether it is embedding a document or a query, so the two land in the
# right places in vector space for retrieval ("asymmetric" search).

def embed_documents(chunks: list[str], title: str) -> list[list[float]]:
    return _embed([f"title: {title} | text: {c}" for c in chunks])


def embed_query(question: str) -> list[float]:
    return _embed([f"task: question answering | query: {question}"])[0]
