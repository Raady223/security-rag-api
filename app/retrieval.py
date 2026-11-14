from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, Document


@dataclass
class RetrievedChunk:
    id: int
    filename: str
    content: str
    distance: float  # cosine distance: 0 = same direction, 1 = unrelated, 2 = opposite


def search(db: Session, query_vector: list[float], k: int = 5) -> list[RetrievedChunk]:
    """Return the k chunks whose embeddings are closest to the query by cosine distance."""
    distance = Chunk.embedding.cosine_distance(query_vector).label("distance")  # SQL: embedding <=> :q
    stmt = (
        select(Chunk.id, Document.filename, Chunk.content, distance)
        .join(Document, Chunk.document_id == Document.id)
        .order_by(distance)  # ascending: closest first; served by the HNSW index
        .limit(k)
    )
    return [RetrievedChunk(*row) for row in db.execute(stmt)]
