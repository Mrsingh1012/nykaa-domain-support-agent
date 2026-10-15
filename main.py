
"""
Nykaa AI Support Agent API
FastAPI application entry point.
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from src.support_agent import handle_customer_message


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
CHAT_PAGE = STATIC_DIR / "index.html"


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Nykaa AI Support Agent",
    description="E-Commerce customer support API",
    version="1.1.0",
)


# --------------------------------------------------
# REQUEST AND RESPONSE MODELS
# --------------------------------------------------

class SupportRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Customer support question",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        """Reject questions containing only whitespace."""

        value = value.strip()

        if not value:
            raise ValueError("Question cannot be empty.")

        return value


class SupportResponse(BaseModel):
    question: str
    answer: str


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

# Mount static files only when the folder exists.
if STATIC_DIR.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )


# --------------------------------------------------
# CHAT PAGE
# --------------------------------------------------

@app.get("/chat", include_in_schema=False)
def chat_page():
    """Serve the optional HTML chat interface."""

    if not CHAT_PAGE.is_file():
        raise HTTPException(
            status_code=404,
            detail="Chat page not found. Check static/index.html.",
        )

    return FileResponse(CHAT_PAGE)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def home():
    """Check whether the API is running."""

    return {
        "message": "Nykaa AI Support Agent API is running",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Return application health status."""

    return {"status": "healthy"}


# --------------------------------------------------
# CUSTOMER SUPPORT ENDPOINT
# --------------------------------------------------

@app.post("/support", response_model=SupportResponse)
def customer_support(request: SupportRequest):
    """Process a customer support question."""

    try:
        answer = handle_customer_message(request.question)

        return SupportResponse(
            question=request.question,
            answer=str(answer),
        )

    except Exception as exc:
        logger.exception("Failed to process support request")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the support request.",
        ) from exc
