"""Text preprocessing and embedding helpers for RAG ingestion.

These helpers are intentionally lightweight so they can be reused by
ingestion, indexing, and testing code without pulling in the vector store.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, List, Sequence

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency fallback
    np = None


def preprocess_document(raw_text: str) -> str:
    """Clean and normalize raw document text.

    The normalization keeps the content readable while removing common noise
    that hurts chunking and embedding quality.
    """
    if raw_text is None:
        raise ValueError("raw_text must not be None")

    text = unicodedata.normalize("NFKC", str(raw_text))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping word-based chunks.

    Args:
        text: Input text to split.
        chunk_size: Approximate number of words per chunk.
        overlap: Number of trailing words to repeat in the next chunk.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must not be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    cleaned_text = preprocess_document(text)
    if not cleaned_text:
        return []

    words = cleaned_text.split()
    if len(words) <= chunk_size:
        return [cleaned_text]

    chunks: List[str] = []
    step = chunk_size - overlap
    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk_words = words[start:end]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break

    return chunks


def generate_embeddings(texts: Sequence[str] | Iterable[str], model) -> np.ndarray:
    """Convert texts to embeddings using a model with an ``encode`` method.

    The function accepts any model that exposes ``encode(texts, convert_to_numpy=True)``
    or a compatible callable returning array-like embeddings.
    """
    if texts is None:
        raise ValueError("texts must not be None")

    text_list = [preprocess_document(text) for text in list(texts)]
    if not text_list:
        if np is not None:
            return np.empty((0, 0), dtype=np.float32)
        return []

    if model is None:
        raise ValueError("model must not be None")

    if hasattr(model, "encode"):
        embeddings = model.encode(text_list, convert_to_numpy=True, show_progress_bar=False)
    else:
        embeddings = model(text_list)

    if np is not None:
        return np.asarray(embeddings)
    return embeddings


__all__ = ["chunk_text", "preprocess_document", "generate_embeddings"]