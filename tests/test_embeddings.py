from types import SimpleNamespace

from google.genai import types

from app import embeddings
from app.config import settings


class FakeEmbedClient:
    def __init__(self):
        self.calls = []
        self.models = self

    def embed_content(self, model, contents, config):
        self.calls.append(SimpleNamespace(contents=contents, config=config))
        return SimpleNamespace(embeddings=[SimpleNamespace(values=[0.1] * 3) for _ in contents])


def test_each_text_gets_its_own_content_and_prefix(monkeypatch):
    # Remove the autouse fake embedder so the real embed_documents runs (against a fake client).
    monkeypatch.undo()
    fake = FakeEmbedClient()
    monkeypatch.setattr(embeddings, "get_client", lambda: fake)

    vectors = embeddings.embed_documents(["first chunk", "second chunk"], title="doc")

    assert len(vectors) == 2  # one vector per chunk, not one merged vector
    sent = fake.calls[0].contents
    assert all(isinstance(c, types.Content) for c in sent)
    assert sent[0].parts[0].text == "title: doc | text: first chunk"
    assert fake.calls[0].config.output_dimensionality == settings.embedding_dim


def test_query_uses_query_prefix(monkeypatch):
    monkeypatch.undo()
    fake = FakeEmbedClient()
    monkeypatch.setattr(embeddings, "get_client", lambda: fake)

    embeddings.embed_query("what is T1110?")

    assert fake.calls[0].contents[0].parts[0].text == "task: question answering | query: what is T1110?"


def test_large_inputs_are_batched(monkeypatch):
    monkeypatch.undo()
    fake = FakeEmbedClient()
    monkeypatch.setattr(embeddings, "get_client", lambda: fake)

    vectors = embeddings.embed_documents([f"chunk {i}" for i in range(120)], title="big")

    assert len(vectors) == 120
    assert [len(c.contents) for c in fake.calls] == [50, 50, 20]
