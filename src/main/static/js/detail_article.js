function copySummary() {
    const summaryTextElem = document.getElementById("summary-text");

    if (!summaryTextElem) {
        alert("Summary container not found.");
        return;
    }

    const summaryText = summaryTextElem.innerText.trim(); 
    console.log("Extracted summary:", summaryText);

    if (!summaryText) {
        alert("Summary is empty.");
        return;
    }

    navigator.clipboard.writeText(summaryText)
        .then(() => {
            alert("Summary copied to clipboard!");
        })
        .catch(err => {
            console.error("Failed to copy text:", err);
        });
}
// ------------------------
// Chat Functionality (Streaming)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

const userInputElem = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const chatBox = document.getElementById("chat-box");

sendButton.addEventListener("click", sendMessage);
userInputElem.addEventListener("keypress", function(event) {
    if (event.key === "Enter") sendMessage();
});

async function sendMessage() {
    const userInput = userInputElem.value.trim();
    if (!userInput) {
        alert("Message cannot be empty!");
        return;
    }

    userInputElem.disabled = true;
    sendButton.disabled = true;

    chatBox.innerHTML += `<div class="chat-message user-message">${userInput}</div>`;

    let loadingDiv = document.createElement("div");
    loadingDiv.className = "chat-message ai-message loading";
    loadingDiv.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch(articleChatUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ message: userInput })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        chatBox.removeChild(loadingDiv);
        let aiMessageDiv = document.createElement("div");
        aiMessageDiv.className = "chat-message ai-message";
        let aiTextSpan = document.createElement("span");
        aiTextSpan.className = "ai-response";
        aiMessageDiv.appendChild(aiTextSpan);
        chatBox.appendChild(aiMessageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        let partialData = "";
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            partialData += decoder.decode(value, { stream: true });

            const sseMessages = partialData.split("\n\n");
            partialData = sseMessages.pop();

            sseMessages.forEach(msg => {
                if (msg.startsWith("data: ")) {
                    let chunk = msg.slice("data: ".length);
                    aiTextSpan.textContent += chunk;
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            });
        }

    } catch (error) {
        chatBox.removeChild(loadingDiv);
        chatBox.innerHTML += `<div class="chat-message error-message"><span>Error:</span> ${error.message}</div>`;
    }

    userInputElem.disabled = false;
    sendButton.disabled = false;
    userInputElem.value = "";
    userInputElem.focus();
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ------------------------
// Flashcard Functionality
document.addEventListener("DOMContentLoaded", function () {
    let allFlashcards = [];
    let currentFlashcards = [];
    let currentCardIndex = 0;
    let knownCount = 0;
    let unknownFlashcards = [];

    function fetchFlashcardsFromServer() {
        fetch("/main/generate_flashcards/article_text/")
            .then(response => response.json())
            .then(data => {
                if (data.flashcards) {
                    generateFlashcardsFromData(data.flashcards);
                } else {
                    throw new Error("No flashcards returned");
                }
            })
            .catch(error => {
                console.error("Error fetching flashcards:", error);
                document.getElementById("flashcard-display").innerHTML = `
                    <div class="alert alert-warning">
                        Unable to load flashcards. Please try again.
                    </div>`;
            });
    }

    function generateFlashcardsFromData(flashcards) {
        allFlashcards = flashcards;

        const selectedCount = parseInt(document.getElementById("flashcard-count").value);
        const shuffled = allFlashcards.sort(() => 0.5 - Math.random()).slice(0, selectedCount);

        currentFlashcards = shuffled;
        currentCardIndex = 0;
        knownCount = 0;
        unknownFlashcards = [];

        showFlashcard();
        document.getElementById("results-section").classList.add("d-none");
    }

    function showFlashcard() {
        const flashcardFront = document.getElementById("flashcard-front");
        const flashcardBack = document.getElementById("flashcard-back");

        if (currentCardIndex >= currentFlashcards.length) {
            showResults();
            return;
        }

        const card = currentFlashcards[currentCardIndex];
        flashcardFront.innerText = card.question;
        flashcardBack.innerText = card.answer;
        flashcardBack.classList.add("d-none");
    }

    function flipCard() {
        document.getElementById("flashcard-back").classList.toggle("d-none");
    }

    function markAsKnown() {
        knownCount++;
        currentCardIndex++;
        showFlashcard();
    }

    function markAsUnknown() {
        unknownFlashcards.push(currentFlashcards[currentCardIndex]);
        currentCardIndex++;
        showFlashcard();
    }

    function showResults() {
        const total = currentFlashcards.length;
        const percentage = ((knownCount / total) * 100).toFixed(2);
        document.getElementById("results-text").innerHTML = `
            You knew <strong>${knownCount}</strong> out of <strong>${total}</strong> flashcards.
            <br>Success rate: <strong>${percentage}%</strong>.`;
        document.getElementById("results-section").classList.remove("d-none");
    }

    function restartFlashcards() {
        generateFlashcardsFromData(allFlashcards);
    }

    function continueLearning() {
        currentFlashcards = [...unknownFlashcards];
        currentCardIndex = 0;
        knownCount = 0;
        unknownFlashcards = [];
        showFlashcard();
        document.getElementById("results-section").classList.add("d-none");
    }

    window.fetchFlashcardsFromServer = fetchFlashcardsFromServer;
    window.flipCard = flipCard;
    window.markAsKnown = markAsKnown;
    window.markAsUnknown = markAsUnknown;
    window.restartFlashcards = restartFlashcards;
    window.continueLearning = continueLearning;
});
