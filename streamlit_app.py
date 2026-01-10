import streamlit as st
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

from langchain_cohere import ChatCohere, CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

st.set_page_config(
    page_title="HK Healthcare RAG Chatbot",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hong Kong Healthcare Information Assistant")
st.markdown("💡 **Using Cohere API (100% FREE!)** - No HuggingFace needed!")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("### 🆓 Only Need ONE API Key!")

    cohere_api_key = st.secrets.get("COHERE_API_KEY", "")

    if not cohere_api_key:
        cohere_api_key = st.text_input(
            "Cohere API Key", 
            type="password",
            help="Get FREE at dashboard.cohere.com/api-keys"
        )

    # Cohere model selection
    model_choice = st.selectbox(
        "Chat Model",
        [
            "command-light",  # Fast & FREE
            "command",        # Better quality, still FREE
        ],
        help="Both models are 100% FREE!"
    )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max Tokens", 128, 1024, 256, 64)

    st.markdown("---")
    st.markdown("### 📊 Cohere Benefits:")
    st.markdown("- ✅ 100% FREE tier")
    st.markdown("- ✅ No credit card needed")
    st.markdown("- ✅ Works in Hong Kong")
    st.markdown("- ✅ Fast & reliable")
    st.markdown("- ✅ 1000 API calls/month FREE")

    st.markdown("---")
    st.markdown("### 🔑 Get FREE Key:")
    st.markdown("[Cohere Dashboard](https://dashboard.cohere.com/api-keys)")
    st.markdown("Sign up → Copy key → Paste above!")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@st.cache_resource
def initialize_rag_chain(cohere_key, model_name, temp, max_tok):
    try:
        # Initialize Cohere Chat LLM
        llm = ChatCohere(
            cohere_api_key=cohere_key,
            model=model_name,
            temperature=temp,
            max_tokens=max_tok
        )

        st.success(f"✅ Cohere Chat loaded: {model_name}")

        # Initialize Cohere Embeddings
        embeddings = CohereEmbeddings(
            cohere_api_key=cohere_key,
            model="embed-english-light-v3.0"
        )

        st.success("✅ Cohere Embeddings loaded")

        # Check for database
        persist_directory = "./chroma_db"

        if not os.path.exists(persist_directory):
            st.warning("⚠️ No healthcare database found")
            st.info("""
            **App works, but has no HK healthcare data yet!**

            The chatbot will answer based on Cohere's general knowledge.

            **To add your healthcare data:**
            1. Locally: Create `data/` folder with PDFs/TXTs
            2. Run: `python ingest_data.py`
            3. Upload `chroma_db/` folder to GitHub
            4. Redeploy!

            **For now, ask general HK healthcare questions!** ✅
            """)

            # Simple chat mode without RAG
            prompt = ChatPromptTemplate.from_template(
                "You are a helpful assistant. Answer this question about Hong Kong healthcare:\n\n{question}"
            )

            simple_chain = prompt | llm | StrOutputParser()
            return simple_chain, None

        # Full RAG mode
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        st.success(f"✅ Loaded {vectorstore._collection.count()} documents")

        prompt = ChatPromptTemplate.from_template(
            """Use this context to answer the question:

Context:
{context}

Question: {question}

Provide a clear, accurate answer based on the context above."""
        )

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        st.success("✅ Full RAG mode ready!")
        return rag_chain, retriever

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        with st.expander("🐛 Full Error"):
            st.code(traceback.format_exc())
        return None, None

# Check API key
if not cohere_api_key:
    st.warning("⚠️ Please add your Cohere API key in the sidebar!")
    st.info("""
    ### 🎉 Get FREE Cohere API Key (30 seconds):

    1. Go to: [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)
    2. Sign up with email (NO credit card needed!)
    3. Copy your API key
    4. Paste in sidebar →

    **FREE tier includes:**
    - 1000 API calls/month
    - Both chat & embeddings
    - Works in Hong Kong! 🇭🇰
    """)
    st.stop()

# Initialize chain
with st.spinner("🔄 Initializing Cohere AI..."):
    chain, retriever = initialize_rag_chain(cohere_api_key, model_choice, temperature, max_tokens)

if chain is None:
    st.error("❌ Failed to initialize. Check error above.")
    st.stop()

st.success("✅ Chatbot ready! Ask me about Hong Kong healthcare.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 View Sources"):
                st.markdown(message["sources"])

# Chat input
if prompt := st.chat_input("Ask about HK healthcare..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                answer = chain.invoke(prompt)

                st.markdown(answer)

                # Get sources if retriever exists
                if retriever:
                    try:
                        source_docs = retriever.invoke(prompt)

                        if source_docs:
                            sources_text = "### 📄 Sources:\n\n"
                            for i, doc in enumerate(source_docs, 1):
                                source = doc.metadata.get("source", "Unknown")
                                preview = doc.page_content[:150] + "..."
                                sources_text += f"**{i}. {source}**\n```\n{preview}\n```\n\n"

                            with st.expander("📚 View Sources"):
                                st.markdown(sources_text)

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "sources": sources_text
                            })
                    except:
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)

                import traceback
                with st.expander("🐛 Full Error Details"):
                    st.code(traceback.format_exc())

                st.info("""
                💡 **Troubleshooting:**
                - Check your Cohere API key is valid
                - Try "command-light" model (faster)
                - Reduce max tokens to 128
                - Wait 30 seconds and try again
                """)

                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown("---")
st.markdown("### ✨ Why Cohere?")
st.markdown("- 🚀 **Faster** than HuggingFace free tier")
st.markdown("- ✅ **More reliable** - no cold starts")
st.markdown("- 💰 **100% FREE** - 1000 calls/month")
st.markdown("- 🌍 **Works in Hong Kong** - no VPN needed")
st.markdown("### 🎯 Your Portfolio Project:")
st.markdown("**Tech Stack:** Cohere AI + LangChain + Streamlit + ChromaDB")
st.markdown("**Cost:** $0/month | **Status:** Production-ready! 🎉")
