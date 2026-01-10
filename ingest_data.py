"""
Data Ingestion Script - Create Chroma Vector Database
Uses Cohere FREE embeddings - NO CREDIT CARD NEEDED!
Run this locally BEFORE deploying to Streamlit Cloud
"""

import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

# Configuration
DATA_DIR = "./data"  # Put your healthcare PDFs/TXTs here
CHROMA_DIR = "./chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def load_documents(data_dir):
    """Load documents from directory"""
    print(f"📂 Loading documents from {data_dir}...")

    documents = []

    # Load PDFs
    if os.path.exists(data_dir):
        try:
            pdf_loader = DirectoryLoader(
                data_dir,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader,
                show_progress=True
            )
            pdf_docs = pdf_loader.load()
            documents.extend(pdf_docs)
            print(f"  ✅ Loaded {len(pdf_docs)} PDF documents")
        except Exception as e:
            print(f"  ⚠️ No PDFs found or error loading: {e}")

        # Load text files
        try:
            txt_loader = DirectoryLoader(
                data_dir,
                glob="**/*.txt",
                loader_cls=TextLoader,
                show_progress=True,
                loader_kwargs={"encoding": "utf-8"}
            )
            txt_docs = txt_loader.load()
            documents.extend(txt_docs)
            print(f"  ✅ Loaded {len(txt_docs)} TXT documents")
        except Exception as e:
            print(f"  ⚠️ No TXT files found or error loading: {e}")

    print(f"\n✅ Total: {len(documents)} documents loaded")
    return documents

def split_documents(documents):
    """Split documents into chunks"""
    print("\n✂️ Splitting documents into chunks...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True
    )

    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} chunks")

    return chunks

def create_vector_store(chunks):
    """Create and persist Chroma vector store with Cohere embeddings"""
    print("\n🔮 Creating vector embeddings with Cohere (FREE!)...")

    # Get Cohere API key
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        print("\n❌ COHERE_API_KEY not found in .env file!")
        print("\n🔑 Get your FREE Cohere API key:")
        print("1. Go to: https://dashboard.cohere.com/api-keys")
        print("2. Sign up (no credit card needed!)")
        print("3. Copy your API key")
        print("4. Create .env file with: COHERE_API_KEY=your_key_here")
        raise ValueError("Missing COHERE_API_KEY")

    # Initialize Cohere embeddings (FREE tier!)
    print("🔑 Initializing Cohere embeddings...")
    embeddings = CohereEmbeddings(
        cohere_api_key=cohere_api_key,
        model="embed-english-light-v3.0"  # FREE model, works great!
    )

    print(f"\n📊 Processing {len(chunks)} chunks...")
    print("⏳ This may take a few minutes for large datasets...")
    print("💡 Tip: Cohere FREE tier = 100 embeds/minute")

    # Create vector store (with progress updates)
    try:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DIR
        )

        print(f"\n✅ Vector store created successfully!")
        print(f"📁 Location: {CHROMA_DIR}")
        print(f"📊 Total vectors: {vectorstore._collection.count()}")

    except Exception as e:
        print(f"\n❌ Error creating vector store: {e}")
        print("\n💡 Common issues:")
        print("- Check your COHERE_API_KEY is valid")
        print("- Ensure you have internet connection")
        print("- Try reducing chunk size if you have many documents")
        raise

    return vectorstore

def main():
    """Main ingestion pipeline"""
    print("="*60)
    print("🚀 HK Healthcare RAG Data Ingestion")
    print("💰 Using Cohere FREE embeddings - No credit card needed!")
    print("="*60)

    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"\n📁 Created {DATA_DIR} directory.")
        print("\n⚠️ Please add your Hong Kong healthcare documents there!")
        print("\nSupported formats: PDF, TXT")
        print("\nExample files to add:")
        print("- HK hospital directories")
        print("- Healthcare service guides")
        print("- Medical information PDFs")
        print("- Clinic information documents")
        print("\n👉 After adding files, run this script again!")
        return

    # Check if directory has files
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.pdf', '.txt'))]
    if not files:
        print(f"\n⚠️ No PDF or TXT files found in {DATA_DIR}")
        print("\nPlease add documents first!")
        print("\nExample test file you can create:")
        print(f"  echo 'Hong Kong healthcare test document' > {DATA_DIR}/test.txt")
        return

    print(f"\n📁 Found {len(files)} files in {DATA_DIR}:")
    for f in files[:5]:  # Show first 5
        print(f"  - {f}")
    if len(files) > 5:
        print(f"  ... and {len(files)-5} more")

    # Load documents
    documents = load_documents(DATA_DIR)

    if not documents:
        print("\n❌ No documents loaded. Check your data directory!")
        return

    # Split into chunks
    chunks = split_documents(documents)

    if not chunks:
        print("\n❌ No chunks created. Check your documents!")
        return

    # Create vector store
    try:
        vectorstore = create_vector_store(chunks)
    except Exception as e:
        print(f"\n❌ Failed to create vector store: {e}")
        return

    print("\n" + "="*60)
    print("✨ Ingestion Complete! Your vector database is ready.")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  - Documents: {len(documents)}")
    print(f"  - Chunks: {len(chunks)}")
    print(f"  - Vector DB: {CHROMA_DIR}")
    print(f"\n🚀 Next steps:")
    print("  1. Test locally: streamlit run streamlit_app.py")
    print("  2. Upload chroma_db/ folder to GitHub")
    print("  3. Deploy to Streamlit Cloud!")
    print(f"\n💡 Remember: Your vector database is in {CHROMA_DIR}/")
    print("   Make sure to commit this folder to git!")

if __name__ == "__main__":
    main()
