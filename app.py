import streamlit as st
import requests
import os

# ------------------ SETTINGS ------------------
st.set_page_config(page_title="LawGuide", layout="centered")
st.title("⚖️ LawGuide - Your Legal AI Assistant (India)")
st.markdown("💬 Ask your legal questions in **Hinglish** (Hindi + English mix).")

# ------------------ CUSTOM CSS ------------------
st.markdown("""
    <style>
    .stChatMessage { background-color: #1e1e1e; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    .stTextInput > div > input { border: 1px solid red; }
    </style>
""", unsafe_allow_html=True)

# ------------------ OPENROUTER CONFIG ------------------
MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Use environment variable for API key
OPENROUTER_API_KEY = os.getenv("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")

if not OPENROUTER_API_KEY:
    st.error("❌ API key not found. Please add it in your Render environment variables as 'API_KEY'.")
    st.stop()

# ------------------ SESSION STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ DISPLAY PAST MESSAGES ------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ USER INPUT ------------------
user_input = st.chat_input("Ask your legal question here...")

if user_input:
    # Show user input
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call OpenRouter API
    with st.chat_message("assistant"):
        with st.spinner("Thinking like a lawyer..."):
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": MODEL,
                "messages": st.session_state.messages,
                "temperature": 0.7
            }

            try:
                response = requests.post(API_URL, headers=headers, json=payload)
                response.raise_for_status()
                reply = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                reply = f"❌ Error: {str(e)}"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
