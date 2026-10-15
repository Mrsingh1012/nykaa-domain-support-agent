
"""
Order lookup utility for the Nykaa Domain Support Agent.

Dataset:
    <project-root>/data/orders.json

Supported formats:
    [{"record_id": "NK0006", "status": "Shipped"}]
    {"orders": [{"record_id": "NK0006", "status": "Shipped"}]}

This module searches local JSON data only.
It does not connect to a live shipping or order-management API.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ORDERS_FILE = PROJECT_ROOT / "data" / "orders.json"

logger = logging.getLogger(__name__)

ORDER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,50}$")

ORDER_ID_PATTERNS = (
    re.compile(r"\bNK\d{4,}\b", re.IGNORECASE),
    re.compile(r"\bORD-\d{3,}\b", re.IGNORECASE),
)


# --------------------------------------------------
# CUSTOM EXCEPTION
# --------------------------------------------------

class OrderDataError(Exception):
    """Raised when the order dataset cannot be loaded."""


# --------------------------------------------------
# LOAD AND VALIDATE ORDERS
# --------------------------------------------------

def load_orders(
    file_path: Path | str = ORDERS_FILE,
) -> list[dict[str, Any]]:
    """Load order records from a JSON file."""

    path = Path(file_path)

    if not path.is_file():
        raise OrderDataError(
            f"Order dataset was not found: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as exc:
        raise OrderDataError(
            f"Invalid JSON at line {exc.lineno}, "
            f"column {exc.colno}."
        ) from exc

    except OSError as exc:
        raise OrderDataError(
            f"Unable to read order dataset: {exc}"
        ) from exc

    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and isinstance(
        data.get("orders"), list
    ):
        records = data["orders"]
    else:
        raise OrderDataError(
            "Expected a JSON list or an object "
            "containing an 'orders' list."
        )

    if not all(isinstance(record, dict) for record in records):
        raise OrderDataError(
            "Every order record must be a JSON object."
        )

    return records


# --------------------------------------------------
# ORDER ID HELPERS
# --------------------------------------------------

def _get_order_identifier(
    order: dict[str, Any],
) -> str | None:
    """Return the first supported order identifier."""

    for key in ("record_id", "order_id", "id"):
        value = order.get(key)

        if value is not None and str(value).strip():
            return str(value).strip()

    return None


def extract_order_id(question: str) -> str | None:
    """
    Extract a supported order ID from a question.

    Examples:
        Where is order NK0006? -> NK0006
        Track order ORD-1001 -> ORD-1001
        Where is my order? -> None
    """

    if not isinstance(question, str) or not question.strip():
        return None

    for pattern in ORDER_ID_PATTERNS:
        match = pattern.search(question)

        if match:
            return match.group(0).upper()

    return None


# --------------------------------------------------
# ORDER LOOKUP
# --------------------------------------------------

def lookup_order(
    order_id: str,
    file_path: Path | str = ORDERS_FILE,
) -> str:
    """Return a customer-friendly order status summary."""

    if not isinstance(order_id, str) or not order_id.strip():
        return "Please provide a valid order ID."

    order_id = order_id.strip()

    if not ORDER_ID_PATTERN.fullmatch(order_id):
        return (
            "The order ID format is invalid. "
            "Please check the ID and try again."
        )

    try:
        orders = load_orders(file_path)

    except OrderDataError:
        logger.exception("Order dataset could not be loaded")

        return (
            "Order lookup is temporarily unavailable. "
            "Please try again later or contact customer support."
        )

    for order in orders:
        stored_id = _get_order_identifier(order)

        if stored_id is None:
            continue

        if stored_id.casefold() != order_id.casefold():
            continue

        details = [
            f"Order ID: {stored_id}",
            f"Status: {order.get('status', 'Unknown')}",
            f"Category: {order.get('category', 'Unknown')}",
        ]

        optional_fields = (
            ("order_value_inr", "Order Value: INR {}"),
            ("days_since_created", "Days Since Created: {}"),
            ("delayed_shipment", "Delayed Shipment: {}"),
        )

        for field, label in optional_fields:
            value = order.get(field)

            if value is not None:
                details.append(label.format(value))

        return "\n".join(details)

    return (
        f"No order was found for ID '{order_id}'. "
        "Please verify the ID."
    )


# --------------------------------------------------
# LOCAL TEST MODE
# --------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("NYKAA ORDER LOOKUP")
    print(f"Dataset: {ORDERS_FILE}")
    print("Enter an order ID or a question. Type 'exit' to quit.")

    while True:
        try:
            user_input = input("\nOrder ID or question: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nOrder lookup stopped.")
            break

        if user_input.casefold() == "exit":
            print("Order lookup stopped.")
            break

        if not user_input:
            print("Please enter an order ID.")
            continue

        order_id = extract_order_id(user_input)

        # If no known ID pattern is found, allow a bare ID.
        if order_id is None:
            order_id = user_input

        print()
        print(lookup_order(order_id))
