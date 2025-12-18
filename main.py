from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import nltk
from nltk.tokenize import sent_tokenize

# Assuming these are your custom modules
try:
    from model import predict_spam
    from explain import explain_email
except ImportError:
    # Placeholder for testing if files aren't present
    def predict_spam(text): return {"label": "SAFE", "confidence": 0.0}
    def explain_email(text): return []

# Download necessary NLTK data once at startup
nltk.download("punkt", quiet=True)

app = FastAPI(title="AI Spam & Phishing Detector API")

class EmailInput(BaseModel):
    email_text: str

@app.post("/analyze")
async def analyze_email(data: EmailInput):
    email = data.email_text.strip()
    
    if not email:
        raise HTTPException(status_code=400, detail="Email text cannot be empty.")

    try:
        # 1. Overall prediction
        overall = predict_spam(email)

        # 2. Sentence-level analysis
        sentences = sent_tokenize(email)
        suspicious_sentences = []
        for s in sentences:
            result = predict_spam(s)
            if result.get("label") == "SPAM":
                suspicious_sentences.append(s)

        # 3. Explainability (keyword highlighting)
        explanation = explain_email(email)

        return {
            "overall_result": overall,
            "suspicious_sentences": suspicious_sentences,
            "highlighted_words": explanation,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))