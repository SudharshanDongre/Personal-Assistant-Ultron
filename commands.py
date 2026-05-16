"""RAG command helpers for Ultron voice assistant."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

from ingest import add_user_knowledge, load_user_preferences


PROJECT_ROOT = Path(__file__).resolve().parent
USER_DATA_ROOT = PROJECT_ROOT / "user_data"


def _save_user_preferences(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
	"""Persist small profile updates into user_data/<user_id>/preferences.json."""
	user_dir = USER_DATA_ROOT / user_id
	user_dir.mkdir(parents=True, exist_ok=True)
	path = user_dir / "preferences.json"

	existing: Dict[str, Any] = {"user_id": user_id}
	if path.exists():
		try:
			existing = json.loads(path.read_text(encoding="utf-8"))
			if not isinstance(existing, dict):
				existing = {"user_id": user_id}
		except Exception:
			existing = {"user_id": user_id}

	existing.update(updates)
	existing.setdefault("user_id", user_id)
	path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
	return existing


def _parse_profile_statement(command_text: str) -> Dict[str, str]:
	"""Parse simple self-profile statements from natural speech."""
	raw = command_text.strip()
	lower = raw.lower().strip(" .!?")

	if lower.startswith("my name is "):
		name = raw[len("my name is ") :].strip(" .!?,")
		if name:
			return {
				"category": "identity",
				"knowledge": f"User name is {name}.",
				"pref_key": "username",
				"pref_value": name,
				"ack": f"Got it, I will remember your name as {name}.",
			}

	if lower.startswith("i prefer "):
		preference = raw[len("i prefer ") :].strip(" .!?,")
		if preference:
			return {
				"category": "preference",
				"knowledge": f"User preference: {preference}.",
				"pref_key": "work_style",
				"pref_value": preference,
				"ack": "Understood. I have saved that preference.",
			}

	if lower.startswith("i like "):
		like_text = raw[len("i like ") :].strip(" .!?,")
		if like_text:
			return {
				"category": "preference",
				"knowledge": f"User likes {like_text}.",
				"pref_key": "likes",
				"pref_value": like_text,
				"ack": "Noted. I have added that to your profile.",
			}

	return {}


def format_response_with_context(rag_context: Iterable[Dict[str, Any]]) -> str:
	"""Build a short response prefix from retrieved context."""
	items = list(rag_context or [])
	if not items:
		return "I do not have personalized context for that yet"

	top = items[0]
	top_text = str(top.get("text", "")).strip()
	if not top_text:
		return "From what I have learned about you"

	preview = top_text[:140].rstrip()
	if len(top_text) > 140:
		preview += "..."
	return f"Based on your saved context: {preview}"


def _extract_phrase(command_text: str, trigger: str) -> str:
	start = command_text.lower().find(trigger)
	if start < 0:
		return ""
	return command_text[start + len(trigger) :].strip(" :,-")


def _normalize_for_matching(text: str) -> str:
	"""Lowercase and strip punctuation to make speech matches more tolerant."""
	cleaned = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text)
	return " ".join(cleaned.split())


def _is_name_query(normalized_text: str) -> bool:
	"""Recognize natural variants like 'what ise my name'."""
	if "my name" not in normalized_text:
		return False
	if "what" in normalized_text:
		return True
	if "tell" in normalized_text and "name" in normalized_text:
		return True
	return False


def _is_knowledge_query(normalized_text: str) -> bool:
	"""Recognize variants of 'what do you know about me'."""
	if "know" not in normalized_text:
		return False
	if "about me" in normalized_text:
		return True
	if "what do you know about" in normalized_text:
		return True
	if "what you know" in normalized_text and "about" in normalized_text:
		return True
	return False


def _speak_retrieval_results(
	results: List[Dict[str, Any]],
	speak: Callable[[str], None],
) -> None:
	if not results:
		speak("I could not find relevant notes in your knowledge base.")
		return

	speak(f"I found {len(results)} relevant result{'s' if len(results) > 1 else ''}.")
	for index, item in enumerate(results[:3], start=1):
		text = str(item.get("text", "")).strip()
		if not text:
			continue
		preview = text[:180].rstrip()
		if len(text) > 180:
			preview += "..."
		speak(f"Result {index}: {preview}")


def handle_rag_commands(
	command_text: str,
	current_user: str,
	retriever: Any,
	vector_store: Any,
	speak: Callable[[str], None],
	listen_to_command: Callable[[], str],
	switch_user: Callable[[str], bool],
) -> bool:
	"""Handle Phase 4 RAG-specific commands.

	Returns True if the command was handled here, otherwise False.
	"""
	c = command_text.lower()
	normalized = _normalize_for_matching(command_text)
	profile_fact = _parse_profile_statement(command_text)
	if profile_fact:
		add_user_knowledge(
			current_user,
			profile_fact["knowledge"],
			category=profile_fact["category"],
			vector_store=vector_store,
		)
		_save_user_preferences(
			current_user,
			{profile_fact["pref_key"]: profile_fact["pref_value"]},
		)
		speak(profile_fact["ack"])
		return True

	if _is_name_query(normalized):
		prefs = load_user_preferences(current_user)
		name = str(prefs.get("username", "")).strip()
		if name:
			speak(f"Your name is {name}.")
		else:
			speak("I do not have your name yet. You can say: my name is Sudarshan.")
		return True

	if "learn my preferences" in c:
		speak("Sure Sir, what would you like me to learn?")
		new_pref = listen_to_command().strip()
		if not new_pref:
			speak("I did not catch that. Please try again.")
			return True

		add_user_knowledge(current_user, new_pref, category="preference", vector_store=vector_store)
		speak("Got it, I have saved that to your profile.")
		return True

	if "add to my knowledge" in c:
		payload = _extract_phrase(command_text, "add to my knowledge")
		if not payload:
			speak("What should I add to your knowledge base?")
			payload = listen_to_command().strip()

		if not payload:
			speak("No content received, so I did not add anything.")
			return True

		add_user_knowledge(current_user, payload, category="knowledge", vector_store=vector_store)
		speak("Done. I have added that to your knowledge base.")
		return True

	if "search my docs for" in c:
		query = _extract_phrase(command_text, "search my docs for")
		if not query:
			speak("Please tell me what you want to search in your docs.")
			return True

		results = retriever.retrieve(query, user_id=current_user, top_k=3, threshold=0.3)
		_speak_retrieval_results(results, speak)
		return True

	if c.startswith("forget "):
		topic = _extract_phrase(command_text, "forget")
		if not topic:
			speak("Please tell me what topic you want me to forget.")
			return True

		documents = vector_store.list_documents(current_user)
		topic_lower = topic.lower()
		delete_ids: List[str] = []
		for item in documents:
			preview = str(item.get("text_preview", "")).lower()
			metadata = dict(item.get("metadata") or {})
			category = str(metadata.get("category", "")).lower()
			source = str(metadata.get("source", "")).lower()
			if topic_lower in preview or topic_lower in category or topic_lower in source:
				doc_id = item.get("doc_id")
				if doc_id:
					delete_ids.append(doc_id)

		if not delete_ids:
			speak("I could not find matching entries to forget.")
			return True

		deleted = vector_store.delete(delete_ids, user_id=current_user)
		speak(f"Done. I removed {deleted} knowledge item{'s' if deleted != 1 else ''}.")
		return True

	if "what do you know about me" in c or _is_knowledge_query(normalized):
		prefs = load_user_preferences(current_user)
		docs = vector_store.list_documents(current_user)

		summary_keys = [
			"username",
			"response_style",
			"work_style",
			"programming_languages",
			"projects",
		]
		parts: List[str] = []
		for key in summary_keys:
			value = prefs.get(key)
			if value:
				parts.append(f"{key.replace('_', ' ')}: {value}")

		if parts:
			speak("Here is what I currently know: " + "; ".join(parts))
		else:
			speak("I have not learned your detailed preferences yet.")

		speak(f"I currently have {len(docs)} indexed knowledge chunk{'s' if len(docs) != 1 else ''} for you.")
		return True

	if "switch user to" in c:
		new_user = _extract_phrase(command_text, "switch user to")
		if not new_user:
			speak("Please provide a user id to switch to.")
			return True

		if switch_user(new_user):
			speak(f"Switched to user {new_user}.")
		else:
			speak("I could not switch user at the moment.")
		return True

	return False


__all__ = ["format_response_with_context", "handle_rag_commands"]
