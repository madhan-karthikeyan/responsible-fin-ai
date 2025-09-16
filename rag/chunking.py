# rag/chunking.py

import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextChunker:
    """
    Advanced text chunking for financial documents
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_by_sentences(self, text: str) -> List[str]:
        """
        Chunk text by sentences while respecting chunk size limits
        """
        # Split into sentences using multiple delimiters
        sentences = re.split(r'[.!?]+\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    
                # Start new chunk with overlap from previous chunk
                if chunks and self.chunk_overlap > 0:
                    # Take last few sentences for overlap
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def chunk_by_sections(self, text: str, section_markers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Chunk text by logical sections (useful for financial documents)
        """
        if section_markers is None:
            section_markers = [
                'Section', 'Chapter', 'Rule', 'Clause', 
                'Subsection', 'Para', 'Article'
            ]
        
        chunks = []
        current_section = ""
        current_title = "Introduction"
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            is_section_header = any(
                line.lower().startswith(marker.lower()) for marker in section_markers
            ) or re.match(r'^\d+\.', line)  # Numbered sections
            
            if is_section_header and current_section:
                # Save current section
                section_chunks = self.chunk_by_sentences(current_section)
                for i, chunk in enumerate(section_chunks):
                    chunks.append({
                        'text': chunk,
                        'section_title': current_title,
                        'chunk_index': i,
                        'total_chunks': len(section_chunks)
                    })
                
                # Start new section
                current_title = line[:100]  # Limit title length
                current_section = line
            else:
                current_section += "\n" + line
        
        # Process final section
        if current_section:
            section_chunks = self.chunk_by_sentences(current_section)
            for i, chunk in enumerate(section_chunks):
                chunks.append({
                    'text': chunk,
                    'section_title': current_title,
                    'chunk_index': i,
                    'total_chunks': len(section_chunks)
                })
        
        return chunks


# rag/embedding.py

import numpy as np
from typing import List, Dict, Any, Optional, Union
from sentence_transformers import SentenceTransformer
import logging
import os

# Optional OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Using sentence-transformers only.")

