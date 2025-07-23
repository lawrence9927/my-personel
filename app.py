import streamlit as st
import requests
import os
import uuid

# ------------------ SETTINGS ------------------
st.set_page_config(page_title="LawGuide", layout="wide")
st.title("⚖️ LawGuide - Your Legal AI Assistant (India)")
st.markdown("💬 Ask your legal questions in **Hinglish** (Hindi + English mix).")

# ------------------ OPENROUTER CONFIG ------------------
MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    st.error("❌ API key not found. Please set it in your Render environment as 'API_KEY'")
    st.stop()

# ------------------ SIDEBAR & SAVED CHATS ------------------
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat_id" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = chat_id
    st.session_state.chat_sessions[chat_id] = []

# Sidebar: list of previous chats
with st.sidebar:
    st.markdown("### 📁 Saved Chats")
    for cid in st.session_state.chat_sessions.keys():
        if st.button(f"Chat {cid[:5]}", key=cid):
            st.session_state.current_chat_id = cid

    if st.button("🆕 New Chat"):
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.chat_sessions[new_id] = []

# Get current chat
chat_id = st.session_state.current_chat_id
messages = st.session_state.chat_sessions[chat_id]

# ------------------ DISPLAY CHAT ------------------
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ INPUT ------------------
user_input = st.chat_input("Ask your legal question here...")

if user_input:
    messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking like a lawyer..."):
            try:
                response = requests.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": MODEL,
                        "messages": messages,
                        "temperature": 0.7
                    },
                    timeout=15  # slight improvement in speed
                )
                response.raise_for_status()
                reply = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                reply = "⚠️ Something went wrong while getting a reply."

            messages.append({"role": "assistant", "content": reply})
            st.markdown(reply)
