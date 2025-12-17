import os
import re
import streamlit as st
from transformers import pipeline

# ---------------- SPEED & WARNINGS FIX ----------------
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Spam Detection",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- SENTENCE SPLITTER (NO NLTK) ----------------
def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]

# ---------------- LOAD FAST TRANSFORMER MODEL ----------------
@st.cache_resource
def load_model():
    return pipeline(
        "text-classification",
        model="prajjwal1/bert-tiny",   # FAST transformer
        return_all_scores=True,
        framework="pt"                # PyTorch only
    )

classifier = load_model()

# ---------------- PREDICTION FUNCTION ----------------
def predict(text):
    result = classifier(text)[0]
    spam_score = result[0]["score"]
    ham_score = result[1]["score"]
    label = "SPAM" if spam_score > ham_score else "NOT SPAM"
    return spam_score, label

# ---------------- UI HEADER ----------------
st.markdown(
    "<h1 style='text-align:center;'>🛡️ AI Spam & Phishing Detection System</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:gray;'>Transformer-based • Fast • Sentence-level Analysis</p>",
    unsafe_allow_html=True
)

# ---------------- INPUT ----------------
st.subheader("📩 Paste Email Content")
email_text = st.text_area(
    "",
    height=220,
    placeholder="Paste the complete email here..."
)

# ---------------- ANALYZE BUTTON ----------------
if st.button("🔍 Analyze Email"):

    if not email_text.strip():
        st.warning("⚠ Please paste an email first.")
    else:
        spam_score, label = predict(email_text)

        st.divider()
        col1, col2 = st.columns(2)

        # -------- OVERALL RESULT --------
        with col1:
            st.subheader("📊 Overall Result")
            if label == "SPAM":
                st.error(f"🚨 SPAM DETECTED ({round(spam_score*100, 2)}%)")
            else:
                st.success(f"✅ NOT SPAM ({round(spam_score*100, 2)}%)")

            st.progress(spam_score)

        # -------- SENTENCE LEVEL --------
        with col2:
            st.subheader("🚩 Suspicious Sentences")
            sentences = split_sentences(email_text)
            found = False

            for s in sentences:
                s_score, s_label = predict(s)
                if s_label == "SPAM":
                    st.warning(s)
                    found = True

            if not found:
                st.success("No suspicious sentences detected")

        st.divider()

        # -------- EXPLANATION --------
        st.subheader("🧠 Why this email looks suspicious")
        keywords = [
            "urgent", "verify", "click", "reward", "account",
            "locked", "won", "prize", "immediately", "suspended",
            "limited", "confirm"
        ]

        detected = [k for k in keywords if k in email_text.lower()]

        if detected:
            for k in detected:
                st.markdown(f"- 🔴 **{k}**")
        else:
            st.markdown("✔ No strong spam indicators detected")
