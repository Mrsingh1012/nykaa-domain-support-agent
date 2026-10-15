
"""
E-Commerce AI Assistant
Streamlit frontend connected to FastAPI.
"""
import requests
import streamlit as st

st.set_page_config(
    page_title="Nykaa AI Support Agent",
    page_icon="🛍️",
    layout="centered",
)

# ---------------- CONFIGURATION ----------------

API_URL = "http://127.0.0.1:8000/support"
API_TIMEOUT = 30


# ---------------- PAGE SETUP ----------------

st.title("🛍️ Nykaa AI Support Agent")
st.caption("Product Help | Order Tracking | Returns & Refunds")


# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------- API FUNCTION ----------------

def ask_support_agent(question: str) -> str:
    """Send a question to FastAPI and return its answer."""

    try:
        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=API_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Invalid response format from API.")

        answer = data.get("answer")

        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("API returned an empty or invalid answer.")

        return answer.strip()

    except requests.Timeout as exc:
        raise RuntimeError(
            "Request timed out. Please try again."
        ) from exc

    except requests.ConnectionError as exc:
        raise RuntimeError(
            "Cannot connect to FastAPI. Start the backend on port 8000."
        ) from exc

    except requests.HTTPError as exc:
        status = (
            exc.response.status_code
            if exc.response is not None
            else "unknown"
        )
        raise RuntimeError(
            f"FastAPI returned HTTP {status}. Check the backend logs."
        ) from exc

    except ValueError as exc:
        raise RuntimeError(
            "Invalid JSON or answer received from FastAPI."
        ) from exc

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Request failed: {exc}"
        ) from exc


# ---------------- DISPLAY CHAT HISTORY ----------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("error"):
            st.error(message["content"])
        else:
            st.markdown(message["content"])


# ---------------- CUSTOMER INPUT ----------------

prompt = st.chat_input(
    "Ask about products, orders or returns..."
)

if prompt and prompt.strip():
    question = prompt.strip()

    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Support agent is working..."):
            try:
                answer = ask_support_agent(question)

                st.markdown(answer)
                st.caption("Agent: Support")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                })

            except RuntimeError as exc:
                error_message = str(exc)
                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "error": True,
                })
