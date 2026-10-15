"""
Nykaa Support Semantic RAG.

Loads Markdown/text policies, splits them into chunks, stores embeddings
in ChromaDB, and retrieves relevant passages for customer questions.

This module performs retrieval only. It does not call an LLM.

Run from the project root:
    python -m src.semantic_rag

Install dependencies:
    python -m pip install chromadb sentence-transformers
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, cast

import chromadb
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
CHROMA_DB_DIR = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "nykaa_support_knowledge"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_K = 3
MAX_TOP_K = 10

CHUNK_SIZE = 900
CHUNK_OVERLAP = 120

# ChromaDB L2 distance: smaller generally means more similar.
# Tune this threshold against your own test questions.
MAX_DISTANCE = 1.0


# ============================================================
# Logging and cached objects
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None
_client: Any = None
_collection: Any = None


# ============================================================
# Model and database
# ============================================================

def get_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""
    global _model

    if _model is None:
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return _model


def get_collection() -> Collection:
    """Create or reuse the persistent ChromaDB collection."""
    global _client, _collection

    if _collection is None:
        CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

        _client = chromadb.PersistentClient(
            path=str(CHROMA_DB_DIR)
        )

        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "Nykaa customer support knowledge base"
            },
        )

    # ChromaDB returns a Collection. cast() also makes the intended
    # type explicit to static type checkers.
    return cast(Collection, _collection)


# ============================================================
# Text chunking
# ============================================================

def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks near natural boundaries."""

    if not isinstance(text, str) or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    cleaned = re.sub(r"\r\n?", "\n", text).strip()
    chunks: list[str] = []
    start = 0

    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))

        if end < len(cleaned):
            boundaries = [
                cleaned.rfind("\n\n", start, end),
                cleaned.rfind("\n", start, end),
                cleaned.rfind(". ", start, end),
                cleaned.rfind("? ", start, end),
                cleaned.rfind("! ", start, end),
            ]

            boundary = max(boundaries)

            if boundary > start + chunk_size // 2:
                if cleaned[boundary:boundary + 2] == "\n\n":
                    end = boundary + 2
                else:
                    end = boundary + 1

        chunk = cleaned[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(cleaned):
            break

        start = max(end - overlap, start + 1)

    return chunks


# ============================================================
# Load knowledge-base documents
# ============================================================

def load_knowledge_documents() -> list[dict[str, str]]:
    """Load .md and .txt files recursively from knowledge_base/."""

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge-base folder not found: {KNOWLEDGE_BASE_DIR}. "
            "Create knowledge_base/ and add .md or .txt policy files."
        )

    paths = sorted(
        path
        for path in KNOWLEDGE_BASE_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".md", ".txt"}
    )

    documents: list[dict[str, str]] = []

    for path in paths:
        try:
            content = path.read_text(
                encoding="utf-8-sig"
            ).strip()
        except (OSError, UnicodeError) as exc:
            logger.warning("Skipping %s: %s", path.name, exc)
            continue

        if not content:
            logger.warning("Skipping empty document: %s", path.name)
            continue

        relative_name = path.relative_to(
            KNOWLEDGE_BASE_DIR
        ).as_posix()

        for index, chunk in enumerate(split_text(content)):
            documents.append(
                {
                    "id": f"{relative_name}::{index}",
                    "source": relative_name,
                    "content": chunk,
                }
            )

    return documents


# ============================================================
# Index documents
# ============================================================

