import shap
from transformers import pipeline

# Initialize the pipeline
# Note: Using a specific model for spam if available is better, 
# but distilbert-base-uncased-finetuned-sst-2-english works for testing.
pipe = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    return_all_scores=True
)

# Initialize the explainer
# We specify the model and the masker (which tells SHAP how to hide words)
explainer = shap.Explainer(pipe)

def explain_email(text):
    if not text.strip():
        return []

    # Get SHAP values
    shap_values = explainer([text])
    
    # SHAP for text returns an object where:
    # .data[0] are the tokens/words
    # .values[0] are the importance scores for each token
    words = shap_values.data[0]
    
    # We look at the scores for the 'POSITIVE' (or SPAM) class.
    # If your model has 2 classes, index [:, 1] usually targets the second label.
    scores = shap_values.values[0][:, 1] 

    suspicious_words = []
    
    for w,s in zip(words, scores):
        # Clean the word (remove whitespace markers and special tokens)
        clean_word = str(w).strip().replace('Ġ', '')
        
        # Filter: Only keep meaningful words with high impact scores
        if s > 0.15 and clean_word not in ["[CLS]", "[SEP]", ""]:
            suspicious_words.append(clean_word)

    # Return unique words, limited to the top 12
    return list(dict.fromkeys(suspicious_words))[:12]