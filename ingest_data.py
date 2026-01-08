import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # ✅ NEW
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import json

# Initialize embeddings (you'll need GOOGLE_API_KEY env variable)
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"  # Fast, free, runs locally
)


# 1. Load PDFs
print("Loading PDFs...")
pdf_docs = []
for pdf_file in ["en_full_report.pdf", "HA_Annual_Report_2023-24_en.pdf"]:
    loader = PyPDFLoader(f"data/{pdf_file}")
    pdf_docs.extend(loader.load())
print(f"Loaded {len(pdf_docs)} PDF pages")

# 2. Load CSVs as raw text (they're messy tab-delimited files)
print("Loading CSVs...")
csv_docs = []
for csv_file in ["healthstat_table1.csv", "healthstat_table2.csv"]:
    with open(f"data/{csv_file}", "r", encoding="utf-8-sig", errors="ignore") as f:
        text = f.read()
    
    doc = Document(
        page_content=text,
        metadata={"source": csv_file, "type": "statistics"}
    )
    csv_docs.append(doc)
print(f"Loaded {len(csv_docs)} CSV files as text")



# 3. Load JSONs and convert to text
print("Loading JSON facilities...")
json_docs = []

for json_file in ["facility-hosp.json", "facility-fmc.json", "facility-sop.json"]:
    with open(f"data/{json_file}", "r", encoding="utf-8") as f:
        facilities = json.load(f)
        for facility in facilities:
            # Convert each facility to a text document
            text = f"Facility: {facility.get('name', 'N/A')}\n"
            text += f"Type: {json_file.replace('facility-', '').replace('.json', '')}\n"
            text += f"District: {facility.get('district', 'N/A')}\n"
            text += f"Address: {facility.get('address', 'N/A')}\n"
            
            doc = Document(
                page_content=text,
                metadata={"source": json_file, "type": "facility"}
            )
            json_docs.append(doc)
print(f"Loaded {len(json_docs)} facilities")

# 4. Combine all documents
all_docs = pdf_docs + csv_docs + json_docs
print(f"\nTotal documents: {len(all_docs)}")

# 5. Split into chunks
print("Splitting documents...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
splits = text_splitter.split_documents(all_docs)
print(f"Created {len(splits)} chunks")

# 6. Create vector store
print("\nCreating Chroma vector store...")
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
print("✅ Vector store created successfully!")
print(f"Stored in: ./chroma_db")
