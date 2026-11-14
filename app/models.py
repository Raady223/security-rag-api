from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.db import Base


class Document(Base):
    """One uploaded file."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class Chunk(Base):
    """A ~500-token piece of a document, plus its embedding vector."""

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer)  # position inside the document
    content: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(settings.embedding_dim))

    document: Mapped[Document] = relationship(back_populates="chunks")

    __table_args__ = (
        # HNSW = approximate nearest-neighbour index. vector_cosine_ops makes it
        # serve queries that sort by cosine distance (the <=> operator).
        Index(
            "ix_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class Technique(Base):
    """A MITRE ATT&CK technique. Plain SQL table, looked up by the get_technique tool."""

    __tablename__ = "techniques"

    technique_id: Mapped[str] = mapped_column(String(16), primary_key=True)  # e.g. "T1110"
    name: Mapped[str] = mapped_column(String(255))
    tactic: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
