
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


class TestNykaaAPI(unittest.TestCase):
    """Integration tests for the Nykaa Support API."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    @patch(
        "src.support_agent.handle_customer_message",
        return_value="Order ID: NK0006\nStatus: Shipped",
    )
    def test_support_endpoint_success(self, mock_handler):
        response = self.client.post(
            "/support",
            json={"question": "Where is my order NK0006?"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["question"],
            "Where is my order NK0006?",
        )
        self.assertIn("NK0006", data["answer"])

    def test_support_endpoint_empty_question(self):
        response = self.client.post(
            "/support",
            json={"question": ""},
        )

        # The endpoint should return a controlled response,
        # rather than an unhandled server error.
        self.assertLess(response.status_code, 500)

    def test_support_endpoint_missing_question(self):
        response = self.client.post(
            "/support",
            json={},
        )

        # FastAPI request validation should reject missing input.
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
