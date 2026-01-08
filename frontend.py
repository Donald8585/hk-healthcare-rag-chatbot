import streamlit as st
import requests
import json

# Page config
st.set_page_config(
    page_title="HK Healthcare RAG Chatbot",
    page_icon="🏥",
    layout="wide"
)

# Title
st.title("🏥 Hong Kong Healthcare RAG Chatbot")
st.markdown("Ask questions about Hong Kong healthcare policies, statistics, and facilities.")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This chatbot uses:
    - **616 documents** from HK healthcare sources
    - **1785 semantic chunks** in vector DB
    - **Ollama llama3.2:3b** for generation
    - **Local embeddings** (no API costs)
    """)

    st.header("Example Questions")
    st.markdown("""
    - How many doctors per 1000 population?
    - What are the life expectancy rates?
    - List hospitals in Kowloon
    - Hospital Authority governance structure
    """)

    # API status check
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.code(source, language="text")

# User input
if prompt := st.chat_input("Ask a question about HK healthcare..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                response = requests.post(
                    "http://localhost:8000/query",
                    json={"question": prompt},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data.get("sources", [])

                    st.markdown(answer)

                    # Show sources
                    if sources:
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.code(source, language="text")

                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"Error: {response.status_code}")

            except Exception as e:
                st.error(f"Connection error: {str(e)}")
                st.info("Make sure the API is running: `uvicorn app:app --port 8000`")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Built with LangChain, Chroma, and Ollama | Data: Hospital Authority & HK Gov Open Data</small>
</div>
""", unsafe_allow_html=True)
