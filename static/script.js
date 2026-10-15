const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const chatMessages = document.getElementById("chatMessages");
const sendButton = document.getElementById("sendButton");

function addMessage(text, sender) {
    const message = document.createElement("div");

    message.classList.add("message", sender);

    // Use textContent to safely display the response.
    message.textContent = text;

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return message;
}

async function sendQuestion(question) {
    const cleanQuestion = question.trim();

    if (!cleanQuestion || sendButton.disabled) {
        return;
    }

    addMessage(cleanQuestion, "user");

    questionInput.value = "";
    sendButton.disabled = true;
    sendButton.textContent = "Sending...";

    const loadingMessage = addMessage(
        "Please wait, finding your answer...",
        "bot"
    );

    try {
        const response = await fetch("/support", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: cleanQuestion
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "The support request failed."
            );
        }

        loadingMessage.textContent = data.answer;

    } catch (error) {
        loadingMessage.textContent =
            "Sorry, I could not process your request. " +
            "Please try again. Details: " + error.message;

    } finally {
        sendButton.disabled = false;
        sendButton.textContent = "Send";
        questionInput.focus();
    }
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await sendQuestion(questionInput.value);
});

document.querySelectorAll("[data-question]").forEach((button) => {
    button.addEventListener("click", async () => {
        await sendQuestion(button.dataset.question);
    });
});