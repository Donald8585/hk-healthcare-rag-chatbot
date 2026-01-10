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
st.markdown("💡 **Powered by Cohere AI (100% FREE!)** 🚀")

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

    # ACTUAL current models (Jan 2026)
    model_choice = st.selectbox(
        "Chat Model",
        [
            "command-r7b-12-2024",      # Small, fast, current (RECOMMENDED)
            "command-r-08-2024",        # Standard, current
            "command-r-plus-08-2024",   # Best quality, current
        ],
        help="command-r7b is fastest & works on FREE tier!"
    )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max Tokens", 128, 1024, 256, 64)

    st.markdown("---")
    st.markdown("### 📊 Model Info:")
    st.markdown("- **command-r7b**: Small, fast (⭐ BEST for free)")
    st.markdown("- **command-r-08-2024**: Balanced")
    st.markdown("- **command-r-plus-08-2024**: Highest quality")

    st.markdown("---")
    st.markdown("### 🆓 FREE Tier:")
    st.markdown("- 20 trial API calls")
    st.markdown("- Then 1000 calls/month FREE")
    st.markdown("- No credit card needed!")
    st.markdown("- Works in Hong Kong 🇭🇰")

    st.markdown("---")
    st.markdown("### 🔑 Get FREE Key:")
    st.markdown("[Cohere Dashboard](https://dashboard.cohere.com/api-keys)")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@st.cache_resource
def initialize_rag_chain(cohere_key, model_name, temp, max_tok):
    try:
        # Initialize with CURRENT Cohere model
        llm = ChatCohere(
            cohere_api_key=cohere_key,
            model=model_name,
            temperature=temp,
            max_tokens=max_tok
        )

        st.success(f"✅ Cohere Chat: {model_name}")

        # Initialize embeddings
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
            **🎉 Good news: App is working!** Just needs healthcare data.

            The chatbot will answer using general knowledge for now.

            **To add HK healthcare data:**
            1. Create `data/` folder with PDFs/TXTs
            2. Run: `python ingest_data.py`
            3. Push `chroma_db/` to GitHub
            4. Redeploy!

            **Try asking general HK healthcare questions!** ✅
            """)

            # Simple chat without RAG
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

        doc_count = vectorstore._collection.count()
        st.success(f"✅ Loaded {doc_count} documents - RAG mode active!")

        prompt = ChatPromptTemplate.from_template(
            """Use this context to answer:

Context:
{context}

Question: {question}

Provide a clear answer based on the context."""
        )

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        return rag_chain, retriever

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        with st.expander("🐛 Details"):
            st.code(traceback.format_exc())
        return None, None

# Check API key
if not cohere_api_key:
    st.warning("⚠️ Add your Cohere API key in sidebar!")
    st.info("""
    ### 🎉 Get FREE Cohere Key (30 sec):

    1. Visit: [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)
    2. Sign up (no credit card!)
    3. Copy your API key
    4. Paste in sidebar →

    **FREE: 20 trial + 1000/month calls!** 🎉
    """)
    st.stop()

# Initialize
with st.spinner("🔄 Loading Cohere AI..."):
    chain, retriever = initialize_rag_chain(cohere_api_key, model_choice, temperature, max_tokens)

if chain is None:
    st.error("❌ Failed. Check error above.")
    st.stop()

st.success("✅ Chatbot ready! Ask about HK healthcare.")

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 Sources"):
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

                # Get sources if available
                if retriever:
                    try:
                        source_docs = retriever.invoke(prompt)
                        if source_docs:
                            sources_text = "### 📄 Sources:\n\n"
                            for i, doc in enumerate(source_docs, 1):
                                source = doc.metadata.get("source", "Unknown")
                                preview = doc.page_content[:150] + "..."
                                sources_text += f"**{i}. {source}**\n```{preview}```\n\n"

                            with st.expander("📚 Sources"):
                                st.markdown(sources_text)

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "sources": sources_text
                            })
                        else:
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                    except:
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)

                import traceback
                with st.expander("🐛 Details"):
                    st.code(traceback.format_exc())

                st.info("💡 Try: Switch to command-r7b model or reduce max tokens")
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown("---")
st.markdown("### 🎯 Portfolio Project:")
st.markdown("- 🤖 **AI:** Cohere command-r7b")
st.markdown("- 🔍 **Pattern:** RAG (Retrieval Augmented Generation)")
st.markdown("- 🗄️ **Vector DB:** ChromaDB")
st.markdown("- 🌐 **Deployed:** Streamlit Cloud")
st.markdown("- 💰 **Cost:** $0/month")
st.markdown("- ✅ **Status:** Production-ready! 🎉")
