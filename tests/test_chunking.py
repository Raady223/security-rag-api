import pytest

from app.chunking import chunk_text


def words(n: int) -> str:
    return " ".join(f"w{i}" for i in range(n))


def test_short_text_is_one_chunk():
    assert chunk_text(words(100)) == [words(100)]


def test_chunks_are_about_500_tokens_with_overlap():
    chunks = chunk_text(words(1000))
    sizes = [len(c.split()) for c in chunks]
    assert sizes == [375, 375, 324]  # 375 words ~ 500 tokens
    # the last 37 words (~50 tokens) of one chunk start the next one
    assert chunks[0].split()[-37:] == chunks[1].split()[:37]


def test_every_word_is_kept():
    chunks = chunk_text(words(1000))
    seen = {w for c in chunks for w in c.split()}
    assert seen == set(words(1000).split())


def test_empty_text_gives_no_chunks():
    assert chunk_text("   \n\n ") == []


def test_newlines_and_markdown_are_preserved():
    assert chunk_text("# Title\n\n- item one\n- item two") == ["# Title\n\n- item one\n- item two"]


def test_overlap_must_be_smaller_than_chunk():
    with pytest.raises(ValueError):
        chunk_text("text", chunk_tokens=50, overlap_tokens=50)
