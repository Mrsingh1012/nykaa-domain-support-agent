from pathlib import Path
import re


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge_base"


# ==========================================
# TEXT PROCESSING
# ==========================================

STOP_WORDS = {
    "what", "is", "the", "a", "an",
    "how", "does", "do", "can", "i",
    "my", "me", "to", "for", "of",
    "in", "on", "and", "are", "was",
    "were", "be", "it", "please", "tell"
}


def tokenize(text: str) -> set[str]:
    """Convert text into searchable lowercase words."""
    words = re.findall(r"\b[a-z0-9]+\b", text.lower())
    return set(words) - STOP_WORDS


# ==========================================
# LOAD KNOWLEDGE BASE
# ==========================================

def load_documents() -> list[dict]:
    """Load all Markdown documents from knowledge_base."""

    if not KNOWLEDGE_BASE.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: {KNOWLEDGE_BASE}"
        )

    documents = []

    for file_path in sorted(KNOWLEDGE_BASE.glob("*.md")):

        content = file_path.read_text(encoding="utf-8").strip()

        # Ignore empty files
        if not content:
            continue

        documents.append({
            "source": file_path.name,
            "content": content,
        })

    return documents


# ==========================================
# DOCUMENT RELEVANCE
# ==========================================

def search_knowledge(
    query: str,
    top_k: int = 3
) -> list[dict]:
    """Return the most relevant knowledge-base documents."""

    documents = load_documents()

    if not query.strip():
        return []

    query_words = tokenize(query)

    if not query_words:
        return []

    # Domain-specific intent boosts.
    # These help separate similar documents.
    delivery_terms = {
        "delivery", "shipping", "shipment",
        "delayed", "dispatch", "tracking"
    }

    return_terms = {
        "return", "returns", "refund",
        "refunds", "exchange", "exchanges"
    }

    results = []

    for document in documents:

        filename = document["source"].lower()
        content = document["content"]

        content_words = tokenize(content)

        # Basic word overlap score
        overlap = query_words & content_words
        score = len(overlap)

        # Give a small boost for relevant file names
        if (
            query_words & delivery_terms
            and any(term in filename for term in
                    ("delivery", "shipping", "shipment"))
        ):
            score += 3

        if (
            query_words & return_terms
            and any(term in filename for term in
                    ("return", "refund", "exchange"))
        ):
            score += 3

        if score > 0:
            results.append({
                "source": document["source"],
                "content": content,
                "score": score,
            })

    # Highest relevance first
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:max(1, top_k)]


# ==========================================
# CUSTOMER QUESTION ANSWERING
# ==========================================

def answer_question(question: str) -> str:
    """Answer using the most relevant knowledge documents."""

    results = search_knowledge(question, top_k=3)

    if not results:
        return (
            "No relevant information found in the knowledge base. "
            "Please contact customer support."
        )

    # Do not include lower-scoring, unrelated documents.
    best_score = results[0]["score"]

    best_results = [
        item for item in results
        if item["score"] == best_score
    ]

    response_parts = []

    for item in best_results:
        response_parts.append(
            f"Source: {item['source']}\n"
            f"Relevance score: {item['score']}\n"
            f"{item['content']}"
        )

    return "\n\n---\n\n".join(response_parts)


# ==========================================
# COMMAND-LINE INTERFACE
# ==========================================

def main():
    """Run the customer support question interface."""

    print("=" * 50)
    print("NYKAA DOMAIN SUPPORT - RAG SYSTEM")
    print("=" * 50)
    print(f"Knowledge Base: {KNOWLEDGE_BASE}")
    print()

    try:
        documents = load_documents()
    except (FileNotFoundError, OSError) as error:
        print(f"Error loading knowledge base: {error}")
        return

    if not documents:
        print("No non-empty Markdown documents found.")
        print("Add content to your knowledge_base/*.md files.")
        return

    print(f"Loaded {len(documents)} knowledge documents.")
    print("Type 'exit' to stop.")
    print()

    while True:
        try:
            question = input("Customer question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nRAG system stopped.")
            break

        if question.lower() in {"exit", "quit"}:
            print("RAG system stopped.")
            break

        if not question:
            print("Please enter a question.\n")
            continue

        print()
        print(answer_question(question))
        print()


if __name__ == "__main__":
    main()