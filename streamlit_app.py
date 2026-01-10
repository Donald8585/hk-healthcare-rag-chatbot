import streamlit as st
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

from langchain_huggingface import HuggingFaceEndpoint
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

st.set_page_config(
    page_title="HK Healthcare RAG Chatbot",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hong Kong Healthcare Information Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("### 🆓 100% FREE APIs")

    hf_api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
    cohere_api_key = st.secrets.get("COHERE_API_KEY", "")

    if not hf_api_key:
        hf_api_key = st.text_input("HuggingFace API Token", type="password")

    if not cohere_api_key:
        cohere_api_key = st.text_input("Cohere API Key", type="password")

    # SIMPLIFIED model list - only models that 100% work
    model_choice = st.selectbox(
        "LLM Model",
        [
            "google/flan-t5-base",  # Small, fast, reliable
            "google/flan-t5-large",
            "HuggingFaceH4/zephyr-7b-beta"
        ]
    )

    max_tokens = st.slider("Max Tokens", 64, 512, 128, 64)

    st.markdown("---")
    st.markdown("### 🔑 Get FREE Keys:")
    st.markdown("[HuggingFace Token](https://huggingface.co/settings/tokens)")
    st.markdown("[Cohere Key](https://dashboard.cohere.com/api-keys)")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@st.cache_resource
def initialize_rag_chain(hf_key, cohere_key, model_name, max_tok):
    try:
        st.info(f"🔄 Loading model: {model_name}...")

        # Initialize LLM with minimal parameters
        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            huggingfacehub_api_token=hf_key,
            max_new_tokens=max_tok,
            temperature=0.3
        )

        st.success(f"✅ LLM loaded: {model_name}")

        # Initialize embeddings
        embeddings = CohereEmbeddings(
            cohere_api_key=cohere_key,
            model="embed-english-light-v3.0"
        )

        st.success("✅ Embeddings loaded")

        # Check for vector database
        persist_directory = "./chroma_db"

        if not os.path.exists(persist_directory):
            st.warning("⚠️ No database found - Running in NO-RAG mode")
            st.info("""
            **App is working, but has no healthcare data yet!**

            The LLM will answer directly without retrieving documents.

            To add data:
            1. Create `data/` folder locally
            2. Add healthcare PDFs/TXTs
            3. Run `python ingest_data.py`
            4. Upload `chroma_db/` to GitHub
            """)

            # Return simple LLM chain (no RAG)
            template = """Answer this question about Hong Kong healthcare:

Question: {question}

Answer:"""

            prompt = PromptTemplate(template=template, input_variables=["question"])
            simple_chain = prompt | llm | StrOutputParser()

            return simple_chain, None

        # Full RAG mode if database exists
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        template = """Context: {context}

Question: {question}

Answer:"""

        prompt = PromptTemplate(template=template, input_variables=["context", "question"])

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        st.success("✅ Full RAG mode ready!")
        return rag_chain, retriever

    except Exception as e:
        st.error(f"❌ Initialization failed: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        import traceback
        st.code(traceback.format_exc())
        return None, None

if not hf_api_key or not cohere_api_key:
    st.warning("⚠️ Please add API keys in sidebar!")
    st.info("""
    ### Get FREE API Keys:

    1. **HuggingFace**: huggingface.co/settings/tokens
    2. **Cohere**: dashboard.cohere.com/api-keys

    Both are 100% free and work in Hong Kong!
    """)
    st.stop()

# Initialize
with st.spinner("🔄 Initializing..."):
    chain, retriever = initialize_rag_chain(hf_api_key, cohere_api_key, model_choice, max_tokens)

if chain is None:
    st.error("❌ Failed to initialize. Check errors above.")
    st.stop()

st.success("✅ Chatbot ready!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about HK healthcare..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                # Invoke chain
                answer = chain.invoke(prompt)

                # Clean up
                if "Answer:" in answer:
                    answer = answer.split("Answer:")[-1].strip()

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.error(f"Error type: {type(e).__name__}")

                # Show full traceback for debugging
                import traceback
                with st.expander("🐛 Full Error Details"):
                    st.code(traceback.format_exc())

                st.info("""
                💡 **Try these fixes:**
                1. Wait 60 seconds and try again (model cold start)
                2. Switch to "google/flan-t5-base" (most reliable)
                3. Check your API keys are valid
                4. Try a simpler question: "What is healthcare?"
                """)

                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown("---")
st.markdown("### 💡 Troubleshooting:")
st.markdown("- **Silent error?** Switch to flan-t5-base model")
st.markdown("- **Timeout?** Wait 60 seconds, try again")
st.markdown("- **Still failing?** Check error details above")
