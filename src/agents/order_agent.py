

"""Professional order tracking agent for the Nykaa support system."""

import logging
import re
from typing import Any

from src.order_tool import extract_order_id, lookup_order

logger = logging.getLogger(__name__)


class OrderAgent:
    """Handle order tracking with clear customer-facing responses."""

    name = "order_agent"

    def run(self, message: str) -> dict[str, Any]:
        """Extract an order ID and return a structured lookup result."""

        if not isinstance(message, str) or not message.strip():
            return {
                "agent": self.name,
                "success": False,
                "answer": "Please enter your order tracking question.",
                "data": None,
            }

        order_id = extract_order_id(message)

        if not order_id:
            # Detect a short NK-style ID such as NK006 without
            # incorrectly converting it to another order ID.
            candidate = re.search(
                r"\bNK\d+\b", message, re.IGNORECASE
            )

            if candidate:
                invalid_id = candidate.group(0).upper()
                return {
                    "agent": self.name,
                    "success": False,
                    "answer": (
                        f"'{invalid_id}' does not match the expected "
                        "order ID format. Please check your order "
                        "confirmation and enter the complete ID, "
                        "for example NK0006."
                    ),
                    "data": None,
                }

            return {
                "agent": self.name,
                "success": False,
                "answer": (
                    "Please provide your order ID, for example NK0006."
                ),
                "data": None,
            }

        try:
            result = lookup_order(order_id)

            if not isinstance(result, str) or not result.strip():
                logger.warning(
                    "Empty or unexpected lookup response for %s",
                    order_id,
                )
                return {
                    "agent": self.name,
                    "success": False,
                    "answer": (
                        "We couldn't retrieve your order details right "
                        "now. Please try again later."
                    ),
                    "data": None,
                }

            answer = result.strip()
            normalized = answer.casefold()

            if (
                normalized.startswith("no order was found")
                or normalized.startswith("please provide a valid order id")
                or normalized.startswith("the order id format is invalid")
            ):
                return {
                    "agent": self.name,
                    "success": False,
                    "answer": answer,
                    "data": None,
                }

            if "temporarily unavailable" in normalized:
                return {
                    "agent": self.name,
                    "success": False,
                    "answer": answer,
                    "data": None,
                }

            return {
                "agent": self.name,
                "success": True,
                "answer": answer,
                "data": {"order_id": order_id, "details": answer},
            }

        except Exception:
            logger.exception("Order agent failed for ID %s", order_id)

            return {
                "agent": self.name,
                "success": False,
                "answer": (
                    "Order tracking is temporarily unavailable. "
                    "Please try again later."
                ),
                "data": None,
            }


order_agent = OrderAgent()
