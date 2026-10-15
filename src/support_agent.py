"""
Nykaa Domain Support Agent.

Features:
- Order ID extraction and local order lookup
- Semantic retrieval from the support knowledge base
- Customer-friendly response formatting
- Logging and graceful error handling

Order data is read from a local sample dataset.
No live Nykaa order or shipping API is connected.
"""

from __future__ import annotations

import logging
import re
from threading import Lock
from typing import Any

from src.order_tool import extract_order_id, lookup_order
from src.product_tool import search_products, format_product_results
from src.semantic_rag import answer_question, index_documents


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logger = logging.getLogger(__name__)

if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )


# --------------------------------------------------
# INTENT KEYWORDS
# --------------------------------------------------

ORDER_KEYWORDS = (
    "track",
    "tracking",
    "shipment",
    "delivery status",
    "where is my order",
    "track my order",
    "order status",
    "my order",
    "parcel",
    "????? ?????",
    "????? ??????",
    "???? ?????",
    "????? ????",
)

POLICY_KEYWORDS = (
    "return",
    "refund",
    "exchange",
    "cancellation",
    "delivery time",
    "shipping policy",
    "cash on delivery",
    "cod",
    "payment policy",
    "policy",
    "returns",
    "refunds",
    "?????",
    "??????",
    "?????",
    "????????",
    "????",
    "???????",
)

PRODUCT_KEYWORDS = (
    "product",
    "products",
    "search product",
    "find product",
    "show me",
    "face serum",
    "moisturizer",
    "lipstick",
    "mascara",
    "cleanser",
    "skincare",
    "makeup",
    "price of",
    "under ?",
    "under rs",
    "under inr",
    "???",
    "????????",
    "??????????",
)


# --------------------------------------------------
# KNOWLEDGE BASE INITIALIZATION
# --------------------------------------------------

_kb_initialized = False
_kb_lock = Lock()


def ensure_knowledge_base() -> bool:
    """
    Initialize the knowledge base once per process.

    Returns True when initialization succeeds.
    """

    global _kb_initialized

    if _kb_initialized:
        return True

    with _kb_lock:
        if _kb_initialized:
            return True

        try:
            count = index_documents()

            logger.info(
                "Knowledge base initialized. Chunks: %s",
                count,
            )

            _kb_initialized = True
            return True

        except Exception:
            logger.exception(
                "Knowledge base initialization failed"
            )
            return False


# --------------------------------------------------
# INTENT DETECTION
# --------------------------------------------------

def detect_intent(message: str) -> str:
    """Classify a customer message using keyword-based routing."""

    if not isinstance(message, str) or not message.strip():
        return "general"

    text = message.casefold()

    # 1. Explicit order IDs always take priority.
    if extract_order_id(message):
        return "order_tracking"

    # 2. Policy questions before generic order keywords.
    policy_terms = (
        "return",
        "returns",
        "refund",
        "refunds",
        "exchange",
        "cancellation",
        "cancel order",
        "delivery",
        "shipping",
        "how many days",
        "delivery time",
        "shipping time",
        "cash on delivery",
        "cod",
        "payment policy",
        "return policy",
        "refund policy",
    )

    if (
        any(keyword in text for keyword in POLICY_KEYWORDS)
        or any(term in text for term in policy_terms)
    ):
        return "policy"

    # 3. Order tracking questions.
    if any(keyword in text for keyword in ORDER_KEYWORDS):
        return "order_tracking"

    # 4. Product search questions.
    if any(keyword in text for keyword in PRODUCT_KEYWORDS):
        return "product_search"

    # 5. Fallback.
    return "general"




# --------------------------------------------------
# RAG RESPONSE FORMATTING
# --------------------------------------------------

def format_retrieval_response(response: Any) -> str:
    """Format the semantic retrieval response for customers."""

    if not isinstance(response, str) or not response.strip():
        return (
            "I couldn't find a usable answer in the support "
            "knowledge base. Please verify the policy through "
            "official customer support."
        )

    response = response.strip()

    normalized = response.casefold()

    if "couldn't find sufficiently relevant information" in normalized:
        return response

    formatted_lines: list[str] = []

    for raw_line in response.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Hide internal retrieval scores.
        if line.casefold().startswith("distance:"):
            continue

        # Remove generic RAG headings.
        if line.casefold().startswith(
            (
                "relevant information from the support knowledge base:",
                "here is the relevant information from the support knowledge base:",
            )
        ):
            continue

        # Retain source information without the [1] prefix.
        if line.startswith("[") and "] source:" in line.casefold():
            source_index = line.casefold().find("source:")
            line = line[source_index:]

        formatted_lines.append(line)


    if not formatted_lines:
        return (
            "I couldn't find a usable answer in the support "
            "knowledge base. Please contact official support."
        )

    return "\n".join(formatted_lines)


