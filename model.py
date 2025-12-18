from transformers import pipeline

# Dedicated model for Email Phishing & Spam detection
MODEL_NAME = "cybersectony/phishing-email-detection-distilbert_v2.1"

classifier = pipeline(
    "text-classification",
    model=MODEL_NAME,
    return_all_scores=True
)

def predict_spam(text):
    if not text.strip():
        return {"spam_probability": 0.0, "label": "SAFE"}

    # Run inference
    results = classifier(text)[0]
    
    # Map the model-specific labels to your UI labels
    # Most spam models use LABEL_0 (Safe) and LABEL_1 (Spam)
    # Check your model's card, but usually higher index = malicious
    spam_score = results[1]["score"] 
    ham_score = results[0]["score"]

    return {
        "spam_probability": round(spam_score * 100, 2),
        "label": "SPAM" if spam_score > 0.5 else "NOT SPAM"
    }