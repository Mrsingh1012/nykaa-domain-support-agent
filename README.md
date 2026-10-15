# Nykaa AI Support Agent

An AI-powered e-commerce customer support application built with Python, FastAPI, Streamlit, and Retrieval-Augmented Generation (RAG).

## Overview

The Nykaa AI Support Agent helps customers with common e-commerce support queries through a chat interface.

## Features

- **Order Tracking:** Look up order details using an order ID.
- **Product Search:** Find matching products and view available product information.
- **Policy Support:** Retrieve relevant information from the local knowledge base.
- **Error Handling:** Provide helpful responses for unknown orders and invalid requests.
- **REST API:** Serve customer support requests through FastAPI.
- **Chat Interface:** Interact with the support agent through Streamlit.
- **Automated Tests:** Unit, RAG, and API integration tests.

## Technology Stack

- Python 3.11
- FastAPI and Uvicorn
- Streamlit
- ChromaDB
- Sentence Transformers
- Pydantic
- `unittest` and HTTPX

## Project Structure

```text
nykaa-domain-support-agent/
├── data/
│   ├── orders.json
│   └── products.json
├── knowledge_base/
│   ├── cod_refunds.md
│   ├── delivery.md
│   └── returns.md
├── src/
│   ├── agents/
│   ├── order_tool.py
│   ├── product_tool.py
│   ├── semantic_rag.py
│   └── support_agent.py
├── tests/
│   ├── test_api.py
│   ├── test_order_agent.py
│   ├── test_policy_agent.py
│   ├── test_product_tool.py
│   ├── test_semantic_rag.py
│   └── test_support_agent.py
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

## Setup

### 1. Create a virtual environment

```powershell
py -3.11 -m venv .venv
```

### 2. Activate it

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

Ensure `streamlit` and `requests` are included in `requirements.txt` for the frontend.

## Run the Application

### Start the FastAPI backend

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

### Start the Streamlit frontend

Open a second terminal in the project directory:

```powershell
python -m streamlit run app.py
```

## API Example

Endpoint: `POST /support`

Request:

```json
{
  "question": "Where is my order NK0006?"
}
```

The response contains the submitted question and the support agent's answer.

## Run Tests

```powershell
python -m unittest discover -s tests -v
```

The latest reported test run completed with **31 tests passing**.

## Important Notes

- This project currently uses local sample order and product data.
- It is a demonstration project, not a verified connection to Nykaa's production systems.
- Policy answers depend on the local knowledge-base documents.
- Keep secrets, virtual environments, local databases, and generated files out of version control.

## Future Improvements

- Improve chat UI and response formatting.
- Add more retrieval-quality tests.
- Add authentication, rate limiting, and production monitoring.
- Deploy the API and frontend securely.
- Add CI automation for tests.

## License

Add a license before distributing or publishing this project.
