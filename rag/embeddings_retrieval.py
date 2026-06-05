"""Embedding-based retrieval over the SDR tutor knowledge base (ChromaDB).

Sibling to ``rag/retrieval.py`` (BM25 over the same KB). The two coexist:

- ``retrieval.py``    — used by the chain skills (machine-generated queries,
                        lexical, deterministic, offline, no API key).
- ``embeddings_retrieval.py`` — used by the AI Tutor (free-form human questions
                        that need semantic match, plus a write-back path
                        for approved Q&A so the loop closes).

The chain does NOT migrate to embeddings; both retrievers index the same
``rag/knowledge_base/*.md`` docs but with different mechanics.

Usage::

    from rag.embeddings_retrieval import ensure_index, retrieve, add_approved_qa

    ensure_index()                                  # builds index on first call
    chunks = retrieve("how do I handle price objections", top_k=5)
    add_approved_qa("Q text", "A text")             # write approved Q&A back
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

REPO_ROOT = Path(__file__).resolve().parent.parent
KB_DIR = REPO_ROOT / "rag" / "knowledge_base"
DEFAULT_PERSIST_DIR = REPO_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "sdr_tutor_kb"
CHUNK_SIZE_WORDS = 300
CHUNK_OVERLAP_WORDS = 40
LOW_CONFIDENCE_THRESHOLD = 0.40  # cosine similarity below this → flagged


@dataclass
class EmbedChunk:
    """A chunk returned by ``retrieve()``.

    ``score`` is cosine similarity in [0, 1] — higher is more relevant.
    (ChromaDB returns cosine *distance*; we convert to similarity = 1 - distance.)
    """

    doc_name: str
    chunk_id: str
    passage: str
    score: float


def _strip_frontmatter(text: str) -> str:
    """Drop a leading YAML frontmatter block delimited by ``---`` lines."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :].lstrip("\n")


def _chunk_words(text: str, size: int, overlap: int) -> list[str]:
    """Split text into ~size-word chunks with given overlap.

    Word-based fixed-window chunking (not paragraph-based) so semantic
    retrieval sees consistent-length contexts.
    """
    words = text.split()
    if not words:
        return []
    if len(words) <= size:
        return [" ".join(words)]
    chunks: list[str] = []
    step = max(1, size - overlap)
    for start in range(0, len(words), step):
        window = words[start : start + size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + size >= len(words):
            break
    return chunks


_COLLECTION_CACHE: dict[str, "chromadb.api.models.Collection.Collection"] = {}


def get_collection(persist_dir: str | Path | None = None):
    """Lazy-init the ChromaDB collection. Cached per persist path."""
    persist = Path(persist_dir or DEFAULT_PERSIST_DIR)
    persist.mkdir(parents=True, exist_ok=True)
    key = str(persist.resolve())
    if key not in _COLLECTION_CACHE:
        client = chromadb.PersistentClient(path=str(persist))
        embedder = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedder,
            metadata={"hnsw:space": "cosine"},
        )
        _COLLECTION_CACHE[key] = collection
    return _COLLECTION_CACHE[key]


def build_index(
    kb_dir: str | Path | None = None,
    persist_dir: str | Path | None = None,
) -> int:
    """Index every ``.md`` in ``kb_dir`` (except README) into ChromaDB.

    Returns the number of chunks upserted.
    """
    kb = Path(kb_dir or KB_DIR)
    collection = get_collection(persist_dir)

    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict] = []
    for md_path in sorted(kb.glob("*.md")):
        if md_path.name.lower() == "readme.md":
            continue
        text = _strip_frontmatter(md_path.read_text(encoding="utf-8"))
        chunks = _chunk_words(text, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS)
        for i, chunk in enumerate(chunks):
            ids.append(f"{md_path.name}::{i}")
            docs.append(chunk)
            metas.append({"doc_name": md_path.name, "chunk_index": i, "source": "kb"})

    if ids:
        collection.upsert(ids=ids, documents=docs, metadatas=metas)
    return len(ids)


def ensure_index(
    kb_dir: str | Path | None = None,
    persist_dir: str | Path | None = None,
) -> int:
    """Build the index only if the collection is empty. Returns current chunk count."""
    collection = get_collection(persist_dir)
    if collection.count() == 0:
        return build_index(kb_dir, persist_dir)
    return collection.count()


