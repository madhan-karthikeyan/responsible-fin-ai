# query.py (adapted for Ollama Cloud)
import os
import chromadb
from ollama import Client as OllamaClient
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.prompts import PromptTemplate

class QueryEngine:
    def __init__(
        self,
        model_name: str = "gpt-oss:20b-cloud",
        chroma_path: str = "./chroma_db",
        storage_dir: str = "./storage",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        ollama_base_url: str = "https://ollama.com",
        request_timeout: float = 60.0,
    ):
        """
        Query engine configured to talk to Ollama Cloud via ollama.Client
        and use LlamaIndex with a Chroma vector store + HuggingFace embeddings.
        """

        # ---------- Embedding & LLM settings ----------
        # Set the embedding model used by LlamaIndex global Settings
        Settings.embed_model = HuggingFaceEmbedding(model_name=embedding_model)

        # Build the low-level Ollama HTTP client with Authorization header
        ollama_api_key = "" # Key here
        if not ollama_api_key:
            raise RuntimeError("Please set OLLAMA_API_KEY in environment before running")

        ollama_client = OllamaClient(
            host=ollama_base_url,
            headers={"Authorization": "Bearer " + ollama_api_key},
        )

        # Create the LlamaIndex Ollama wrapper; pass the client so it calls Ollama Cloud
        self.llm_obj = Ollama(
            model=model_name,
            base_url=ollama_base_url,
            request_timeout=request_timeout,
            client=ollama_client,
        )

        # Also set the global Settings.llm so any LlamaIndex internals use it
        Settings.llm = self.llm_obj

        # Keep model name for logging/CSV exports
        self._model_name = model_name

        # ---------- Chroma vector store ----------
        # Use persistent chroma client (keeps DB on disk)
        chroma_client = chromadb.PersistentClient(path=chroma_path)
        chroma_collection = chroma_client.get_or_create_collection("finance_docs")

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        # ---------- Storage / Index ----------
        storage_context = StorageContext.from_defaults(
            persist_dir=storage_dir,
            vector_store=vector_store
        )

        # Load existing index from storage (must have been created already)
        self.index = load_index_from_storage(storage_context)

        # ---------- Prompt template ----------
        self.CUSTOM_PROMPT_TEMPLATE = PromptTemplate(
            """You are FinTutor, a precise and reliable financial AI assistant.

Use only the provided context to answer. If information is missing, say:
"Insufficient data in context to answer confidently."

Follow this structure in every response:
1. Key Point or Definition  
2. Step-by-Step Explanation (if applicable)  
3. Final Answer or Recommendation  

Keep responses concise, factual, and consistent.
Avoid speculation, opinions, or unnecessary elaboration.

Context:
{context_str}

Question:
{query_str}
"""
        )

        # Build a query engine from the index with desired options
        self.query_engine = self.index.as_query_engine(
            response_mode="tree_summarize",
            text_qa_template=self.CUSTOM_PROMPT_TEMPLATE,
            similarity_top_k=4,  # top 4 context chunks
        )

    def get_model_name(self) -> str:
        return self._model_name

    def query(self, user_query: str, **kwargs):
        """
        Run a query through the LlamaIndex-powered query engine.
        Additional kwargs are forwarded to the query method if supported.
        """
        return self.query_engine.query(user_query, **kwargs)
