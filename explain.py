import shap
from transformers import pipeline

pipe = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

explainer = shap.Explainer(pipe)

def explain_email(text):
    shap_values = explainer([text])
    words = shap_values.data[0]
    scores = shap_values.values[0]

    suspicious_words = []
    for w, s in zip(words, scores):
        if s > 0.15:
            suspicious_words.append(w)

    return list(set(suspicious_words[:12]))
