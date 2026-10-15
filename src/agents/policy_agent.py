

"""Policy support agent using the existing semantic RAG system."""

import logging
from typing import Any

from src.semantic_rag import answer_question, index_documents
from src.support_agent import format_retrieval_response

logger = logging.getLogger(__name__)


class PolicyAgent:
    """Answer customer policy questions using the support knowledge base."""

    name = "policy_agent"

    def run(self, message: str) -> dict[str, Any]:
        """Retrieve policy information and return a structured response."""

        if not isinstance(message, str) or not message.strip():
            return {
                "agent": self.name,
                "success": False,
                "answer": "Please enter your policy question.",
                "data": None,
            }

        try:
            index_documents()

            result = answer_question(message.strip())
            answer = format_retrieval_response(result)
            normalized_answer = answer.strip().casefold()

            fallback_phrases = (
                "i couldn't find sufficiently relevant information",
                "i couldn't find a usable answer",
                "policy search is temporarily unavailable",
            )

            is_fallback = normalized_answer.startswith(fallback_phrases)

            return {
                "agent": self.name,
                "success": bool(normalized_answer) and not is_fallback,
                "answer": answer,
                "data": None,
            }

        except Exception:
            logger.exception("Policy agent failed")

            return {
                "agent": self.name,
                "success": False,
                "answer": (
                    "Policy search is temporarily unavailable. "
                    "Please try again later."
                ),
                "data": None,
            }


policy_agent = PolicyAgent()
