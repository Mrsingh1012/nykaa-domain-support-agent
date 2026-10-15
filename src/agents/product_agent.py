
"""Product agent for the Nykaa domain support system."""

import logging
from typing import Any

from src.product_tool import format_product_results, search_products

logger = logging.getLogger(__name__)


class ProductAgent:
    """Handle product discovery using the existing product tool."""

    name = "product_agent"

    def run(self, message: str) -> dict[str, Any]:
        """Search the product catalogue and return a structured result."""
        if not isinstance(message, str) or not message.strip():
            return {
                "agent": self.name,
                "success": False,
                "answer": "Please tell me which product you are looking for.",
                "data": [],
            }

        try:
            products = search_products(message)

            return {
                "agent": self.name,
                "success": True,
                "answer": format_product_results(products),
                "data": products,
            }

        except Exception:
            logger.exception("Product agent failed")

            return {
                "agent": self.name,
                "success": False,
                "answer": (
                    "Product search is temporarily unavailable. "
                    "Please try again later."
                ),
                "data": [],
            }


product_agent = ProductAgent()
