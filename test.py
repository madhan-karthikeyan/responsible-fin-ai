from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.readers.file import PDFReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pathlib import Path
# Initialize PDFReader
pdf_reader = PDFReader()

pdf_files = list(Path("data/sebi").glob("*.pdf"))
# Load documents from the 'data/sebi' directory
documents = SimpleDirectoryReader("./data/sebi", input_files=pdf_files).load_data()

# Initialize embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2") 


# Initialize LLM
Settings.llm = Ollama(model="llama3")


# Build vector index
index = VectorStoreIndex.from_documents(documents)

# Create query engine
query_engine = index.as_query_engine()

# Test query
query = "How do I Invest in the Securities Market?"
response = query_engine.query(query)

print("Answer:\n", response)
