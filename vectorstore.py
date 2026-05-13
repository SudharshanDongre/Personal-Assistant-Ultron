import os
import pickle
from typing import List, Dict, Optional, Any

import numpy as np


class VectorStore:
    """Lightweight VectorStore wrapper.

    - Uses `sentence-transformers` for embeddings when available.
    - Stores entries in an in-memory per-user namespace and can save/load via pickle.

    Methods:
      - index(documents, user_id, metadata)
      - search(query, user_id, top_k)
      - delete(doc_ids, user_id)
      - save(path)
      - load(path)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.embed_model = None
        try:
            from sentence_transformers import SentenceTransformer

            self.embed_model = SentenceTransformer(model_name)
        except Exception:
            # Defer raising until embedding is actually requested so the module
            # is import-friendly even when sentence-transformers isn't installed.
            self.embed_model = None

        # db: user_id -> list of entries
        # entry: {"doc_id", "text", "metadata", "embedding" (np.ndarray)}
        self.db: Dict[str, List[Dict[str, Any]]] = {}
        self._next_id = 1

    def _require_embedding_model(self) -> None:
        if self.embed_model is None:
            raise ImportError(
                "sentence-transformers is required for embeddings. "
                "Install with: pip install sentence-transformers"
            )

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        self._require_embedding_model()
        embs = self.embed_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return np.asarray(embs)

    def index(self, documents: List[Any], user_id: str = "default", metadata: Optional[Dict] = None) -> List[str]:
        """Index a list of documents.

        documents may be a list of strings or a list of dicts with keys `text` and optional `metadata`.
        Returns list of created `doc_id`s.
        """
        if not documents:
            return []

        texts: List[str] = []
        doc_metadatas: List[Optional[Dict]] = []
        for d in documents:
            if isinstance(d, str):
                texts.append(d)
                doc_metadatas.append(metadata)
            elif isinstance(d, dict) and "text" in d:
                texts.append(d["text"])
                # merge provided metadata with per-document metadata
                merged = dict(metadata or {})
                if "metadata" in d and isinstance(d["metadata"], dict):
                    merged.update(d["metadata"])
                doc_metadatas.append(merged)
            else:
                raise ValueError("Each document must be a string or a dict with a 'text' key")

        embs = self._embed_texts(texts)

        user_list = self.db.setdefault(user_id, [])
        created_ids: List[str] = []
        for i, text in enumerate(texts):
            doc_id = f"doc_{self._next_id:06d}"
            self._next_id += 1
            entry = {
                "doc_id": doc_id,
                "text": text,
                "metadata": doc_metadatas[i],
                "embedding": embs[i],
            }
            user_list.append(entry)
            created_ids.append(doc_id)

        return created_ids

    def search(self, query: str, user_id: str = "default", top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents in the given user's namespace.

        Returns list of results: {doc_id, text, metadata, score}
        Score is cosine similarity in [0, 1].
        """
        if user_id not in self.db or not self.db[user_id]:
            return []

        q_emb = self._embed_texts([query])[0]
        user_entries = self.db[user_id]
        matrix = np.vstack([e["embedding"] for e in user_entries])

        # cosine similarity
        q_norm = np.linalg.norm(q_emb)
        mat_norms = np.linalg.norm(matrix, axis=1)
        # avoid div by zero
        denom = (mat_norms * (q_norm + 1e-12))
        sims = (matrix @ q_emb) / (denom + 1e-12)

        # Clip to [-1,1], then map to 0..1
        sims = np.clip(sims, -1.0, 1.0)

        ranked_idx = np.argsort(-sims)[:top_k]
        results: List[Dict[str, Any]] = []
        for idx in ranked_idx:
            results.append(
                {
                    "doc_id": user_entries[idx]["doc_id"],
                    "text": user_entries[idx]["text"],
                    "metadata": user_entries[idx]["metadata"],
                    "score": float(sims[idx]),
                }
            )

        return results

    def delete(self, doc_ids: List[str], user_id: str = "default") -> int:
        """Delete documents by id from a user's namespace. Returns number deleted."""
        if user_id not in self.db:
            return 0
        before = len(self.db[user_id])
        self.db[user_id] = [e for e in self.db[user_id] if e["doc_id"] not in set(doc_ids)]
        after = len(self.db[user_id])
        return before - after

    def save(self, path: str) -> None:
        """Persist the entire vector DB to disk (pickle)."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"db": self.db, "next_id": self._next_id}, f)

    def load(self, path: str) -> None:
        """Load the vector DB from disk (pickle)."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"No vectorstore file at: {path}")
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.db = data.get("db", {})
        self._next_id = data.get("next_id", 1)

    def list_documents(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Return shallow info about documents for a user."""
        return [
            {"doc_id": e["doc_id"], "metadata": e["metadata"], "text_preview": e["text"][:200]}
            for e in self.db.get(user_id, [])
        ]


__all__ = ["VectorStore"]
