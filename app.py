from fastapi import FastAPI
from pydantic import BaseModel
import nltk
from nltk.tokenize import sent_tokenize

from model import predict_spam
from explain import explain_email

nltk.download("punkt")

app = FastAPI(title="AI Spam & Phishing Detector")

class EmailInput(BaseModel):
    email_text: str

@app.post("/analyze")
def analyze_email(data: EmailInput):
    email = data.email_text

    overall = predict_spam(email)

    sentences = sent_tokenize(email)
    suspicious_sentences = []

    for s in sentences:
        result = predict_spam(s)
        if result["label"] == "SPAM":
            suspicious_sentences.append(s)

    explanation = explain_email(email)

    return {
        "overall_result": overall,
        "suspicious_sentences": suspicious_sentences,
        "highlighted_words": explanation
    }
