import shap
from transformers import pipeline

# 1. USE THE SAME MODEL AS model.py
MODEL_NAME = "cybersectony/phishing-email-detection-distilbert_v2.1"

pipe = pipeline(
    "text-classification",
    model=MODEL_NAME,
    return_all_scores=True
)

# 2. Use a simpler explainer for faster responses in the Edge popup
explainer = shap.Explainer(pipe)

def explain_email(text):
    if not text.strip() or len(text.strip()) < 10:
        return []

    try:
        # Get SHAP values for the first 128 tokens to save memory
        shap_values = explainer([text[:512]]) 
        
        words = shap_values.data[0]
        # Index [:, 1] targets the 'Phishing/Spam' class in your model
        scores = shap_values.values[0][:, 1] 

        suspicious_words = []
        for w, s in zip(words, scores):
            clean_word = str(w).strip().replace('Ġ', '').replace('##', '')
            
            # 3. INCREASE SCORE THRESHOLD
            # Only highlight words that significantly push the score toward SPAM
            if s > 0.4 and len(clean_word) > 2: 
                if clean_word.lower() not in ["[cls]", "[sep]", "the", "and", "your"]:
                    suspicious_words.append(clean_word)

        return list(dict.fromkeys(suspicious_words))[:10]
    except Exception as e:
        print(f"SHAP Error: {e}")
        return []