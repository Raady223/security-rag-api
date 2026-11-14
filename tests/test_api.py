import json

from conftest import call_response, fake_vector, text_response
from sqlalchemy import func, select

from app import embeddings, retrieval
from app.config import settings
from app.models import Chunk, Document

BRUTE = "Password spraying tries one common password against many accounts to avoid lockout. " * 5
PHISH = "Phishing emails impersonate trusted senders and carry malicious attachments. " * 5


def upload(client, name, body):
    return client.post("/documents", files={"file": (name, body.encode(), "text/markdown")})


def answer_json(**kw):
    return json.dumps({"answer": "x", "sources": [], "confident": True} | kw)


# ------------------------------------------------------------------------ health

def test_health(client):
    assert client.get("/health").json() == {"status": "ok", "database": "ok"}


# --------------------------------------------------------------------- documents

def test_upload_stores_chunks_with_vectors(client, db):
    r = upload(client, "brute.md", BRUTE)
    assert r.status_code == 201
    assert r.json() == {"document_id": 1, "filename": "brute.md", "chunk_count": 1}
    chunk = db.scalars(select(Chunk)).one()
    assert len(chunk.embedding) == settings.embedding_dim


def test_upload_rejects_wrong_type(client):
    assert upload(client, "file.pdf", "x").status_code == 400


def test_upload_rejects_empty_file(client):
    assert upload(client, "empty.md", "   ").status_code == 400


def test_upload_rejects_non_utf8(client):
    r = client.post("/documents", files={"file": ("bad.txt", b"\xff\xfe\x00", "text/plain")})
    assert r.status_code == 400


def test_upload_rejects_large_file(client):
    assert upload(client, "big.txt", "a" * 1_000_001).status_code == 413


def test_embedding_failure_stores_nothing(client, db, monkeypatch):
    def boom(chunks, title):
        raise RuntimeError("quota exceeded")

    monkeypatch.setattr(embeddings, "embed_documents", boom)
    r = upload(client, "brute.md", BRUTE)
    assert r.status_code == 502
    assert db.scalar(select(func.count()).select_from(Document)) == 0


# ------------------------------------------------------------------------ search

def test_search_ranks_closest_chunk_first(client, db):
    upload(client, "brute.md", BRUTE)
    upload(client, "phish.md", PHISH)
    results = retrieval.search(db, fake_vector("password spraying lockout"), k=5)
    assert [r.filename for r in results] == ["brute.md", "phish.md"]
    assert results[0].distance < results[1].distance


# --------------------------------------------------------------------------- ask

def test_ask_answers_with_sources(client, fake_llm):
    upload(client, "brute.md", BRUTE)
    fake_llm.script = [text_response("DONE"), text_response(answer_json(answer="Spraying", sources=[1]))]
    r = client.post("/ask", json={"question": "What is password spraying and lockout?"})
    assert r.status_code == 200
    assert r.json() == {"answer": "Spraying", "sources": [1], "confident": True}


def test_ask_returns_not_found_without_calling_llm(client, fake_llm):
    upload(client, "brute.md", BRUTE)
    r = client.post("/ask", json={"question": "banana bread recipe"})
    assert r.json()["confident"] is False
    assert r.json()["sources"] == []
    assert fake_llm.requests == []  # the relevance gate saved the LLM call


def test_ask_with_technique_id_uses_tool_even_if_no_chunk_is_close(client, fake_llm):
    fake_llm.script = [
        call_response(("get_technique", {"technique_id": "T1003"})),
        text_response("DONE"),
        text_response(answer_json(answer="OS Credential Dumping")),
    ]
    r = client.post("/ask", json={"question": "What is T1003?"})
    assert r.json()["answer"] == "OS Credential Dumping"
    final_prompt = fake_llm.requests[2].contents
    assert "OS Credential Dumping" in final_prompt  # the tool result reached the prompt
    assert "<chunk" not in final_prompt


def test_ask_returns_502_when_llm_output_is_invalid_twice(client, fake_llm):
    upload(client, "brute.md", BRUTE)
    fake_llm.script = [text_response("DONE"), text_response("bad"), text_response("still bad")]
    r = client.post("/ask", json={"question": "What is password spraying and lockout?"})
    assert r.status_code == 502


def test_ask_validates_question(client):
    assert client.post("/ask", json={"question": "hi"}).status_code == 422
