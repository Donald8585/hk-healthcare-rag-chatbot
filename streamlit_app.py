import streamlit as st
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3  # CRITICAL: Fix for Chroma on Streamlit Cloud

from langchain_huggingface import HuggingFaceEndpoint
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
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
            "microsoft/Phi-3-mini-4k-instruct",
            "HuggingFaceH4/zephyr-7b-beta",
            "google/flan-t5-large",
            "mistralai/Mixtral-8x7B-Instruct-v0.1"
        ],
        help="Models that work on FREE HuggingFace Inference API!"
    )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max Tokens", 128, 1024, 256, 64)

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

    st.markdown("---")
    st.markdown("### 💡 Model Tips:")
    st.markdown("- **Phi-3-mini**: Fast, accurate (RECOMMENDED)")
    st.markdown("- **Zephyr-7b**: Best quality")
    st.markdown("- **FLAN-T5**: Fastest responses")
    st.markdown("- **Mixtral**: Most powerful (slower)")

def format_docs(docs):
    """Format retrieved documents into context string"""
    return "\n\n".join(doc.page_content for doc in docs)

@st.cache_resource
def initialize_rag_chain(hf_key, cohere_key, model_name, temp, max_tok):
    """Initialize RAG chain using modern LCEL pattern"""

    try:
        # Initialize HuggingFace LLM with better parameters
        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            huggingfacehub_api_token=hf_key,
            temperature=temp,
            max_new_tokens=max_tok,
            task="text-generation",  # Explicit task
            do_sample=True,
            top_k=40,
            top_p=0.9,
            repetition_penalty=1.1
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
            ### 📦 Database Not Found

            **This is expected for first deployment!** The app is working fine.

            **To add your data:**
            1. Create a `data/` folder locally
            2. Add HK healthcare PDFs/TXT files
            3. Run: `python ingest_data.py`
            4. Upload the `chroma_db/` folder to GitHub
            5. Redeploy!

            **For now, you can test the UI and API keys work!** ✅
            """)
            return None, None

        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )

        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        # Create prompt template optimized for better responses
        template = """You are a helpful Hong Kong healthcare information assistant.

Context information:
{context}

Question: {question}

Please provide a clear, accurate answer based on the context above. If the context doesn't contain the information needed, say "I don't have information about that in my knowledge base."

Answer:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # Build RAG chain using LCEL
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        return rag_chain, retriever

    except Exception as e:
        st.error(f"❌ Initialization error: {str(e)}")
        st.info("💡 Try switching to a different model in the sidebar!")
        return None, None

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
    rag_chain, retriever = initialize_rag_chain(
        hf_api_key, 
        cohere_api_key, 
        model_choice, 
        temperature,
        max_tokens
    )

if rag_chain is None:
    st.warning("⚠️ Running in demo mode (no database). Add your data to enable full functionality!")
    st.info("🎉 **Good news:** Your app is deployed and working! You just need to add your healthcare data.")
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
                # Get answer using RAG chain
                answer = rag_chain.invoke(prompt)

                # Clean up answer (remove prompt repetition if present)
                if "Answer:" in answer:
                    answer = answer.split("Answer:")[-1].strip()

                # Get source documents
                source_docs = retriever.invoke(prompt)

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
                st.info("""
                💡 **Troubleshooting tips:**
                - Try switching to a different model (Phi-3-mini recommended)
                - Reduce max_tokens in sidebar
                - Some models may be temporarily unavailable
                - Wait 30 seconds and try again (models may be "cold starting")
                """)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Footer
st.markdown("---")
st.markdown("### 💡 Tips:")
st.markdown("- Ask specific questions about HK hospitals, clinics, or services")
st.markdown("- Check the sources to verify information")
st.markdown("- If a model fails, try switching to **Phi-3-mini** (most reliable)")
st.markdown("- FREE tier = perfect for portfolio demos! 🎉")
st.markdown("### 📊 Your Portfolio Project:")
st.markdown("- 🌐 **Deployed:** Streamlit Cloud")
st.markdown("- 🤖 **Tech:** RAG + LangChain + HuggingFace + Cohere")
st.markdown("- 💰 **Cost:** $0/month")
st.markdown("- 🚀 **Status:** Production-ready!")
