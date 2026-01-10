import streamlit as st
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3  # CRITICAL: Fix for Chroma on Streamlit Cloud

from langchain_huggingface import HuggingFaceEndpoint
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA  # Updated import path
from langchain_core.prompts import PromptTemplate  # Updated import path
import os

# Page config
st.set_page_config(
    page_title="HK Healthcare RAG Chatbot",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hong Kong Healthcare Information Assistant")
st.markdown("Ask questions about Hong Kong healthcare services, hospitals, and medical information.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for API keys and settings
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("### 🆓 100% FREE APIs - No Credit Card!")

    # Get API keys from secrets or user input
    hf_api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
    cohere_api_key = st.secrets.get("COHERE_API_KEY", "")

    if not hf_api_key:
        hf_api_key = st.text_input(
            "HuggingFace API Token", 
            type="password", 
            help="Get FREE at huggingface.co/settings/tokens"
        )

    if not cohere_api_key:
        cohere_api_key = st.text_input(
            "Cohere API Key", 
            type="password", 
            help="Get FREE at dashboard.cohere.com/api-keys"
        )

    model_choice = st.selectbox(
        "LLM Model",
        [
            "mistralai/Mistral-7B-Instruct-v0.2",
            "meta-llama/Llama-2-7b-chat-hf",
            "HuggingFaceH4/zephyr-7b-beta",
            "google/flan-t5-xxl"
        ],
        help="All FREE on HuggingFace!"
    )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max Tokens", 256, 2048, 512, 128)

    st.markdown("---")
    st.markdown("### 📊 Model Info")
    st.markdown(f"**Provider**: 🤗 HuggingFace (FREE)")
    st.markdown(f"**Embeddings**: Cohere (FREE)")
    st.markdown(f"**Cost**: $0/month! 🎉")

    st.markdown("---")
    st.markdown("### 🔑 Get FREE API Keys:")
    st.markdown("1. [HuggingFace](https://huggingface.co/settings/tokens)")
    st.markdown("2. [Cohere](https://dashboard.cohere.com/api-keys)")
    st.markdown("Both work in Hong Kong! 🇭🇰")

@st.cache_resource
def initialize_rag_chain(hf_key, cohere_key, model_name, temp, max_tok):
    """Initialize RAG chain with HuggingFace LLM and Cohere embeddings"""

    try:
        # Initialize HuggingFace LLM
        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            huggingfacehub_api_token=hf_key,
            temperature=temp,
            max_new_tokens=max_tok,
            top_k=50,
            top_p=0.95
        )

        # Initialize Cohere embeddings (FREE tier!)
        embeddings = CohereEmbeddings(
            cohere_api_key=cohere_key,
            model="embed-english-light-v3.0"  # FREE model
        )

        # Load Chroma vector store
        persist_directory = "./chroma_db"

        if not os.path.exists(persist_directory):
            st.error(f"❌ Chroma DB not found at {persist_directory}.")
            st.info("""
            ### 📦 First time setup:
            1. Create a `data/` folder and add your HK healthcare PDFs/TXT files
            2. Run: `python ingest_data.py`
            3. This creates the `chroma_db/` folder with embeddings
            4. Then run Streamlit again!
            """)
            return None

        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )

        # Create custom prompt
        prompt_template = """You are a helpful Hong Kong healthcare information assistant. 
Use the following context to answer the question accurately and concisely.
If you don't know the answer, say "I don't have information about that in my knowledge base."

Context: {context}

Question: {question}

Helpful Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        # Create RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )

        return qa_chain

    except Exception as e:
        st.error(f"❌ Initialization error: {str(e)}")
        return None

# Check if API keys are provided
if not hf_api_key or not cohere_api_key:
    st.warning("⚠️ Please provide FREE API keys in the sidebar to start chatting!")
    st.info("""
    ### 🎉 100% FREE Setup (No Credit Card!)

    **Step 1: Get HuggingFace Token** (30 seconds)
    1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
    2. Click "New token" → Name it anything → Create
    3. Copy the token (starts with `hf_`)

    **Step 2: Get Cohere API Key** (30 seconds)
    1. Go to [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)
    2. Sign up with email (no credit card!)
    3. Copy your API key

    **Both work perfectly in Hong Kong!** 🇭🇰

    **Rate Limits (FREE tier):**
    - HuggingFace: ~1000 requests/hour
    - Cohere: ~100 embeds/minute

    More than enough for testing and portfolio demos!
    """)
    st.stop()

# Initialize RAG chain
with st.spinner("🔄 Initializing AI models..."):
    qa_chain = initialize_rag_chain(
        hf_api_key, 
        cohere_api_key, 
        model_choice, 
        temperature,
        max_tokens
    )

if qa_chain is None:
    st.stop()

st.success("✅ Chatbot ready! Ask me anything about Hong Kong healthcare.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 View Sources"):
                st.markdown(message["sources"])

# Chat input
if prompt := st.chat_input("Ask about Hong Kong healthcare..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                result = qa_chain({"query": prompt})
                answer = result["result"]
                source_docs = result.get("source_documents", [])

                # Display answer
                st.markdown(answer)

                # Format sources
                if source_docs:
                    sources_text = "### 📄 Sources:\n\n"
                    for i, doc in enumerate(source_docs, 1):
                        source = doc.metadata.get("source", "Unknown")
                        content_preview = doc.page_content[:200] + "..."
                        sources_text += f"**{i}. {source}**\n```\n{content_preview}\n```\n\n"

                    with st.expander("📚 View Sources"):
                        st.markdown(sources_text)

                    # Add to session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources_text
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.info("Try reducing max_tokens in sidebar or switching to a different model.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Footer
st.markdown("---")
st.markdown("### 💡 Tips:")
st.markdown("- Ask specific questions about HK hospitals, clinics, or services")
st.markdown("- Check the sources to verify information")
st.markdown("- If responses are slow, try switching to a smaller model")
st.markdown("- FREE tier = perfect for portfolio demos! 🎉")