def index_documents(force_rebuild: bool = False) -> int:
    """
    Index knowledge-base chunks in ChromaDB.

    Set force_rebuild=True to rebuild the index after changing policies.
    Returns the number of chunks in the index.
    """
    global _collection

    collection = get_collection()

    if force_rebuild:
        if _client is None:
            raise RuntimeError("ChromaDB client is not initialized.")

        try:
            _client.delete_collection(name=COLLECTION_NAME)
        except Exception as exc:
            logger.debug("Could not delete old collection: %s", exc)

        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "Nykaa customer support knowledge base"
            },
        )

        collection = get_collection()

    elif collection.count() > 0:
        logger.info(
            "Knowledge collection already contains %s chunks; "
            "skipping indexing.",
            collection.count(),
        )
        return int(collection.count())

    documents = load_knowledge_documents()

    if not documents:
        logger.warning(
            "No usable .md or .txt documents found in %s",
            KNOWLEDGE_BASE_DIR,
        )
        return 0

    model = get_model()
    batch_size = 100

    for start in range(0, len(documents), batch_size):
        batch = documents[start:start + batch_size]

        embeddings = model.encode(
            [item["content"] for item in batch],
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        # Use upsert so rerunning indexing does not fail on duplicate IDs.
        collection.upsert(
            ids=[item["id"] for item in batch],
            documents=[item["content"] for item in batch],
            metadatas=[
                {"source": item["source"]}
                for item in batch
            ],
            embeddings=embeddings,
        )

    total = int(collection.count())

    logger.info(
        "Indexing complete. Chunks in collection: %s",
        total,
    )

    return total


# ============================================================
# Semantic search
# ============================================================

def search_knowledge(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict[str, Any]]:
    """Return ranked passages with source filenames and distances."""

    if not isinstance(question, str) or not question.strip():
        return []

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or top_k < 1
    ):
        raise ValueError("top_k must be a positive integer.")

    top_k = min(top_k, MAX_TOP_K)
    collection = get_collection()

    if collection.count() == 0:
        index_documents()
        collection = get_collection()

    count = int(collection.count())

    if count == 0:
        return []

    query_embedding = get_model().encode(
        [question.strip()],
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()

    result = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    documents = (result.get("documents") or [[]])[0] or []
    metadatas = (result.get("metadatas") or [[]])[0] or []
    distances = (result.get("distances") or [[]])[0] or []

    matches: list[dict[str, Any]] = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        if not document:
            continue

        try:
            numeric_distance = float(distance)
        except (TypeError, ValueError):
            numeric_distance = float("inf")

        metadata_dict = metadata or {}

        matches.append(
            {
                "source": metadata_dict.get("source", "unknown"),
                "content": str(document),
                "distance": round(numeric_distance, 4),
            }
        )

    return matches


# ============================================================
# Build a grounded response
# ============================================================
def answer_question(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    max_distance: float = MAX_DISTANCE,
) -> str:
    """Return a concise, topic-focused answer grounded in policy documents."""

    if not isinstance(question, str) or not question.strip():
        return "Please enter a valid question."

    if (
        not isinstance(max_distance, (int, float))
        or isinstance(max_distance, bool)
        or max_distance < 0
    ):
        raise ValueError("max_distance must be a non-negative number.")

    query = question.strip().lower()

    # Identify the customer's primary topic.
    topic_configs = {
        "return": {
            "query_terms": ("return", "returns", "exchange"),
            "source_terms": ("return", "exchange"),
            "content_terms": (
                "return",
                "returns",
                "exchange",
                "unused",
                "original packaging",
                "delivery",
            ),
        },
        "refund": {
            "query_terms": ("refund", "refunds", "money back"),
            "source_terms": ("refund", "cod"),
            "content_terms": (
                "refund",
                "refunds",
                "money back",
                "inspection",
                "eligible",
            ),
        },
        "delivery": {
            "query_terms": (
                "delivery",
                "shipping",
                "shipment",
                "delayed",
            ),
            "source_terms": ("delivery", "shipping", "shipment"),
            "content_terms": (
                "delivery",
                "shipping",
                "shipment",
                "delayed",
                "dispatch",
            ),
        },
        "cancellation": {
            "query_terms": ("cancel", "cancellation", "cancelled"),
            "source_terms": ("cancel",),
            "content_terms": (
                "cancel",
                "cancellation",
                "cancelled",
            ),
        },
    }

    selected_topic = None

    for topic, config in topic_configs.items():
        if any(term in query for term in config["query_terms"]):
            selected_topic = topic
            break

    # Refund queries may need a wider retrieval distance.
    effective_max_distance = max_distance

    if selected_topic == "refund":
        effective_max_distance = max(max_distance, 1.2)

    matches = search_knowledge(question, top_k=top_k)

    relevant = [
        match
        for match in matches
        if match["distance"] <= effective_max_distance
    ]

    if not relevant:
        return (
            "I couldn't find sufficiently relevant information "
            "in the support knowledge base. Please contact "
            "customer support to confirm the applicable policy."
        )

    # Prefer documents whose filenames match the requested topic.
    # Example: return questions prefer returns.md over cod_refunds.md.
    if selected_topic:
        config = topic_configs[selected_topic]

        source_matches = [
            match
            for match in relevant
            if any(
                term in Path(match["source"]).stem.lower()
                for term in config["source_terms"]
            )
        ]

        if source_matches:
            relevant = source_matches
        else:
            # Fallback: match whole words/phrases in the document text.
            content_matches = []

            for match in relevant:
                content = match["content"].lower()

                if any(
                    re.search(
                        r"(?<!\w)"
                        + re.escape(term)
                        + r"(?!\w)",
                        content,
                    )
                    for term in config["content_terms"]
                ):
                    content_matches.append(match)

            if content_matches:
                relevant = content_matches

    # Return the best matching passage only to reduce unrelated content.
    relevant.sort(key=lambda match: match["distance"])
    best_match = relevant[0]

    source = best_match["source"]
    content = best_match["content"].strip()

    response = f"Source: {source}\n\n{content}"

    if selected_topic in {"return", "refund"}:
        response += (
            "\n\nPlease confirm order-specific eligibility "
            "before making a final decision."
        )

    return response


# ============================================================
# Interactive test
# ============================================================

def main() -> None:
    """Run a simple interactive semantic retrieval session."""

    print("=" * 60)
    print("NYKAA SUPPORT - SEMANTIC RAG")
    print("=" * 60)
    print(f"Knowledge base: {KNOWLEDGE_BASE_DIR}")
    print("Type 'exit' or 'quit' to stop.\n")

    try:
        count = index_documents()

        if count == 0:
            print(
                "No knowledge documents found. Add .md or .txt "
                "files to the knowledge_base folder."
            )
            return

    except Exception as exc:
        logger.exception("Knowledge-base initialization failed")
        print(f"Could not initialize knowledge base: {exc}")
        return

    while True:
        try:
            question = input("Customer question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nRAG session stopped.")
            break

        if question.casefold() in {"exit", "quit", "q"}:
            print("RAG session stopped.")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            print(f"\n{answer_question(question)}\n")
        except Exception:
            logger.exception("Semantic search failed")
            print(
                "Search failed. Check the terminal logs, "
                "dependencies, and knowledge-base files.\n"
            )


if __name__ == "__main__":
    main()
