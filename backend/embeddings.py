from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_CHROMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma_db"
)
_COLLECTION_NAME = "sdr_kb"

_client: chromadb.PersistentClient | None = None
_collection: chromadb.Collection | None = None


def _get_collection() -> chromadb.Collection:
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=_CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name=_COLLECTION_NAME,
            embedding_function=DefaultEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ---------------------------------------------------------------------------
# Core ingest
# ---------------------------------------------------------------------------


def add_documents(
    texts: list[str],
    ids: list[str],
    source: str,
    doc_type: str,
    extra_metadata: dict | None = None,
) -> None:
    """Add raw text chunks with provenance metadata."""
    now = datetime.now(timezone.utc).isoformat()
    metadatas = [
        {
            "source": source,
            "type": doc_type,
            "timestamp": now,
            **(extra_metadata or {}),
        }
        for _ in texts
    ]
    _get_collection().upsert(documents=texts, ids=ids, metadatas=metadatas)


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


def query(text: str, k: int = 5) -> list[dict]:
    """Return top-k chunks with content and source metadata."""
    results = _get_collection().query(
        query_texts=[text],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "content": doc,
                "source": meta.get("source", "unknown"),
                "type": meta.get("type", "unknown"),
                "timestamp": meta.get("timestamp", ""),
                "score": round(1 - dist, 4),  # cosine similarity
            }
        )
    return chunks


# ---------------------------------------------------------------------------
# KB write-back: approved Q&A pairs
# ---------------------------------------------------------------------------


def add_qa_pair(
    question: str,
    answer: str,
    pair_id: str,
    source: str = "approved_qa",
) -> None:
    """Write an approved Q&A pair into the KB as a combined chunk."""
    text = f"Q: {question}\nA: {answer}"
    add_documents(
        texts=[text],
        ids=[pair_id],
        source=source,
        doc_type="qa_pair",
    )


# ---------------------------------------------------------------------------
# KB write-back: coaching notes
# ---------------------------------------------------------------------------


def add_coaching_note(
    note: str,
    note_id: str,
    coach: str = "unknown",
    topic: str = "",
) -> None:
    """Store an approved coaching note as a gold-standard example."""
    add_documents(
        texts=[note],
        ids=[note_id],
        source="coaching",
        doc_type="coaching_note",
        extra_metadata={"coach": coach, "topic": topic},
    )


# ---------------------------------------------------------------------------
# KB write-back: handoff docs from offboarding
# ---------------------------------------------------------------------------


def add_handoff_doc(
    content: str,
    doc_id: str,
    departing_rep: str = "unknown",
    territory: str = "",
) -> None:
    """Store an approved handoff document from an offboarding SDR."""
    add_documents(
        texts=[content],
        ids=[doc_id],
        source="handoff",
        doc_type="handoff_doc",
        extra_metadata={
            "departing_rep": departing_rep,
            "territory": territory,
        },
    )
