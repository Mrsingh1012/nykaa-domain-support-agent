# Nykaa Domain Support Agent

An AI-powered e-commerce customer support system designed to answer customer queries, track orders, search products, and retrieve relevant support policies using a modular multi-agent architecture and Retrieval-Augmented Generation (RAG).

The project combines Python, FastAPI, Streamlit, semantic search, and automated testing to demonstrate how AI agents can support common e-commerce customer service workflows.

## Overview

E-commerce businesses receive a wide range of customer queries related to order status, product discovery, shipping, returns, refunds, and company policies. Handling these requests manually can be time-consuming and difficult to scale.

The Nykaa Domain Support Agent aims to simplify these workflows through an intelligent support interface that identifies customer intent, invokes relevant tools, searches product information, and retrieves contextual knowledge to generate useful responses.

**Project type:** AI Agent / E-commerce Customer Support  
**Primary language:** Python  
**Backend:** FastAPI  
**Frontend:** Streamlit  
**Knowledge retrieval:** Retrieval-Augmented Generation (RAG) and semantic search  
**Testing:** Python unittest framework  
**Data storage:** Local JSON datasets and ChromaDB, where configured

## Key Features

### 1. Intelligent Customer Query Handling
- Processes customer questions about e-commerce support.
- Identifies supported intents, including order tracking, product search, and policy-related queries.
- Routes requests to the appropriate support logic or tool.

### 2. Order Tracking
- Extracts order IDs from customer messages.
- Looks up order information from the configured local dataset.
- Returns available order details, such as status, category, order value, and shipment delay indicators.
- Handles invalid or missing order IDs through validation and error handling.

### 3. Product Search
- Searches the configured product catalogue.
- Supports product discovery using customer queries.
- Returns available product details, including product names, identifiers, and prices.

### 4. Retrieval-Augmented Generation (RAG)
- Uses a local knowledge base for retrieving relevant support information.
- Integrates semantic retrieval to improve the relevance of answers.
- Can support policy-related queries using retrieved context.

### 5. FastAPI Backend
- Exposes HTTP endpoints for interacting with the support system.
- Separates API handling from the underlying support logic.
- Supports local development and API testing.

### 6. Streamlit Frontend
- Provides a simple interface for submitting customer questions.
- Displays support responses in an interactive application.
- Makes the system easier to demonstrate and test.

### 7. Automated Testing
- Includes unit tests for supported application components.
- Tests important workflows, input validation, and error-handling scenarios.
- Helps identify regressions during development.

## Technology Stack

- **Python:** Application logic and agent tools
- **FastAPI:** Backend API
- **Streamlit:** User interface
- **ChromaDB:** Local vector storage, where configured
- **RAG and semantic retrieval:** Knowledge-grounded support responses
- **JSON:** Local sample order and product data
- **unittest:** Automated testing
- **Git and GitHub:** Version control and project collaboration

## Project Architecture

Customer Query → API / User Interface → Intent Detection → Relevant Support Tool or Retrieval Component → Response Generation → Customer Response

The order lookup, product search, and knowledge retrieval components are designed to keep responsibilities modular and easier to maintain.

## Project Structure

```text
nykaa-domain-support-agent/
├── data/
│   └── orders.json
├── knowledge_base/
│   └── cod_refunds.md
├── src/
│   ├── agents/
│   ├── order_tool.py
│   ├── product_tool.py
│   ├── semantic_rag.py
│   └── support_agent.py
├── tests/
├── chroma_db/
├── main.py
├── README.md
├── .gitignore
└── requirements.txt
```

Note: The exact files and folders may vary depending on the final repository version.

## Installation and Setup

### Prerequisites
- Python 3.11 recommended
- Git
- Visual Studio Code (optional)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/nykaa-domain-support-agent.git
cd nykaa-domain-support-agent
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the project

Review the configuration and environment variables required by the application. Add any required API keys to a local `.env` file if the implementation needs them. Never commit credentials or secrets to GitHub.

Ensure the required local datasets and knowledge-base files are available before starting the application.

### 5. Run the backend

Use the FastAPI application entry point configured in the repository. For example, if the application object is `app` in `main.py`:

```powershell
uvicorn main:app --reload
```

The local API will typically be available at:

`http://127.0.0.1:8000`

If enabled, inspect the interactive API documentation at:

`http://127.0.0.1:8000/docs`

### 6. Run the frontend

If the Streamlit interface is implemented in `app.py`, run:

```powershell
python -m streamlit run app.py
```

Replace `app.py` with the actual Streamlit entry-point filename if different.

### 7. Run automated tests

```powershell
python -m unittest discover -s tests -v
```

## Example Use Cases

**Order tracking**

Customer: "Where is my order NK0006?"

Expected workflow: Extract the order ID, retrieve the matching local order record, and return the available order status.

**Product discovery**

Customer: "Find a Vitamin C face serum."

Expected workflow: Search the configured product catalogue and return matching products and their available details.

**Policy questions**

Customer: "What is the return policy?"

Expected workflow: Retrieve relevant information from the configured knowledge base and provide a response grounded in the available policy content.

Examples depend on the datasets and implementation included in the repository.

## Engineering Concepts Demonstrated

- Modular Python application design
- AI agent and tool orchestration concepts
- Intent detection and request routing
- Retrieval-Augmented Generation (RAG)
- Semantic search and vector databases
- REST API development using FastAPI
- Interactive application development using Streamlit
- Unit testing and error handling
- Version control using Git and GitHub

## Current Limitations

- The system depends on the quality and completeness of its configured datasets and knowledge base.
- Local sample data does not represent live Nykaa customer or order information.
- Production deployment would require additional security, authentication, monitoring, scalability, and privacy controls.
- External integrations and live order access are available only if explicitly implemented and configured.
- AI-generated responses should be evaluated for accuracy and groundedness before production use.

## Future Improvements

- Add authentication and role-based access control.
- Improve retrieval evaluation and response-quality testing.
- Integrate a real product catalogue and authorized order-management APIs.
- Add structured logging, monitoring, and performance metrics.
- Containerize the application using Docker.
- Implement CI/CD with automated test execution.
- Add human escalation for unresolved or sensitive customer requests.
- Deploy the application to a suitable cloud platform.

## Disclaimer

This is an independent educational and portfolio project intended to demonstrate AI-powered customer support concepts. It is not an official Nykaa product and is not affiliated with or endorsed by Nykaa. Any sample data should be treated as demonstration data.

## Author

Developed as a portfolio project to explore Python development, AI agents, RAG, semantic retrieval, API development, and automated testing.

GitHub: https://github.com/YOUR-USERNAME
