"""Retrieval helpers for user-specific context lookups."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional


class Retriever:
    """Small wrapper around a vector store with retrieval helpers."""

    def __init__(self, vector_store: Any) -> None:
        if vector_store is None:
            raise ValueError("vector_store must not be None")
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        user_id: str = "default",
        top_k: int = 3,
        threshold: float = 0.6,
    ) -> List[Dict[str, Any]]:
        """Return relevant results above the similarity threshold."""
        if not query or not str(query).strip():
            return []

        results = self.vector_store.search(query, user_id=user_id, top_k=top_k)
        filtered: List[Dict[str, Any]] = []
        for result in results:
            score = float(result.get("score", 0.0))
            if score >= threshold:
                filtered.append(result)
        return filtered

    @staticmethod
    def filter_by_metadata(results: Iterable[Mapping[str, Any]], filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter retrieval results by metadata fields."""
        if not filters:
            return [dict(result) for result in results]

        filtered: List[Dict[str, Any]] = []
        for result in results:
            metadata = dict(result.get("metadata") or {})
            include = True
            for key, expected in filters.items():
                actual = metadata.get(key)
                if isinstance(expected, (list, tuple, set, frozenset)):
                    if actual not in expected:
                        include = False
                        break
                elif actual != expected:
                    include = False
                    break
            if include:
                filtered.append(dict(result))
        return filtered

    @staticmethod
    def format_context(results: Iterable[Mapping[str, Any]]) -> str:
        """Format retrieval results into a prompt-ready context block."""
        items = list(results)
        if not items:
            return "No relevant knowledge found."

        lines = ["Based on your knowledge base:"]
        for index, result in enumerate(items, start=1):
            text = str(result.get("text", "")).strip()
            score = result.get("score")
            metadata = dict(result.get("metadata") or {})
            details: List[str] = []
            if metadata.get("category"):
                details.append(f"category: {metadata['category']}")
            if metadata.get("source"):
                details.append(f"source: {metadata['source']}")
            if metadata.get("document_name"):
                details.append(f"doc: {metadata['document_name']}")

            detail_text = f" ({', '.join(details)})" if details else ""
            score_text = f" [score: {score:.2f}]" if isinstance(score, (int, float)) else ""
            lines.append(f"{index}. {text}{score_text}{detail_text}")

        return "\n".join(lines)


__all__ = ["Retriever"]