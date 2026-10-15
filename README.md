# README_backup.md

An independent e-commerce customer-support portfolio project built with **Python 3.11, FastAPI, Streamlit, ChromaDB, and Sentence Transformers**. It demonstrates order lookup against a synthetic dataset, product search, policy retrieval, API validation, and automated testing.

> **Project track:** Nykaa â€” E-commerce & Retail
> **Data note:** The repository uses synthetic sample orders and a local sample product catalogue. It is not connected to Nykaa's production systems and does not access live customer orders.

## Highlights

- **Order tracking:** Extracts an order ID and looks up the matching record in `data/orders.json`.
- **Product search:** Searches the local catalogue in `data/products.json`.
- **Policy support:** Retrieves relevant passages from Markdown documents in `knowledge_base/`.
- **Semantic retrieval (RAG component):** Chunks policy text, creates embeddings with Sentence Transformers, and stores/retrieves vectors with ChromaDB.
- **FastAPI backend:** Validated `POST /support` endpoint plus health and API-documentation endpoints.
- **Two local chat interfaces:** Streamlit (`app.py`) and an HTML chat page served by FastAPI at `/chat`.
- **Automated tests:** Unit and API tests for order lookup, product search, policy retrieval, and support handling.

## Technology Stack

| Area | Technology |
| --- | --- |
| Language | Python 3.11 |
| API | FastAPI, Uvicorn, Pydantic |
| UI | Streamlit; HTML, CSS, and JavaScript for the static chat page |
| Semantic retrieval | Sentence Transformers, ChromaDB |
| Data | JSON sample datasets; Markdown knowledge base |
| Testing | `unittest`, HTTPX |
| Version control | Git and GitHub |

## Architecture Overview

1. A customer submits a question through Streamlit or the static chat page.
2. The client sends the question to the FastAPI `POST /support` endpoint.
3. FastAPI validates the request and calls `handle_customer_message()` in `src/support_agent.py`.
4. Keyword-based intent routing selects the relevant path:
   - **Order tracking** â†’ extract the order ID â†’ look up the synthetic order dataset.
   - **Product search** â†’ search the local product catalogue.
   - **Policy/general support** â†’ retrieve relevant passages from the local knowledge base using the semantic retrieval component.
5. The API returns a structured JSON response and the client displays the answer.

The semantic retrieval module performs retrieval; it does not itself call an LLM to generate answers. This repository is a demonstration project, not a production deployment.

## Repository Structure

```text
nykaa-domain-support-agent/
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ orders.json
â”‚   â””â”€â”€ products.json
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ index.html
â”‚   â”œâ”€â”€ script.js
â”‚   â””â”€â”€ style.css
â”œâ”€â”€ knowledge_base/
â”‚   â”œâ”€â”€ cod_refunds.md
â”‚   â”œâ”€â”€ customer_support.md
â”‚   â”œâ”€â”€ delivery.md
â”‚   â””â”€â”€ returns.md
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ agents/
â”‚   â”‚   â”œâ”€â”€ order_agent.py
â”‚   â”‚   â”œâ”€â”€ policy_agent.py
â”‚   â”‚   â””â”€â”€ product_agent.py
â”‚   â”œâ”€â”€ intent.py
â”‚   â”œâ”€â”€ order_tool.py
â”‚   â”œâ”€â”€ product_tool.py
â”‚   â”œâ”€â”€ rag.py
â”‚   â”œâ”€â”€ semantic_rag.py
â”‚   â””â”€â”€ support_agent.py
â”œâ”€â”€ static/
â”‚   â”œâ”€â”€ index.html
â”‚   â”œâ”€â”€ script.js
â”‚   â””â”€â”€ style.css
â”œâ”€â”€ tests/
â”‚   â”œâ”€â”€ test_api.py
â”‚   â”œâ”€â”€ test_order_agent.py
â”‚   â”œâ”€â”€ test_policy_agent.py
â”‚   â”œâ”€â”€ test_product_tool.py
â”‚   â”œâ”€â”€ test_semantic_rag.py
â”‚   â””â”€â”€ test_support_agent.py
â”œâ”€â”€ app.py
â”œâ”€â”€ dataset.py
â”œâ”€â”€ main.py
â”œâ”€â”€ requirements.txt
â””â”€â”€ README.md
```

## Dataset Design

The synthetic order dataset is reproducible using `dataset.py`:

- **Random seed:** `42`
- **Number of records:** `50`
- **Categories:** Apparel, Electronics, Home, Footwear, Beauty
- **Statuses:** Placed, Shipped, Delivered, Returned, Refunded
- **Order-value range:** â‚¹299â€“â‚¹24,999
- **Order age:** 0â€“30 days
- **Configured delayed-shipment probability:** 20%
- **Coverage rule:** Each category is seeded with at least three records and every status is included; remaining values are filled using the seeded random generator.

Regenerate and validate the dataset from the repository root:

```powershell
python dataset.py
```

This writes `data/orders.json`. Only use synthetic/demo records in a public repository.

## Getting Started (Windows PowerShell)

### 1. Clone the repository

```powershell
git clone https://github.com/Mrsingh1012/nykaa-domain-support-agent.git
cd nykaa-domain-support-agent
```

### 2. Create and activate a Python 3.11 environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks environment activation, you can run the environment's Python directly with `.\.venv\Scripts\python.exe` instead of activating it.

### 3. Start the FastAPI backend

Open a terminal in the project root:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Useful endpoints:

- API root: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- Interactive API docs: http://127.0.0.1:8000/docs
- Static HTML chat page: http://127.0.0.1:8000/chat

### 4. Start the Streamlit interface

Open a **second terminal** in the project root, activate the same virtual environment, and run:

```powershell
python -m streamlit run app.py
```

Streamlit normally opens at http://localhost:8501. The FastAPI backend must be running because the Streamlit interface sends requests to `http://127.0.0.1:8000/support`.

## API Example

**Request:** `POST /support`

```json
{
  "question": "Where is my order NK0006?"
}
```

**Response shape:**

```json
{
  "question": "Where is my order NK0006?",
  "answer": "Order details returned from the local synthetic dataset."
}
```

The exact answer depends on the current sample data and support logic.

## Run the Tests

From the repository root, with dependencies installed:

```powershell
python -m unittest discover -s tests -v
```

**Latest local result reported:** 31 tests passed. Run the command above to verify the current checkout on your machine.

## Security and Limitations

- Do not commit API keys, passwords, personal data, or real customer/order records.
- The included order records are synthetic demo data; they do not represent live Nykaa customer information.
- The app is not affiliated with or endorsed by Nykaa.
- The current intent routing is keyword-based; it is not a general-purpose autonomous agent.
- Semantic retrieval returns relevant knowledge-base content; the retrieval module itself does not call an LLM.
- A production deployment would need authentication, authorization, rate limiting, observability, privacy controls, robust evaluation, and approved integrations to real business systems.

## Potential Next Steps

- Add a CI workflow to run tests on every pull request.
- Add retrieval-quality evaluation with a fixed test-question set.
- Add authentication and human escalation for unresolved requests.
- Deploy the API and UI securely after a production-readiness review.

## License

No license has been added yet. Add an appropriate license before allowing others to reuse, modify, or redistribute this project.
