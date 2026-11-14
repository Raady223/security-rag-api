import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import llm, rag
from app.db import get_db, init_db

logging.basicConfig(level=logging.INFO)

ALLOWED_EXTENSIONS = {".txt", ".md"}
MAX_UPLOAD_BYTES = 1_000_000  # 1 MB is plenty for text and protects the free API quota


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # runs once when the server starts
    yield


app = FastAPI(title="Security RAG API", lifespan=lifespan)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Report whether the API is up and the database answers a trivial query."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "unreachable", "detail": str(exc)},
        )
    return {"status": "ok", "database": "ok"}


class DocumentOut(BaseModel):
    document_id: int
    filename: str
    chunk_count: int


@app.post("/documents", response_model=DocumentOut, status_code=201)
def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    """Validate the upload, then chunk, embed and store it."""
    filename = file.filename or "upload"
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only .txt and .md files are accepted")

    raw = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File is larger than 1 MB")
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "File must be UTF-8 text")

    try:
        doc = rag.ingest_document(db, filename, content)
    except rag.EmbeddingError as exc:
        raise HTTPException(502, str(exc))
    if doc is None:
        raise HTTPException(400, "File is empty")
    return DocumentOut(document_id=doc.id, filename=filename, chunk_count=len(doc.chunks))


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


@app.post("/ask", response_model=llm.Answer)
def ask(req: AskRequest, db: Session = Depends(get_db)):
    """Answer a question using only the uploaded documents (and the get_technique tool)."""
    try:
        answer, _ = rag.answer_question(db, req.question)
    except (rag.EmbeddingError, llm.LLMError) as exc:
        raise HTTPException(502, str(exc))  # the upstream model failed, not our code
    return answer
