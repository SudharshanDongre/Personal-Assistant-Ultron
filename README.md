# Ultron Voice Assistant

Ultron is a Python-based voice assistant that has evolved from a command runner into a personalized multi-user assistant with retrieval-augmented memory. It still handles the original web, music, and utility commands, but now it can also learn preferences, store knowledge, and switch between user profiles.

## Current Progress

The project is currently at Phase 5 and the implemented pieces are:

- Voice input and speech output through `SpeechRecognition` and `pyttsx3`
- Web browsing, Google search, YouTube search, Wikipedia lookup, jokes, time, and date commands
- Music playback from the local `musiclibrary.py` mapping
- RAG-style knowledge storage and retrieval through `ingest.py`, `vectorstore.py`, and `retriever.py`
- Word-based text chunking and preprocessing in `embeddings.py`
- Multi-user personalization in `users.py` with per-user folders under `user_data/`
- Profile learning commands such as name, preferences, and knowledge snippets

## What Ultron Can Do

### Core Assistant Commands

- Open Google, YouTube, LinkedIn, Canva, and the GitHub profile link
- Search the web with Google
- Search and open YouTube results
- Play songs from the local music library
- Tell jokes
- Report the current time and date
- Respond to simple conversational prompts like greetings and identity questions

### Personalized Knowledge Commands

- `my name is ...` to save the current user name
- `i like ...` to save a preference
- `i prefer ...` to save work-style or response preferences
- `learn my preferences` to capture a spoken preference statement
- `add to my knowledge ...` to store a custom knowledge snippet
- `search my docs for ...` to search indexed user knowledge
- `what do you know about me` to summarize the saved profile and indexed knowledge
- `switch user to ...` to move to another user profile
- `forget ...` to remove matching knowledge items

## Project Structure

```text
main.py             # Entry point and command routing
commands.py         # RAG command handling and context formatting
users.py            # Multi-user profile management
ingest.py           # Document and knowledge ingestion helpers
retriever.py        # Retrieval helpers for user-specific context
vectorstore.py      # Lightweight per-user vector store
embeddings.py       # Text preprocessing and chunking helpers
musiclibrary.py     # Local song name to YouTube link mapping
voices.py           # Voice configuration helpers
requirements.txt    # Python dependencies
user_data/          # Per-user preferences, documents, and saved knowledge
```

## Data Layout

Each user gets a dedicated folder under `user_data/`.

```text
user_data/
  default/
    preferences.json
    documents/
  developer/
    preferences.json
    documents/
  one/
    preferences.json
    documents/
```

The assistant stores profile preferences in `preferences.json` and can also persist vector-store data per user when knowledge is indexed.

## Installation

1. Open the project folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Dependency Notes

- `SpeechRecognition` is required for microphone input
- `pyttsx3` is used for text-to-speech
- `wikipedia`, `pyjokes`, `yt-dlp`, and `pygame` support the assistant commands
- `sentence-transformers` is used for embeddings in the vector store
- `faiss-cpu`, `chromadb`, and `langchain` are available for RAG-related work
- `google-generative-ai` is still commented out in the requirements and is not yet part of the active flow

## Usage

Run the assistant with:

```bash
python main.py
```

After launch, Ultron listens for commands and speaks responses aloud. The current behavior is centered in `main.py`, which first tries to handle RAG commands and then falls back to the original assistant actions.

## Development Notes

- `main.py` now uses the `users` module for centralized user switching and profile lookup
- `commands.py` persists small profile updates and supports retrieval-aware replies
- `vectorstore.py` keeps documents separated by `user_id`
- `ingest.py` can load text and PDF documents and turn them into indexed chunks
- `embeddings.py` currently uses word-based chunking with overlap

## Future Work

- Add weather, email, calendar, and file-management commands
- Wire in Google Gemini responses if that becomes part of the active design
- Expand the music library and command coverage
- Improve search and retrieval ranking for larger knowledge sets

## Troubleshooting

- Make sure the microphone is available and permitted by the OS
- Install dependencies before running the assistant
- If embeddings or document search fail, check that the RAG packages were installed successfully

## License

Use and modify freely for personal learning and automation.