def index_new_docs(
    kb_dir: str | Path | None = None,
    persist_dir: str | Path | None = None,
) -> int:
    """Idempotent: index any KB doc whose doc_name is not already in the collection.

    Preserves existing original-KB and approved_qa chunks. Safe to call on every
    backend boot. Returns the number of new chunks upserted (0 if nothing new).

    Unlike ``ensure_index``, this method scans the KB directory and only inserts
    docs whose ``doc_name`` doesn't appear in the collection's metadata yet —
    so newly-added .md files surface to the Tutor's ChromaDB without losing
    history written back via /tutor/approve.
    """
    kb = Path(kb_dir or KB_DIR)
    collection = get_collection(persist_dir)

    added = 0
    for md_path in sorted(kb.rglob("*.md")):
        if md_path.name.lower() == "readme.md":
            continue
        doc_name = md_path.name
        existing = collection.get(where={"doc_name": doc_name}, limit=1)
        if existing.get("ids"):
            continue
        text = _strip_frontmatter(md_path.read_text(encoding="utf-8"))
        chunks = _chunk_words(text, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS)
        if not chunks:
            continue
        ids = [f"{doc_name}::{i}" for i in range(len(chunks))]
        metadatas = [
            {"doc_name": doc_name, "chunk_index": i, "source": "kb"}
            for i in range(len(chunks))
        ]
        collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
        added += len(chunks)
    return added


def retrieve(
    query: str,
    top_k: int = 5,
    persist_dir: str | Path | None = None,
) -> list[EmbedChunk]:
    """Embed ``query`` and return the top-k chunks with cosine similarity scores."""
    collection = get_collection(persist_dir)
    if collection.count() == 0:
        return []

    result = collection.query(query_texts=[query], n_results=top_k)
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    chunks: list[EmbedChunk] = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        similarity = max(0.0, 1.0 - float(dist))
        chunks.append(
            EmbedChunk(
                doc_name=str((meta or {}).get("doc_name", "?")),
                chunk_id=str((meta or {}).get("chunk_index", "?")),
                passage=doc,
                score=similarity,
            )
        )
    return chunks


def add_approved_qa(
    question: str,
    answer: str,
    persist_dir: str | Path | None = None,
) -> str:
    """Write an approved Q&A pair back to the KB as a new chunk.

    Metadata sets ``source="approved_qa"`` so dashboards can distinguish
    human-validated content from original KB docs.
    """
    collection = get_collection(persist_dir)
    qa_id = f"approved_qa::{uuid.uuid4().hex[:12]}"
    body = f"Q: {question}\n\nA: {answer}"
    collection.upsert(
        ids=[qa_id],
        documents=[body],
        metadatas=[{"doc_name": "approved_qa", "chunk_index": qa_id, "source": "approved_qa"}],
    )
    return qa_id


def build_sources(chunks: list[EmbedChunk]) -> list[dict]:
    """Serialize embedding ``EmbedChunk`` objects into the envelope-output shape.

    Returns a list of ``{doc_name, passage, score, weak}`` dicts. ``weak`` uses
    the **calibrated** cosine threshold ``LOW_CONFIDENCE_THRESHOLD`` (0.40) —
    embeddings live in a bounded [0, 1] space so absolute thresholds work,
    unlike BM25 which uses a relative-to-max rule in ``rag/retrieval.py``.

    Both retrieval modules emit the same dict shape so the UI's EvidencePanel
    can render both without knowing which retriever produced them.
    """
    return [
        {
            "doc_name": c.doc_name,
            "passage": c.passage,
            "score": round(float(c.score), 4),
            "weak": c.score < LOW_CONFIDENCE_THRESHOLD,
        }
        for c in chunks
    ]


def collection_size(persist_dir: str | Path | None = None) -> int:
    """Return the current chunk count in the collection."""
    return get_collection(persist_dir).count()


def reset_collection_cache() -> None:
    """Clear the module-level collection cache (used by tests with tmp paths)."""
    _COLLECTION_CACHE.clear()
