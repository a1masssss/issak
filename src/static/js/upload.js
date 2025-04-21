document.addEventListener('DOMContentLoaded', function() {
    const loadingIndicator = document.getElementById('loading-indicator');

    // Loading indicator 
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function() {
            loadingIndicator.classList.remove("d-none");
            
            // Disable submit button to prevent multiple submissions
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
        });
    });

    const contentTabs = document.querySelectorAll(".nav-link");
    contentTabs.forEach(tab => {
        tab.addEventListener("click", function(event) {
            event.preventDefault();

            // Remove 'active' class from all tabs
            contentTabs.forEach(t => t.classList.remove("active"));
            this.classList.add("active");

            // Hide all tab panes
            document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("show", "active"));

            // Show the selected tab
            const targetPane = document.querySelector(this.getAttribute("href"));
            targetPane.classList.add("show", "active");
        });
    });

    // Character Counter for Text Input with enhanced styling
    const textInput = document.querySelector("#text-form textarea");
    const charCounterContainer = document.createElement("div");
    charCounterContainer.className = "mt-3 text-end";
    charCounterContainer.innerHTML = `<div class="badge bg-light text-dark p-2 fs-6"><span id="char-count">10000</span> characters left</div>`;

    if (textInput) {
        textInput.parentNode.appendChild(charCounterContainer);

        textInput.addEventListener("input", function() {
            const maxChars = 10000;
            let remaining = maxChars - textInput.value.length;
            const charCount = document.getElementById("char-count");
            charCount.textContent = remaining.toLocaleString();
            
            // Change color based on remaining characters
            if (remaining < 1000) {
                charCount.style.color = '#dc3545';
            } else if (remaining < 3000) {
                charCount.style.color = '#fd7e14';
            } else {
                charCount.style.color = '#212529';
            }
        });
    }
});