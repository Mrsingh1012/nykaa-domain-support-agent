
"""Automated tests for the Nykaa support agent."""

import unittest

from src.support_agent import (
    detect_intent,
    handle_customer_message,
)


class TestSupportAgent(unittest.TestCase):

    def test_existing_order(self):
        answer = handle_customer_message(
            "Where is my order NK0006?"
        )

        self.assertIn("NK0006", answer)
        self.assertIn("Shipped", answer)

    def test_missing_order_id(self):
        answer = handle_customer_message(
            "Where is my order?"
        )

        self.assertIn("Please provide your order ID", answer)

    def test_unknown_order(self):
        answer = handle_customer_message(
            "Track order NK9999"
        )

        self.assertIn("No order was found", answer)

    def test_refund_intent(self):
        self.assertEqual(
            detect_intent("How long does a refund take?"),
            "policy",
        )

    def test_return_intent(self):
        self.assertEqual(
            detect_intent("Can I return a product?"),
            "policy",
        )

    def test_delivery_intent(self):
        self.assertEqual(
            detect_intent("How many days does delivery take?"),
            "policy",
        )

        intent = detect_intent(
            "Where is my order NK0006?"
        )

        self.assertEqual(intent, "order_tracking")


if __name__ == "__main__":
    unittest.main(verbosity=2)
