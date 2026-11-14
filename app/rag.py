"""The RAG pipeline itself, independent of HTTP. Used by the API and by the eval script."""

import logging
import re
from pathlib import Path

from sqlalchemy.orm import Session

from app import embeddings, llm, retrieval, tools
from app.chunking import chunk_text
from app.config import settings
from app.models import Chunk, Document

log = logging.getLogger(__name__)

MENTIONS_TECHNIQUE = re.compile(r"\bT\d{4}(\.\d{3})?\b", re.IGNORECASE)

NOT_FOUND = llm.Answer(
    answer="Not found: the uploaded documents do not cover this question.",
    sources=[],
    confident=False,
)


class EmbeddingError(Exception):
    """The embedding API call failed."""


def ingest_document(db: Session, filename: str, content: str) -> Document | None:
    """Chunk, embed and store one document. Returns None if the text is empty."""
    chunks = chunk_text(content)
    if not chunks:
        return None

    # Embed BEFORE writing anything, so a failed API call leaves no half-stored document.
    try:
        vectors = embeddings.embed_documents(chunks, title=Path(filename).stem)
    except Exception as exc:
        raise EmbeddingError(f"Embedding service failed: {exc}") from exc

    doc = Document(filename=filename)
    doc.chunks = [
        Chunk(chunk_index=i, content=c, embedding=v)
        for i, (c, v) in enumerate(zip(chunks, vectors, strict=True))
    ]
    db.add(doc)
    db.commit()  # one transaction: the document and all its chunks, or nothing
    return doc


def answer_question(db: Session, question: str) -> tuple[llm.Answer, list[retrieval.RetrievedChunk]]:
    """Embed -> search -> relevance gate -> (tools) -> structured answer.

    Returns the answer AND the top-k retrieved chunks, so the eval can score retrieval.
    Raises EmbeddingError or llm.LLMError.
    """
    try:
        query_vector = embeddings.embed_query(question)
    except Exception as exc:
        raise EmbeddingError(f"Embedding service failed: {exc}") from exc

    retrieved = retrieval.search(db, query_vector, k=settings.top_k)
    log.info("question=%r distances=%s", question, [(c.id, round(c.distance, 3)) for c in retrieved])

    # Relevance gate: if nothing is close enough, do not spend an LLM call
    # (and do not give the model a chance to make something up).
    # Exception: a question naming a technique ID (e.g. "What is T1003?") can still
    # be answered by the get_technique tool, so we continue without the far chunks.
    context = retrieved
    if not retrieved or retrieved[0].distance > settings.max_distance:
        if not MENTIONS_TECHNIQUE.search(question):
            return NOT_FOUND, retrieved
        context = []

    answer = llm.generate_answer(
        question, context, execute=lambda name, args: tools.run_tool(db, name, args)
    )
    return answer, retrieved
