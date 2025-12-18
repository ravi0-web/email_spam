import os
import re
import streamlit as st
from transformers import pipeline

# ---------------- PERFORMANCE & ENVIRONMENT ----------------
# Disables warnings for tokenizers to keep logs clean
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Spam Detection",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- UTILITIES ----------------
def split_sentences(text):
    """Splits text into sentences using regex for speed (no NLTK required)."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]

@st.cache_resource
def load_model():
    """Loads and caches the model to memory for instant reuse."""
    # Using a specialized spam model for better accuracy than SST-2
    return pipeline(
        "text-classification",
        model="mrm8488/bert-tiny-finetuned-sms-spam-detection", 
        return_all_scores=True,
        framework="pt"
    )

classifier = load_model()

def predict(text):
    """Runs inference and returns score/label."""
    if not text.strip():
        return 0.0, "NOT SPAM"
    
    result = classifier(text)[0]
    # BERT models usually: index 0 = Ham, index 1 = Spam
    # Check score for Spam (LABEL_1 or similar)
    spam_score = result[1]["score"]
    label = "SPAM" if spam_score > 0.5 else "NOT SPAM"
    return spam_score, label

# ---------------- UI STYLING ----------------
st.markdown(
    "<h1 style='text-align:center;'>🛡️ AI Spam & Phishing Detection</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:gray;'>Deep Learning Analysis • Sentence-Level Scrutiny • Real-time Insights</p>",
    unsafe_allow_html=True
)
st.divider()

# ---------------- MAIN LAYOUT ----------------
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📩 Email Input")
    email_text = st.text_area(
        "Paste the content of the email you want to analyze:",
        height=300,
        placeholder="e.g., Dear user, your account has been suspended. Click here to verify..."
    )
    analyze_btn = st.button("🔍 Run Full Analysis", use_container_width=True)

with col_output:
    if analyze_btn:
        if not email_text.strip():
            st.warning("⚠ Please paste an email first.")
        else:
            with st.spinner("Analyzing patterns..."):
                spam_score, label = predict(email_text)

                # 📊 Result Card
                st.subheader("📊 Overall Assessment")
                if label == "SPAM":
                    st.error(f"### 🚨 HIGH RISK: {label}")
                    st.metric("Spam Probability", f"{round(spam_score*100, 2)}%")
                else:
                    st.success(f"### ✅ LOW RISK: {label}")
                    st.metric("Spam Probability", f"{round(spam_score*100, 2)}%")
                
                st.progress(spam_score)

                # 🧠 Trigger Keywords
                st.subheader("🧠 Risk Indicators")
                keywords = [
                    "urgent", "verify", "click", "reward", "account", "password",
                    "locked", "won", "prize", "immediately", "suspended", "bank",
                    "limited", "confirm", "login", "gift card"
                ]
                detected = [k for k in keywords if k in email_text.lower()]
                
                if detected:
                    st.write("Found suspicious patterns in wording:")
                    # Display keywords as badges
                    cols = st.columns(len(detected) if len(detected) < 4 else 4)
                    for i, k in enumerate(detected):
                        cols[i % 4].markdown(f"🏷️ `{k}`")
                else:
                    st.info("No common phishing keywords found.")

# ---------------- SENTENCE LEVEL (FULL WIDTH) ----------------
if analyze_btn and email_text.strip():
    st.divider()
    st.subheader("🚩 Sentence-Level Deep Dive")
    sentences = split_sentences(email_text)
    
    found_suspicious = False
    for s in sentences:
        s_score, s_label = predict(s)
        if s_label == "SPAM":
            st.warning(f"**Potential Issue:** {s} `(Score: {round(s_score, 2)})`")
            found_suspicious = True
    
    if not found_suspicious:
        st.success("All individual sentences appear safe.")

st.divider()
st.caption("Disclaimer: This tool uses a lightweight BERT model for demonstration. Always verify sensitive emails manually.")