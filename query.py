from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.prompts import PromptTemplate
import chromadb

class QueryEngine:
    def __init__(self):
        Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        Settings.llm = Ollama(
            model="llama3",
            verbose=False
        )

        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        chroma_collection = chroma_client.get_or_create_collection("finance_docs")

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        storage_context = StorageContext.from_defaults(
            persist_dir="./storage",
            vector_store=vector_store
        )

        self.index = load_index_from_storage(storage_context)

        self.CUSTOM_PROMPT_TEMPLATE = PromptTemplate(
            """You are a friendly and accurate finance tutor AI.
        Use the following retrieved context to answer the user's question.
        Provide step-by-step explanation when applicable and keep it beginner-friendly.

        Context:
        {context_str}

        Question:
        {query_str}

        Answer in clear, concise, professional language.
        """
        )

        self.query_engine = self.index.as_query_engine(
            response_mode="tree_summarize",
            text_qa_template= self.CUSTOM_PROMPT_TEMPLATE,
            similarity_top_k=4  # retrieve top 4 most relevant chunks
        )
# query = "Whats the minimum age requirement to start trading?"
    def query(self, query: str):
        response = self.query_engine.query(query)
        print("Answer:\n", response)
        return response

# print("\nSource Nodes:")
# for node in response.source_nodes:
#     print(node)
#     print("-----")