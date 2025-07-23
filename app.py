import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="LawGuide AI", layout="centered")

st.title("⚖️ LawGuide AI")
st.caption("Chat with a Hinglish-speaking Indian legal assistant powered by OpenRouter")

# 💡 Replace this with your real OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    st.error("🚨 Please set your OpenRouter API Key as an environment variable or secret.")
    st.stop()

MODEL = "mistralai/mistral-7b-instruct"

# 🧠 Session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful, friendly Hinglish-speaking legal assistant for Indian law. Answer clearly and correctly with legal sections, case laws, or advice when needed."}
    ]

# 💬 Show chat history
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 📥 Take user prompt
user_input = st.chat_input("Ask a legal question...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Typing animation
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        # 🔁 Call OpenRouter API with streaming
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": st.session_state.messages[-10:],  # Limit history
                "stream": True,
            },
            stream=True
        )

        # 🧠 Parse stream
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8").replace("data: ", "")
                if decoded.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(decoded)
                    delta = data["choices"][0]["delta"].get("content", "")
                    full_response += delta
                    placeholder.markdown(full_response + "▌")
                except Exception as e:
                    continue

        placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
