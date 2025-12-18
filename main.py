from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import nltk
from nltk.tokenize import sent_tokenize
import re

# --- 1. Load Custom Modules ---
try:
    from model import predict_spam
    from explain import explain_email
except ImportError:
    print("Warning: model.py or explain.py not found. Using dummy functions.")
    def predict_spam(text): return {"label": "SAFE", "confidence": 0.0}
    def explain_email(text): return []

# --- 2. Initialize App & NLTK ---
nltk.download("punkt", quiet=True)
app = FastAPI(title="AI Spam & Phishing Detector API")

# --- 3. Add CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailInput(BaseModel):
    email_text: str

# --- 4. Helper: Trust Check (Prevents False Positives) ---
def is_likely_safe(text: str):
    # If the email contains specific legitimate footers, it's often a real alert
    safe_patterns = [
        r"Google LLC", 
        r"1600 Amphitheatre Parkway", 
        r"You received this email to let you know about important changes"
    ]
    for pattern in safe_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

@app.post("/analyze")
async def analyze_email(data: EmailInput):
    raw_email = data.email_text
    # Collapsing whitespace helps BERT models focus on words
    cleaned_email = re.sub(r'\s+', ' ', raw_email).strip()
    
    print(f"\n[DEBUG] Analyzing: {cleaned_email[:100]}...")

    if not cleaned_email or len(cleaned_email) < 10:
        raise HTTPException(status_code=400, detail="Text too short.")

    try:
        # 1. Check for known legitimate Google/System patterns first
        if is_likely_safe(cleaned_email):
            print("[DEBUG] Trust pattern matched. Force SAFE.")
            overall = {"label": "SAFE", "confidence": 0.01}
        else:
            overall = predict_spam(cleaned_email)

        # 2. Sentence-level analysis
        sentences = sent_tokenize(cleaned_email)
        suspicious_sentences = []
        
        for s in sentences:
            if len(s.strip()) > 15: # Ignore very short fragments
                result = predict_spam(s)
                # We use a strict check for individual sentences
                if result.get("label").upper() == "SPAM" and result.get("confidence") > 0.90:
                    suspicious_sentences.append({
                        "text": s,
                        "confidence": result.get("confidence")
                    })

        # 3. Final Decision Override
        # If the model said SPAM but didn't find specific suspicious sentences, 
        # it's likely a false positive based on general "tone".
        if overall["label"] == "SPAM" and len(suspicious_sentences) == 0:
            print("[DEBUG] High risk score but no suspicious sentences. Downgrading to SAFE.")
            overall["label"] = "SAFE"

        explanation = explain_email(cleaned_email)

        return {
            "overall_result": overall,
            "suspicious_sentences": suspicious_sentences,
            "highlighted_words": explanation,
            "status": "success"
        }
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)