document.getElementById('scanBtn').onclick = async () => {
    const statusText = document.getElementById('status-text');
    const spinner = document.getElementById('spinner');
    const resultContainer = document.getElementById('result-container');
    const confidenceFill = document.getElementById('confidence-fill');
    const probText = document.getElementById('prob-text');
    const labelText = document.getElementById('label-text');
    const cardType = document.getElementById('card-type');
    
    // UI Elements for Description and Sentences
    const descArea = document.getElementById('description-area');
    const descBox = document.getElementById('description-text');
    const deepDiveArea = document.getElementById('deep-dive-area');
    const sentencesList = document.getElementById('sentences-list');

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        spinner.style.display = "inline-block";
        statusText.innerText = "Extracting email...";

        chrome.tabs.sendMessage(tab.id, { action: "get_content" }, async (res) => {
            if (!res || !res.text) {
                statusText.innerText = "Error: Open an email first!";
                spinner.style.display = "none";
                return;
            }

            statusText.innerText = "Analyzing patterns...";
            
            const response = await fetch("http://127.0.0.1:8000/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email_text: res.text })
            });
            
            const data = await response.json();
            const result = data.overall_result;
            const triggers = data.highlighted_words || [];
            const sentences = data.suspicious_sentences || [];

            // UI Updates
            spinner.style.display = "none";
            statusText.innerText = "Analysis Complete";
            resultContainer.style.display = "block";
            
            // 1. GENUINE SCORE
            const prob = (result.confidence * 100).toFixed(2);
            probText.innerText = `${prob}%`;
            confidenceFill.style.width = `${prob}%`;

            // 2. TRIGGER DESCRIPTION
            if (triggers.length > 0) {
                descArea.style.display = "block";
                descBox.innerHTML = `Suspicious terms found: <span style="color: #ff4b4b;">${triggers.join(', ')}</span>`;
            } else {
                descArea.style.display = "none";
            }

            // 3. SENTENCE DEEP DIVE
            sentencesList.innerHTML = ""; // Clear previous results
            if (sentences.length > 0) {
                deepDiveArea.style.display = "block";
                sentences.forEach(s => {
                    const div = document.createElement('div');
                    div.className = "sentence-item";
                    div.innerHTML = `<i class="fas fa-caret-right"></i> ${s.text}`;
                    sentencesList.appendChild(div);
                });
            } else {
                deepDiveArea.style.display = "none";
            }

            // 4. COLOR CODING & LABELS
            if (result.label.toUpperCase() === "SPAM") {
                cardType.style.borderLeftColor = "#ff4b4b";
                labelText.innerHTML = `<i class="fas fa-exclamation-triangle" style="color:#ff4b4b"></i> HIGH RISK: SPAM`;
                confidenceFill.style.backgroundColor = "#ff4b4b";
                probText.style.color = "#ff4b4b";
            } else {
                cardType.style.borderLeftColor = "#28a745";
                labelText.innerHTML = `<i class="fas fa-check-circle" style="color:#28a745"></i> LOW RISK: SAFE`;
                confidenceFill.style.backgroundColor = "#28a745";
                probText.style.color = "#28a745";
            }
        });
    } catch (err) {
        statusText.innerText = "Connection Error";
        spinner.style.display = "none";
        console.error(err);
    }
};