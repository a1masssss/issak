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

// Get CSRF token from cookies for Django security
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

// Elements
const userInputElem = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const chatBox = document.getElementById("chat-box");

// Send message when button is clicked
sendButton.addEventListener("click", sendMessage);

// Allow sending message by pressing Enter
userInputElem.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

async function sendMessage() {
    const userInput = userInputElem.value.trim();
    if (!userInput) {
        alert("Message cannot be empty!");
        return;
    }

    userInputElem.disabled = true;
    sendButton.disabled = true;

    chatBox.innerHTML += `
        <div class="chat-message user-message">
            ${userInput}
        </div>`;

    let loadingDiv = document.createElement("div");
    loadingDiv.className = "chat-message ai-message loading";
    loadingDiv.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch(youtubeChatUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ message: userInput })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }

        // Read streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        chatBox.removeChild(loadingDiv);

        // Create a new AI response container
        let aiMessageDiv = document.createElement("div");
        aiMessageDiv.className = "chat-message ai-message";

        // Create a span for new AI response
        let aiTextSpan = document.createElement("span");
        aiTextSpan.className = "ai-response"; // No fixed ID to avoid duplication issues
        aiMessageDiv.appendChild(aiTextSpan);

        chatBox.appendChild(aiMessageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        let partialData = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                break;
            }
            partialData += decoder.decode(value, { stream: true });

            const sseMessages = partialData.split("\n\n");
            partialData = sseMessages.pop();

            sseMessages.forEach(msg => {
                if (msg.startsWith("data: ")) {
                    let chunk = msg.slice("data: ".length);
                    
                    // Append new response instead of modifying previous AI responses
                    aiTextSpan.textContent += chunk;
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            });
        }

    } catch (error) {
        chatBox.removeChild(loadingDiv);
        chatBox.innerHTML += `
            <div class="chat-message error-message">
                <span>Error:</span> ${error.message}
            </div>`;
        console.error("Error:", error);
    }

    userInputElem.disabled = false;
    sendButton.disabled = false;
    userInputElem.value = "";
    userInputElem.focus();
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.addEventListener("DOMContentLoaded", function () {
    // Global flashcard management
    let allFlashcards = [];
    let currentFlashcards = [];
    let currentCardIndex = 0;
    let knownCount = 0;
    let unknownFlashcards = [];

    // Fetch flashcards from server
    function fetchFlashcardsFromServer() {
        fetch("/main/generate_flashcards/youtube_text/")
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

    // Generate flashcards based on data
    function generateFlashcardsFromData(flashcards) {
        allFlashcards = flashcards;

        const flashcardCountSelect = document.getElementById("flashcard-count");
        const selectedCount = parseInt(flashcardCountSelect.value);

        const shuffledFlashcards = allFlashcards
            .sort(() => 0.5 - Math.random())
            .slice(0, selectedCount);

        currentFlashcards = shuffledFlashcards;
        currentCardIndex = 0;
        knownCount = 0;
        unknownFlashcards = [];

        showFlashcard();
        document.getElementById("results-section").classList.add("d-none");
    }

    // Show current flashcard
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

    // Flip card
    function flipCard() {
        document.getElementById("flashcard-back").classList.toggle("d-none");
    }

    // Mark as known
    function markAsKnown() {
        knownCount++;
        currentCardIndex++;
        showFlashcard();
    }

    // Mark as unknown
    function markAsUnknown() {
        unknownFlashcards.push(currentFlashcards[currentCardIndex]);
        currentCardIndex++;
        showFlashcard();
    }

    // Show results
    function showResults() {
        const resultsSection = document.getElementById("results-section");
        const resultsText = document.getElementById("results-text");
        const totalCards = currentFlashcards.length;
        const knownPercentage = ((knownCount / totalCards) * 100).toFixed(2);

        resultsText.innerHTML = `
            You knew <strong>${knownCount}</strong> out of <strong>${totalCards}</strong> flashcards.
            <br>Success rate: <strong>${knownPercentage}%</strong>.
        `;
        resultsSection.classList.remove("d-none");
    }

    // Restart all flashcards
    function restartFlashcards() {
        generateFlashcardsFromData(allFlashcards);
    }

    // Continue learning only unknown cards
    function continueLearning() {
        currentFlashcards = [...unknownFlashcards];
        currentCardIndex = 0;
        knownCount = 0;
        unknownFlashcards = [];
        showFlashcard();
        document.getElementById("results-section").classList.add("d-none");
    }

    // Expose globally
    window.fetchFlashcardsFromServer = fetchFlashcardsFromServer;
    window.flipCard = flipCard;
    window.markAsKnown = markAsKnown;
    window.markAsUnknown = markAsUnknown;
    window.restartFlashcards = restartFlashcards;
    window.continueLearning = continueLearning;
});

