

"""Tests for policy agent response status."""

import unittest
from unittest.mock import patch

from src.agents.policy_agent import PolicyAgent


class TestPolicyAgent(unittest.TestCase):

    def setUp(self):
        self.agent = PolicyAgent()

    @patch("src.agents.policy_agent.index_documents")
    @patch("src.agents.policy_agent.answer_question")
    def test_successful_policy_answer(self, mock_answer, mock_index):
        mock_answer.return_value = (
            "Source: returns.md\n"
            "Customers can request a return within 7 days."
        )

        result = self.agent.run("Can I return a product?")

        self.assertTrue(result["success"])
        self.assertIn("7 days", result["answer"])
        self.assertEqual(result["agent"], "policy_agent")
        self.assertIn("returns.md", result["answer"])

    @patch("src.agents.policy_agent.index_documents")
    @patch("src.agents.policy_agent.answer_question")
    def test_fallback_is_not_success(self, mock_answer, mock_index):
        mock_answer.return_value = (
            "I couldn't find sufficiently relevant information "
            "in the support knowledge base. Please contact "
            "customer support to confirm the applicable policy."
        )

        result = self.agent.run("What is an unknown policy?")

        self.assertFalse(result["success"])
        self.assertIn("couldn't find", result["answer"])

    @patch("src.agents.policy_agent.index_documents")
    @patch("src.agents.policy_agent.answer_question")
    def test_unusable_answer_is_not_success(
        self, mock_answer, mock_index
    ):
        mock_answer.return_value = (
            "I couldn't find a usable answer in the support "
            "knowledge base. Please verify the policy through "
            "official customer support."
        )

        result = self.agent.run("What is an unknown policy?")

        self.assertFalse(result["success"])
        self.assertIn("usable answer", result["answer"])

    def test_empty_question(self):
        result = self.agent.run("   ")

        self.assertFalse(result["success"])
        self.assertIn("Please enter", result["answer"])

    @patch("src.agents.policy_agent.index_documents")
    def test_exception_returns_friendly_message(self, mock_index):
        mock_index.side_effect = RuntimeError("Internal database error")

        result = self.agent.run("Can I return a product?")

        self.assertFalse(result["success"])
        self.assertIn("temporarily unavailable", result["answer"])
        self.assertIsNone(result["data"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
