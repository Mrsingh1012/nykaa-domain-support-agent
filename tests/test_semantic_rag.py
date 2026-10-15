
import unittest
from unittest.mock import patch

from src.semantic_rag import answer_question


class TestSemanticRAG(unittest.TestCase):

    @patch("src.semantic_rag.search_knowledge")
    def test_return_question_prefers_returns_policy(self, mock_search):
        mock_search.return_value = [
            {
                "source": "cod_refunds.md",
                "content": "Refunds are processed after inspection.",
                "distance": 0.20,
            },
            {
                "source": "returns.md",
                "content": (
                    "Customers can request a return within "
                    "7 days of delivery."
                ),
                "distance": 0.35,
            },
        ]

        answer = answer_question(
            "What is the return policy for my order?"
        )

        self.assertIn("returns.md", answer)
        self.assertIn("7 days", answer)
        self.assertNotIn("cod_refunds.md", answer)

    @patch("src.semantic_rag.search_knowledge")
    def test_refund_question_prefers_refund_policy(self, mock_search):
        mock_search.return_value = [
            {
                "source": "returns.md",
                "content": "Returns can be requested within 7 days.",
                "distance": 0.30,
            },
            {
                "source": "cod_refunds.md",
                "content": (
                    "Refunds are processed after the returned "
                    "product passes inspection."
                ),
                "distance": 0.25,
            },
        ]

        answer = answer_question("How do I get a refund?")

        self.assertIn("cod_refunds.md", answer)
        self.assertIn("inspection", answer)
        self.assertNotIn("Source: returns.md", answer)

    @patch("src.semantic_rag.search_knowledge")
    def test_no_relevant_policy_returns_safe_message(self, mock_search):
        mock_search.return_value = [
            {
                "source": "returns.md",
                "content": "Return policy information.",
                "distance": 1.8,
            }
        ]

        answer = answer_question(
            "What is the return policy?",
            max_distance=1.0,
        )

        self.assertIn("couldn't find sufficiently relevant", answer)


if __name__ == "__main__":
    unittest.main()
