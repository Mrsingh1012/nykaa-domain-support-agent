import re

INTENT_KEYWORDS = {
    "order_tracking": [
        "track order",
        "where is my order",
        "order status",
        "not arrived",
        "not delivered",
    ],
    "delivery": [
        "delivery",
        "shipping",
        "shipment",
        "delayed",
    ],
    "refund": [
        "refund",
        "money back",
        "refund status",
    ],
    "return": [
        "return policy",
        "return",
        "exchange",
    ],
    "product_info": [
        "product details",
        "product price",
        "ingredients",
        "availability",
    ],
    "human_support": [
        "human agent",
        "talk to support",
        "speak to agent",
    ],
}


def detect_intent(question: str) -> str:
    if not isinstance(question, str) or not question.strip():
        return "unknown"

    text = re.sub(
        r"\s+",
        " ",
        question.lower().strip(),
    )

    for intent, phrases in INTENT_KEYWORDS.items():
        for phrase in sorted(phrases, key=len, reverse=True):
            if phrase in text:
                return intent

    return "general"