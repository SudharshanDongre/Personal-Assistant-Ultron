"""Ingestion helpers for user documents and personalization data.

The functions in this module keep file-system concerns separate from the
vector store so they can be reused during setup, indexing, and testing.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from embeddings import chunk_text, preprocess_document


PROJECT_ROOT = Path(__file__).resolve().parent
USER_DATA_ROOT = PROJECT_ROOT / "user_data"
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}
SUPPORTED_FILE_EXTENSIONS = SUPPORTED_TEXT_EXTENSIONS | {".pdf"}


def _user_root(user_id: str, data_root: Path = USER_DATA_ROOT) -> Path:
    return data_root / user_id


def _ensure_user_structure(user_id: str, data_root: Path = USER_DATA_ROOT) -> Path:
    user_root = _user_root(user_id, data_root)
    (user_root / "documents").mkdir(parents=True, exist_ok=True)
    return user_root


def _read_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def _read_pdf_file(file_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        try:
            from PyPDF2 import PdfReader
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "Reading PDF files requires pypdf or PyPDF2. Install one of them to ingest PDFs."
            ) from exc

    reader = PdfReader(str(file_path))
    pages: List[str] = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        if extracted:
            pages.append(extracted)
    return "\n".join(pages)


def _load_document_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix in SUPPORTED_TEXT_EXTENSIONS:
        return _read_text_file(file_path)
    if suffix == ".pdf":
        return _read_pdf_file(file_path)
    raise ValueError(f"Unsupported file type for ingestion: {file_path.suffix}")


def _normalize_metadata(metadata: Optional[Dict[str, Any]] = None, **extra: Any) -> Dict[str, Any]:
    result = dict(metadata or {})
    for key, value in extra.items():
        if value is not None:
            result[key] = value
    return result


def load_user_preferences(user_id: str, data_root: Path | str = USER_DATA_ROOT) -> Dict[str, Any]:
    """Load a user's stored preferences if present.

    Returns an empty dictionary when the user has no saved preferences yet.
    """
    root = Path(data_root)
    preferences_path = root / user_id / "preferences.json"
    if not preferences_path.exists():
        return {"user_id": user_id}

    try:
        with preferences_path.open("r", encoding="utf-8") as handle:
            preferences = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {preferences_path}") from exc

    if not isinstance(preferences, dict):
        raise ValueError(f"Preferences file must contain a JSON object: {preferences_path}")

    preferences.setdefault("user_id", user_id)
    return preferences


def ingest_documents(
    file_path: str | os.PathLike[str],
    user_id: str,
    vector_store: Any | None = None,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 500,
    overlap: int = 50,
    data_root: Path | str = USER_DATA_ROOT,
) -> Dict[str, Any]:
    """Load a document, split it into chunks, and optionally index it.

    The returned payload includes the chunked text so callers can inspect or
    persist the result even when no vector store is provided.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    user_root = _ensure_user_structure(user_id, Path(data_root))
    raw_text = _load_document_text(path)
    cleaned_text = preprocess_document(raw_text)
    chunks = chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)

    doc_metadata = _normalize_metadata(
        metadata,
        user_id=user_id,
        source=path.name,
        file_path=str(path),
        file_type=path.suffix.lower().lstrip("."),
        document_name=path.stem,
    )

    indexed_ids: List[str] = []
    if vector_store is not None and chunks:
        documents = [
            {
                "text": chunk,
                "metadata": {
                    **doc_metadata,
                    "chunk_index": index,
                    "chunk_count": len(chunks),
                },
            }
            for index, chunk in enumerate(chunks)
        ]
        indexed_ids = vector_store.index(documents, user_id=user_id, metadata=doc_metadata)

    document_record = {
        "file_path": str(path),
        "user_id": user_id,
        "chunk_count": len(chunks),
        "chunks": chunks,
        "indexed_ids": indexed_ids,
        "metadata": doc_metadata,
    }

    documents_dir = user_root / "documents"
    documents_dir.mkdir(parents=True, exist_ok=True)
    return document_record


def add_user_knowledge(
    user_id: str,
    text: str,
    category: str,
    vector_store: Any | None = None,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 500,
    overlap: int = 50,
    data_root: Path | str = USER_DATA_ROOT,
) -> Dict[str, Any]:
    """Add a knowledge snippet to a user's namespace."""
    if not text or not str(text).strip():
        raise ValueError("text must not be empty")

    _ensure_user_structure(user_id, Path(data_root))
    cleaned_text = preprocess_document(text)
    chunks = chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        chunks = [cleaned_text]

    doc_metadata = _normalize_metadata(
        metadata,
        user_id=user_id,
        category=category,
        source="manual_input",
    )

    indexed_ids: List[str] = []
    if vector_store is not None:
        documents = [
            {
                "text": chunk,
                "metadata": {
                    **doc_metadata,
                    "chunk_index": index,
                    "chunk_count": len(chunks),
                },
            }
            for index, chunk in enumerate(chunks)
        ]
        indexed_ids = vector_store.index(documents, user_id=user_id, metadata=doc_metadata)

    return {
        "user_id": user_id,
        "category": category,
        "chunk_count": len(chunks),
        "chunks": chunks,
        "indexed_ids": indexed_ids,
        "metadata": doc_metadata,
    }


def parse_user_data(
    user_id: str = "default",
    data_root: Path | str = USER_DATA_ROOT,
    vector_store: Any | None = None,
) -> Dict[str, Any]:
    """Load a user's preferences and documents from the standard folder layout."""
    root = Path(data_root)
    user_root = _ensure_user_structure(user_id, root)

    preferences = load_user_preferences(user_id, root)
    documents: List[Dict[str, Any]] = []
    indexed_documents: List[Dict[str, Any]] = []

    candidates: List[Path] = []
    documents_dir = user_root / "documents"
    if documents_dir.exists():
        candidates.extend(sorted(path for path in documents_dir.rglob("*") if path.is_file()))

    for file_name in ("docs.txt", "learned_solutions.txt", "general_knowledge.txt"):
        candidate = user_root / file_name
        if candidate.exists():
            candidates.append(candidate)

    for file_path in candidates:
        if file_path.suffix.lower() not in SUPPORTED_FILE_EXTENSIONS:
            continue

        record = ingest_documents(
            file_path,
            user_id=user_id,
            vector_store=vector_store,
            metadata={"category": "document", "source_type": "user_file"},
            data_root=root,
        )
        documents.append(record)
        indexed_documents.append(
            {
                "file_path": record["file_path"],
                "chunk_count": record["chunk_count"],
                "indexed_ids": record["indexed_ids"],
            }
        )

    return {
        "user_id": user_id,
        "preferences": preferences,
        "documents": documents,
        "indexed_documents": indexed_documents,
    }


__all__ = [
    "USER_DATA_ROOT",
    "add_user_knowledge",
    "ingest_documents",
    "load_user_preferences",
    "parse_user_data",
]