from config import OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Generate embeddings using sentence-transformers or OpenAI
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", use_openai: bool = False):
        self.use_openai = use_openai and OPENAI_AVAILABLE and OPENAI_API_KEY
        
        if self.use_openai:
            openai.api_key = OPENAI_API_KEY
            logger.info("Using OpenAI embeddings")
        else:
            # Load sentence transformer model
            self.model = SentenceTransformer(model_name)
            logger.info(f"Using sentence-transformers model: {model_name}")
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        """
        if not texts:
            return np.array([])
        
        if self.use_openai:
            return self._embed_with_openai(texts)
        else:
            return self._embed_with_sentence_transformers(texts, batch_size)
    
    def _embed_with_sentence_transformers(self, texts: List[str], batch_size: int) -> np.ndarray:
        """
        Generate embeddings using sentence-transformers
        """
        try:
            # Process in batches to manage memory
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(batch, show_progress_bar=False)
                all_embeddings.extend(batch_embeddings)
                
                if i % (batch_size * 10) == 0:  # Log every 10 batches
                    logger.info(f"Processed {i + len(batch)}/{len(texts)} texts")
            
            return np.array(all_embeddings)
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return np.array([])
    
    def _embed_with_openai(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings using OpenAI API
        """
        try:
            all_embeddings = []
            
            for i, text in enumerate(texts):
                response = openai.Embedding.create(
                    input=text[:8000],  # OpenAI has token limits
                    model="text-embedding-ada-002"
                )
                embedding = response['data'][0]['embedding']
                all_embeddings.append(embedding)
                
                if i % 100 == 0:
                    logger.info(f"Processed {i}/{len(texts)} texts with OpenAI")
            
            return np.array(all_embeddings)
            
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            return np.array([])
    
    def embed_single_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        """
        if self.use_openai:
            try:
                response = openai.Embedding.create(
                    input=text[:8000],
                    model="text-embedding-ada-002"
                )
                return np.array(response['data'][0]['embedding'])
            except Exception as e:
                logger.error(f"Error generating single OpenAI embedding: {e}")
                return np.array([])
        else:
            return self.model.encode([text])[0]


# rag/ingestion.py

import chromadb
from chromadb.config import Settings
import json
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from config import CHROMA_DB_PATH, PROCESSED_DATA_DIR
from rag.chunking import TextChunker
from rag.embedding import EmbeddingGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBIngestion:
    """
    Handle ingestion of financial data into vector database
    """
    
    def __init__(self, db_path: str = CHROMA_DB_PATH):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Initialize chunker and embedder
        self.chunker = TextChunker(chunk_size=800, chunk_overlap=100)
        self.embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
        
        # Create or get collections
        self.tax_collection = self.client.get_or_create_collection(
            name="tax_rules",
            metadata={"description": "Indian tax rules and regulations"}
        )
        
        self.investment_collection = self.client.get_or_create_collection(
            name="investment_options",
            metadata={"description": "Investment options and descriptions"}
        )
        
        self.budget_collection = self.client.get_or_create_collection(
            name="budgeting_rules",
            metadata={"description": "Budgeting rules and financial heuristics"}
        )
        
        logger.info("Vector database initialized")
    
    def ingest_tax_data(self) -> Dict[str, int]:
        """
        Ingest tax data into vector database
        """
        tax_file = PROCESSED_DATA_DIR / "tax_rules.json"
        
        if not tax_file.exists():
            logger.error(f"Tax data file not found: {tax_file}")
            return {"error": "Tax data file not found"}
        
        with open(tax_file, 'r', encoding='utf-8') as f:
            tax_data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for item in tax_data:
            # Chunk the content
            content = item.get('content', '')
            if len(content) > 100:  # Only process substantial content
                chunks = self.chunker.chunk_by_sentences(content)
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"tax_{uuid.uuid4().hex}_{i}"
                    
                    documents.append(chunk)
                    metadatas.append({
                        'title': item.get('title', 'Unknown'),
                        'source': item.get('source_url', item.get('source_file', 'Unknown')),
                        'type': item.get('type', 'tax'),
                        'year': item.get('year', 'Unknown'),
                        'extracted_date': item.get('extracted_date', 'Unknown'),
                        'chunk_index': i,
                        'original_length': len(content)
                    })
                    ids.append(doc_id)
        
        if documents:
            # Add to collection in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_metas = metadatas[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                
                self.tax_collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
            
            logger.info(f"Ingested {len(documents)} tax document chunks")
        
        return {"tax_chunks": len(documents)}
    
    def ingest_investment_data(self) -> Dict[str, int]:
        """
        Ingest investment data into vector database
        """
        investment_file = PROCESSED_DATA_DIR / "investment_options.json"
        
        if not investment_file.exists():
            logger.error(f"Investment data file not found: {investment_file}")
            return {"error": "Investment data file not found"}
        
        with open(investment_file, 'r', encoding='utf-8') as f:
            investment_data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for item in investment_data:
            # Create comprehensive text for each investment option
            investment_text = f"""
            Investment: {item.get('name', '')}
            Category: {item.get('category', '')}
            Risk Level: {item.get('risk_level', '')}
            Liquidity: {item.get('liquidity', '')}
            Expected Returns: {item.get('expected_return_range', '')}
            Tax Treatment: {item.get('tax_treatment', '')}
            Minimum Investment: ₹{item.get('minimum_investment', '')}
            Lock-in Period: {item.get('lock_in_period', '')}
            
            Description: {item.get('description', '')}
            
            Pros: {', '.join(item.get('pros', []))}
            Cons: {', '.join(item.get('cons', []))}
            
            Suitable For: {item.get('suitable_for', '')}
            """
            
            doc_id = f"investment_{uuid.uuid4().hex}"
            
            documents.append(investment_text.strip())
            metadatas.append({
                'name': item.get('name', 'Unknown'),
                'category': item.get('category', 'Unknown'),
                'risk_level': item.get('risk_level', 'Unknown'),
                'liquidity': item.get('liquidity', 'Unknown'),
                'type': 'investment',
                'source': item.get('source', 'Investment data'),
                'minimum_investment': item.get('minimum_investment', 0),
                'expected_return_range': item.get('expected_return_range', 'Unknown')
            })
            ids.append(doc_id)
        
        if documents:
            self.investment_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Ingested {len(documents)} investment options")
        
        return {"investment_options": len(documents)}
    
    def ingest_budgeting_data(self) -> Dict[str, int]:
        """
        Ingest budgeting rules into vector database
        """
        budget_file = PROCESSED_DATA_DIR / "budgeting_rules.json"
        
        if not budget_file.exists():
            logger.error(f"Budgeting data file not found: {budget_file}")
            return {"error": "Budgeting data file not found"}
        
        with open(budget_file, 'r', encoding='utf-8') as f:
            budget_data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for item in budget_data:
            # Create comprehensive text for each budgeting rule
            rule_text = f"""
            Rule: {item.get('rule_name', '')}
            Category: {item.get('category', '')}
            
            Description: {item.get('description', '')}
            
            Detailed Explanation: {item.get('detailed_explanation', '')}
            
            Applicability: {item.get('applicability', '')}
            
            Advantages: {', '.join(item.get('pros', []))}
            Disadvantages: {', '.join(item.get('cons', []))}
            
            Source: {item.get('source', '')}
            Popularity Score: {item.get('popularity_score', 'Unknown')}/10
            """
            
            doc_id = f"budget_{uuid.uuid4().hex}"
            
            documents.append(rule_text.strip())
            metadatas.append({
                'rule_name': item.get('rule_name', 'Unknown'),
                'category': item.get('category', 'Unknown'),
                'type': 'budgeting_rule',
                'source': item.get('source', 'Budgeting data'),
                'applicability': item.get('applicability', 'Unknown'),
                'popularity_score': item.get('popularity_score', 0)
            })
            ids.append(doc_id)
        
        if documents:
            self.budget_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Ingested {len(documents)} budgeting rules")
        
        return {"budgeting_rules": len(documents)}
    
    def ingest_all_data(self) -> Dict[str, Any]:
        """
        Ingest all processed data into vector database
        """
        logger.info("Starting full data ingestion...")
        
        results = {}
        
        # Ingest tax data
        tax_result = self.ingest_tax_data()
        results.update(tax_result)
        
        # Ingest investment data
        investment_result = self.ingest_investment_data()
        results.update(investment_result)
        
        # Ingest budgeting data
        budget_result = self.ingest_budgeting_data()
        results.update(budget_result)
        
        # Get collection stats
        results['database_stats'] = {
            'tax_collection_count': self.tax_collection.count(),
            'investment_collection_count': self.investment_collection.count(),
            'budget_collection_count': self.budget_collection.count()
        }
        
        logger.info("Data ingestion completed")
        return results
    
    def search_similar_documents(self, query: str, collection_name: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search for similar documents in a specific collection
        """
        collection_map = {
            'tax': self.tax_collection,
            'investment': self.investment_collection,
            'budget': self.budget_collection
        }
        
        if collection_name not in collection_map:
            return {"error": f"Collection {collection_name} not found"}
        
        collection = collection_map[collection_name]
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            return {
                'query': query,
                'collection': collection_name,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error searching collection {collection_name}: {e}")
            return {"error": f"Search failed: {e}"}
    
    def search_all_collections(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Search across all collections
        """
        all_results = {}
        
        for collection_name in ['tax', 'investment', 'budget']:
            results = self.search_similar_documents(query, collection_name, n_results)
            all_results[collection_name] = results
        
        return all_results


def main():
    """Example usage of the RAG pipeline"""
    
    # Initialize ingestion system
    ingestion = VectorDBIngestion()
    
    # Ingest all data
    results = ingestion.ingest_all_data()
    print("Ingestion Results:", json.dumps(results, indent=2))
    
    # Example searches
    test_queries = [
        "What are the tax slabs for 2024-25?",
        "Best investment options for beginners",
        "How to create an emergency fund?"
    ]
    
    for query in test_queries:
        print(f"\n--- Search Results for: {query} ---")
        search_results = ingestion.search_all_collections(query)
        
        for collection_name, collection_results in search_results.items():
            if 'results' in collection_results:
                documents = collection_results['results'].get('documents', [[]])[0]
                metadatas = collection_results['results'].get('metadatas', [[]])[0]
                
                print(f"\n{collection_name.title()} Collection:")
                for i, (doc, meta) in enumerate(zip(documents[:2], metadatas[:2])):  # Show top 2
                    print(f"  Result {i+1}: {doc[:200]}...")
                    print(f"  Metadata: {meta}")

if __name__ == "__main__":
    main()