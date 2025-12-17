from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    return_all_scores=True
)

def predict_spam(text):
    result = classifier(text)[0]
    spam_score = result[0]["score"]
    ham_score = result[1]["score"]

    return {
        "spam_probability": round(spam_score * 100, 2),
        "label": "SPAM" if spam_score > ham_score else "NOT SPAM"
    }