# --------------------------------------------------
# ORDER LOOKUP
# --------------------------------------------------

def _order_response(question: str) -> str:
    """Look up an order in the local sample dataset."""


    order_id = extract_order_id(question)

    if not order_id:
        # Identify a short or malformed NK-style order ID.
        candidate = re.search(r"\bNK\d+\b", question, re.IGNORECASE)

        if candidate:
            invalid_id = candidate.group(0).upper()
            return (
                f"'{invalid_id}' does not match the expected order ID "
                "format. Please check your order confirmation and "
                "enter the complete ID, for example NK0006."
            )

        return (
            "Please provide your order ID, for example NK0006."
        )


    try:
        result = lookup_order(order_id)

    except Exception:
        logger.exception(
            "Order lookup failed for order ID %s",
            order_id,
        )

        return (
            "Order lookup is temporarily unavailable. "
            "Please try again later."
        )

    if isinstance(result, str):
        return result.strip() or (
            "No order details are available for this order."
        )

    if isinstance(result, dict):
        nested = result.get("order") or result.get("record")

        if isinstance(nested, dict):
            result = nested

        if isinstance(result, dict):
            labels = (
                ("Order ID", ("record_id", "order_id", "id")),
                ("Status", ("status", "order_status")),
                ("Category", ("category", "product_category")),
                (
                    "Order Value",
                    ("order_value_inr", "order_value", "amount", "price", "total"),
                ),
                (
                    "Days Since Created",
                    ("days_since_created", "days_since_order"),
                ),
                (
                    "Delayed Shipment",
                    ("delayed_shipment", "is_delayed", "delayed"),
                ),
            )

            lines = []

            for label, keys in labels:
                value = next(
                    (
                        result[key]
                        for key in keys
                        if result.get(key) is not None
                    ),
                    None,
                )

                if value is None:
                    continue

                if label == "Order Value" and isinstance(
                    value, (int, float)
                ):
                    value = f"INR {value:g}"

                lines.append(f"{label}: {value}")

            if lines:
                return "\n".join(lines)

    return str(result)


# --------------------------------------------------
# MAIN CUSTOMER MESSAGE HANDLER
# --------------------------------------------------

def handle_customer_message(message: str) -> str:
    """Route a customer message to the correct support function."""

    if not isinstance(message, str) or not message.strip():
        return "Please enter a question."

    question = message.strip()
    intent = detect_intent(question)

    logger.info("Detected intent: %s", intent)

    # Route order queries directly to the order tool.
    if intent == "order_tracking":
        return _order_response(question)

    # Route product questions to the product search tool.
    if intent == "product_search":
        products = search_products(question)
        return format_product_results(products)


    # Initialize and query the knowledge base for other questions.
    if not ensure_knowledge_base():
        return (
            "Support search is temporarily unavailable. "
            "Please try again later."
        )

    try:
        rag_result = answer_question(question)
        return format_retrieval_response(rag_result)

    except Exception:
        logger.exception("Semantic RAG request failed")

        return (
            "Support search is temporarily unavailable. "
            "Please try again later."
        )


# --------------------------------------------------
# LOCAL INTERACTIVE TEST
# --------------------------------------------------

def main() -> None:
    """Run the support agent in the terminal."""

    print("=" * 48)
    print("       NYKAA DOMAIN SUPPORT AGENT")
    print("       Order Lookup + Semantic RAG")
    print("=" * 48)
    print("Type 'exit' or 'quit' to stop.\n")

    ensure_knowledge_base()

    while True:
        try:
            message = input("Customer: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nAgent stopped.")
            break

        if message.casefold() in {"exit", "quit"}:
            print("Goodbye!")
            break

        response = handle_customer_message(message)
        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
