from pathlib import Path
import re
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    StorageContext, 
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore


def extract_metadata(file_path: Path):
    """
    Extracts metadata fields from a given file path.
    """
    filename = file_path.name
    folder = file_path.parent.name.upper()   # AMFI / RBI / sebi

    # Default values
    metadata = {
        "source": folder,        # AMFI | RBI | SEBI
        "category": "Other",
        "topic": file_path.stem.replace("_", " ").replace("-", " "),
        "audience": "General",
        "ppt_id": None,
        "date": None,
        "filename": filename,
        "page_number": None  # will be added during chunking if available
    }

    # --- RBI patterns ---
    if folder == "RBI":
        if "FINANCIAL LITERACY" in filename.upper():
            metadata["category"] = "Literacy"
            # Extract audience
            match = re.search(r"for\s+([A-Za-z ]+)", filename, re.IGNORECASE)
            if match:
                metadata["audience"] = match.group(1).strip()

        elif "Financing needs" in filename:
            metadata["category"] = "Guide"
            metadata["topic"] = "Financing Needs of Micro and Small Enterprises"

    # --- SEBI patterns ---
    elif folder == "SEBI":
        if filename.upper().startswith("PPT-"):
            metadata["category"] = "PPT"
            # Extract PPT ID
            match = re.match(r"PPT-(\d+)", filename, re.IGNORECASE)
            if match:
                metadata["ppt_id"] = int(match.group(1))

            # Extract date (like Jan24, Feb 2025, 30 Sep 2022)
            date_match = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[ _-]?\d{2,4}", filename, re.IGNORECASE)
            if date_match:
                metadata["date"] = date_match.group(0)

        elif "Mutual-Fund" in filename or "beginners" in filename.lower():
            metadata["category"] = "Guide"
            if "Beginners" in filename:
                metadata["audience"] = "Beginners"
            elif "Advance" in filename:
                metadata["audience"] = "Advanced"
            elif "intermediate" in filename.lower():
                metadata["audience"] = "Intermediate"

        elif "Booklet" in filename:
            metadata["category"] = "Booklet"

        elif "brochure" in filename.lower():
            metadata["category"] = "Brochure"

    # --- AMFI patterns ---
    elif folder == "AMFI":
        if "Strategy" in filename:
            metadata["category"] = "Report"
        elif "NAVAll" in filename:
            metadata["category"] = "Data"
    print(metadata)
    return metadata


# 1. Load all documents recursively
documents = SimpleDirectoryReader(input_dir="data", recursive=True).load_data()

# 2. Attach metadata
for doc in documents:
    file_path = Path(doc.metadata.get("file_path", ""))
    extra_meta = extract_metadata(file_path)
    doc.metadata.update(extra_meta)

# 3. Set embedding model (384-dim for MiniLM)
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 4. Setup ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("finance_docs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 5. Build index and persist
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

print("✅ Indexed all docs with rich metadata into ChromaDB!")
# Fixed: Added missing parentheses
index.storage_context.persist()