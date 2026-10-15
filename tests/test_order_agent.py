
"""Tests for the order tracking agent."""

import unittest
from unittest.mock import patch

from src.agents.order_agent import OrderAgent


class TestOrderAgent(unittest.TestCase):

    def setUp(self):
        self.agent = OrderAgent()

    @patch("src.agents.order_agent.lookup_order")
    def test_valid_order(self, mock_lookup):
        mock_lookup.return_value = (
            "Order ID: NK0006\nStatus: Shipped\nCategory: Skincare"
        )

        result = self.agent.run("Track my order NK0006")

        self.assertTrue(result["success"])
        self.assertIn("NK0006", result["answer"])
        self.assertEqual(result["agent"], "order_agent")
        self.assertEqual(result["data"]["order_id"], "NK0006")

    def test_invalid_short_nykaa_order_id(self):
        result = self.agent.run("Track my order NK006")

        self.assertFalse(result["success"])
        self.assertIn("NK006", result["answer"])
        self.assertIn("NK0006", result["answer"])

    def test_missing_order_id(self):
        result = self.agent.run("Where is my order?")

        self.assertFalse(result["success"])
        self.assertIn("provide your order ID", result["answer"])

    @patch("src.agents.order_agent.lookup_order")
    def test_unknown_order(self, mock_lookup):
        mock_lookup.return_value = (
            "No order was found for ID 'NK0099'. Please verify the ID."
        )

        result = self.agent.run("Track order NK0099")

        self.assertFalse(result["success"])
        self.assertIn("No order was found", result["answer"])

    @patch("src.agents.order_agent.lookup_order")
    def test_lookup_unavailable(self, mock_lookup):
        mock_lookup.return_value = (
            "Order lookup is temporarily unavailable. "
            "Please try again later."
        )

        result = self.agent.run("Track order NK0006")

        self.assertFalse(result["success"])
        self.assertIn("temporarily unavailable", result["answer"])

    def test_empty_message(self):
        result = self.agent.run("   ")

        self.assertFalse(result["success"])
        self.assertIn("Please enter", result["answer"])

    @patch("src.agents.order_agent.lookup_order")
    def test_lookup_exception(self, mock_lookup):
        mock_lookup.side_effect = RuntimeError("Internal error")

        result = self.agent.run("Track order NK0006")

        self.assertFalse(result["success"])
        self.assertIn("temporarily unavailable", result["answer"])
        self.assertIsNone(result["data"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
