const API_URL = "http://127.0.0.1:8000/support";

const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question");
const chatBox = document.getElementById("chat-box");
const sendButton = document.getElementById("send-button");

function addMessage(text, sender) {
    const message = document.createElement("div");

    message.className = `message ${sender}`;

    // textContent prevents the response from being interpreted as HTML.
    message.textContent = text;

    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;

    return message;
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    addMessage(question, "user");

    questionInput.value = "";
    sendButton.disabled = true;

    const loadingMessage = addMessage(
        "⏳ Searching the knowledge base and preparing your answer...",
        "bot"
    );
    try {
        const response = await fetch(API_URL, {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail
                    ? JSON.stringify(data.detail)
                    : `Request failed: ${response.status}`
            );
        }

        loadingMessage.textContent =
            data.answer || "No answer was returned by the server.";

    } catch (error) {
        console.error("Support API error:", error);

        loadingMessage.textContent =
            "Unable to connect to the support server. " +
            "Please check that the backend is running and try again.";
    } finally {
        sendButton.disabled = false;
        questionInput.focus();
    }
});