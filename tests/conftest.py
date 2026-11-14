"""Shared test setup.

- Tests use a separate database (rag_test) on a real Postgres + pgvector.
- Every Gemini call is replaced by a fake. A real call raises, so tests stay free and fast.
"""

import hashlib
import math
import os
import re
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

# --- configure BEFORE importing the app (settings and engine are created at import) ---
TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://rag:rag@localhost:5432/rag_test"
)
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["GEMINI_API_KEY"] = "test-key-not-real"
os.environ["MAX_DISTANCE"] = "0.6"


def _ensure_database(url: str) -> None:
    u = make_url(url)
    admin = create_engine(u.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": u.database})
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{u.database}"'))
    admin.dispose()


_ensure_database(TEST_DB_URL)

from google.genai import types  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import embeddings, llm  # noqa: E402
from app.config import settings  # noqa: E402
from app.db import SessionLocal, engine, init_db  # noqa: E402
from app.main import app  # noqa: E402


# ------------------------------------------------------------------ fake embedder

def fake_vector(text_: str) -> list[float]:
    """Deterministic bag-of-words vector: texts sharing words are close in cosine space."""
    v = [0.0] * settings.embedding_dim
    for word in re.findall(r"[a-z0-9]{4,}", text_.lower()):
        v[int(hashlib.md5(word.encode()).hexdigest(), 16) % len(v)] += 1.0
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]


# --------------------------------------------------------------------- fake Gemini

class FakeGemini:
    """Stands in for genai.Client. Returns scripted responses and records every request."""

    def __init__(self):
        self.script: list[types.GenerateContentResponse] = []
        self.requests: list[SimpleNamespace] = []
        self.models = self

    def generate_content(self, model, contents, config):
        self.requests.append(SimpleNamespace(contents=contents, config=config))
        if not self.script:
            raise AssertionError("unexpected LLM call")
        return self.script.pop(0)


def text_response(s: str) -> types.GenerateContentResponse:
    return types.GenerateContentResponse(candidates=[types.Candidate(content=types.Content(
        role="model", parts=[types.Part.from_text(text=s)]))])


def call_response(*calls: tuple[str, dict]) -> types.GenerateContentResponse:
    parts = [types.Part(function_call=types.FunctionCall(name=n, args=a)) for n, a in calls]
    return types.GenerateContentResponse(candidates=[types.Candidate(content=types.Content(
        role="model", parts=parts))])


# ------------------------------------------------------------------------ fixtures

def _no_real_calls():
    raise RuntimeError("Real Gemini call attempted in tests")


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Every test: no network, and a fake embedder by default."""
    monkeypatch.setattr(embeddings, "get_client", _no_real_calls)
    monkeypatch.setattr(llm, "get_client", _no_real_calls)
    monkeypatch.setattr(embeddings, "embed_documents", lambda chunks, title: [fake_vector(c) for c in chunks])
    monkeypatch.setattr(embeddings, "embed_query", fake_vector)


@pytest.fixture
def fake_llm(monkeypatch) -> FakeGemini:
    fake = FakeGemini()
    monkeypatch.setattr(llm, "get_client", lambda: fake)
    return fake


@pytest.fixture(scope="session")
def _schema():
    init_db()  # extension, tables, seeded techniques
    yield
    engine.dispose()


@pytest.fixture
def db(_schema):
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE documents, chunks RESTART IDENTITY CASCADE"))
    with SessionLocal() as session:
        yield session


@pytest.fixture
def client(db):
    with TestClient(app) as c:
        yield c
