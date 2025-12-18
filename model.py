import torch
from transformers import pipeline

MODEL_NAME = "cybersectony/phishing-email-detection-distilbert_v2.1"

classifier = pipeline(
    "text-classification", 
    model=MODEL_NAME, 
    top_k=None 
)

def predict_spam(text):
    if not text.strip():
        return {"label": "SAFE", "confidence": 0.0, "words": []}

    results = classifier(text[:512])[0]
    
    spam_score = 0.0
    for res in results:
        if res['label'] == 'LABEL_1':
            spam_score = res['score']

    label = "SPAM" if spam_score > 0.70 else "SAFE"

    # --- IMPROVED DESCRIPTION LOGIC ---
    risk_triggers = ["verify", "urgent", "login", "account", "suspended", "security", "click", "bank", "action required", "unusual"]
    
    # Use lowercase for searching to ensure matches
    text_lower = text.lower()
    found_description = []
    
    for word in risk_triggers:
        if word in text_lower:
            found_description.append(word)

    return {
        "label": label,
        "confidence": float(spam_score),
        "words": found_description  # This is the list of triggers
    }