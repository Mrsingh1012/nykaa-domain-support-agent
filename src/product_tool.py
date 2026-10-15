
"""Product search tool for the e-commerce support agent."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_FILE = PROJECT_ROOT / "data" / "products.json"


def load_products() -> list[dict[str, Any]]:
    """Load and validate the product dataset."""
    try:
        with PRODUCTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Product data must be a JSON list.")

        products = []

        for item in data:
            if not isinstance(item, dict):
                continue

            if not all(
                key in item
                for key in ("product_id", "name", "price")
            ):
                continue

            products.append(item)

        return products

    except FileNotFoundError:
        logger.error("Product dataset not found: %s", PRODUCTS_FILE)
        return []

    except (json.JSONDecodeError, ValueError):
        logger.exception("Invalid product dataset.")
        return []


def search_products(
    query: str,
    max_price: float | None = None,
    in_stock_only: bool = True,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Search products by name, brand, category, or description."""
    if not isinstance(query, str) or not query.strip():
        return []

    if max_price is not None and max_price < 0:
        return []

    if limit < 1:
        return []

    products = load_products()

    stop_words = {
        "show", "me", "find", "search", "for",
        "the", "a", "an", "please", "some",
        "product", "products", "of", "under",
    }

    terms = [
        word
        for word in query.casefold().split()
        if word not in stop_words
    ]

    if not terms:
        return []

    results = []

    for product in products:
        if in_stock_only and product.get("in_stock") is not True:
            continue

        try:
            price = float(product["price"])
        except (TypeError, ValueError):
            continue

        if max_price is not None and price > max_price:
            continue

        searchable_text = " ".join(
            str(product.get(field, ""))
            for field in ("name", "brand", "category", "description")
        ).casefold()

        if all(term in searchable_text for term in terms):
            results.append(product)

    results.sort(
        key=lambda item: (
            -float(item.get("rating", 0) or 0),
            float(item["price"]),
        )
    )

    return results[:limit]


def format_product_results(
    products: list[dict[str, Any]],
) -> str:
    """Format search results into a customer-friendly response."""
    if not products:
        return (
            "No matching in-stock products were found. "
            "Try another keyword or a higher budget."
        )

    lines = ["Here are the matching products:"]

    for product in products:
        lines.extend([
            "",
            f"**{product['name']}**",
            f"Product ID: {product['product_id']}",
            f"Brand: {product.get('brand', 'Not specified')}",
            f"Category: {product.get('category', 'Not specified')}",
            f"Price: ₹{float(product['price']):,.2f}",
            f"Rating: {product.get('rating', 'Not rated')}",
            f"In stock: {'Yes' if product.get('in_stock') else 'No'}",
            f"Description: {product.get('description', 'Not available')}",
        ])

    return "\n".join(lines)
