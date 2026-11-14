import re

# Rule of thumb for English: 1 token is about 0.75 words (about 4 characters).
# We count words instead of calling a tokenizer, so chunking is free, fast and
# works offline. The trade-off: chunk sizes are approximate, not exact.
WORDS_PER_TOKEN = 0.75


def chunk_text(text: str, chunk_tokens: int = 500, overlap_tokens: int = 50) -> list[str]:
    """Split text into overlapping windows of roughly `chunk_tokens` tokens.

    Each window starts `chunk_tokens - overlap_tokens` tokens after the previous
    one, so the last ~50 tokens of one chunk are repeated at the start of the next.
    """
    size = int(chunk_tokens * WORDS_PER_TOKEN)      # 375 words
    overlap = int(overlap_tokens * WORDS_PER_TOKEN)  # 37 words
    step = size - overlap
    if step <= 0:
        raise ValueError("overlap must be smaller than chunk size")

    # Each "word" keeps the whitespace after it, so joining them back
    # preserves newlines and markdown structure.
    words = re.findall(r"\S+\s*", text)

    chunks = []
    for start in range(0, len(words), step):
        chunk = "".join(words[start : start + size]).strip()
        if chunk:
            chunks.append(chunk)
        if start + size >= len(words):  # this window reached the end
            break
    return chunks
