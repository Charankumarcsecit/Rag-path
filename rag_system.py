"""RAG system implementation with real-time updates using Ollama."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
import requests

import config
from document_processor import Document, DocumentProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSystem:
    """Real-time Retrieval-Augmented Generation system using Ollama."""
    
    def __init__(self):
        """Initialize the RAG system."""
        self.document_processor = DocumentProcessor(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(config.CHROMA_DB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="documentation",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info("RAG system initialized with Ollama LLM")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text using Ollama's embedding API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                embedding = response.json().get('embedding', [])
                return embedding
            else:
                # Fallback: use simple hash-based embedding for demo
                logger.warning(f"Ollama embedding failed, using fallback. Status: {response.status_code}")
                return self._simple_embedding(text)
                
        except Exception as e:
            logger.warning(f"Error getting Ollama embedding: {e}, using fallback")
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """
        Simple fallback embedding using character-level hashing.
        This is NOT ideal for production but works for demo purposes.
        """
        import hashlib
        # Create a deterministic embedding from text
        embedding_size = 384
        embedding = []
        
        # Hash the text and create embedding
        for i in range(embedding_size):
            hash_input = f"{text}_{i}".encode('utf-8')
            hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
            # Normalize to [-1, 1]
            normalized = (hash_value % 10000) / 5000 - 1
            embedding.append(normalized)
        
        return embedding
    
    def index_documents(self, documents: List[Document]) -> int:
        """
        Index documents into the vector database.
        
        Args:
            documents: List of documents to index
            
        Returns:
            Number of documents indexed
        """
        if not documents:
            logger.warning("No documents to index")
            return 0
        
        try:
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            metadatas = []
            contents = []
            
            for doc in documents:
                doc_id = f"{doc.source}_{doc.chunk_id}"
                ids.append(doc_id)
                contents.append(doc.content)
                metadatas.append(doc.metadata)
                
                # Get embedding
                embedding = self.get_embedding(doc.content)
                embeddings.append(embedding)
            
            # Add to collection (upsert to handle updates)
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            
            logger.info(f"Indexed {len(documents)} documents")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            return 0
    
    def remove_documents(self, file_paths: List[str]) -> int:
        """
        Remove documents from a specific file.
        
        Args:
            file_paths: List of file paths to remove
            
        Returns:
            Number of documents removed
        """
        try:
            removed_count = 0
            
            for file_path in file_paths:
                # Query for all documents from this file
                results = self.collection.get(
                    where={"file_name": Path(file_path).name}
                )
                
                if results['ids']:
                    self.collection.delete(ids=results['ids'])
                    removed_count += len(results['ids'])
                    logger.info(f"Removed {len(results['ids'])} documents from {file_path}")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error removing documents: {e}")
            return 0
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Get query embedding
            query_embedding = self.get_embedding(query)
            
            if not query_embedding:
                logger.warning("Could not generate query embedding")
                return []
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            logger.info(f"Retrieved {len(documents)} documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Generate an answer using Ollama LLM and retrieved context.
        
        Args:
            query: User's question
            context_docs: Retrieved context documents
            
        Returns:
            Generated answer
        """
        try:
            # Build context from retrieved documents
            context = "\n\n".join([
                f"Document {i+1} (from {doc['metadata'].get('file_name', 'unknown')}):\n{doc['content']}"
                for i, doc in enumerate(context_docs)
            ])
            
            # Create prompt
            system_prompt = """You are a helpful documentation assistant. 
Answer questions based on the provided documentation context. 
If the answer is not in the context, say so clearly.
Be concise and accurate."""
            
            user_prompt = f"""Context from documentation:
{context}

Question: {query}

Answer:"""
            
            # Combine prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate response using Ollama
            response = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": config.OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "temperature": 0.3,
                    "stream": False
                },
                timeout=180
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return f"Error from Ollama: {response.status_code}. Make sure Ollama is running and the model '{config.OLLAMA_MODEL}' is available."
            
            answer = response.json().get('response', 'No response from Ollama')
            return answer
            
        except requests.exceptions.ConnectionError:
            return "Could not connect to Ollama. Please make sure Ollama is running (run 'ollama serve' in terminal)."
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Complete RAG query: retrieve + generate.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer and metadata
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(question, top_k=config.TOP_K_RESULTS)
        
        if not retrieved_docs:
            return {
                'answer': "I couldn't find any relevant information in the documentation. Please add some documents to the test_docs folder.",
                'sources': [],
                'num_sources': 0
            }
        
        # Generate answer
        answer = self.generate_answer(question, retrieved_docs)
        
        # Extract unique sources
        sources = list(set([
            doc['metadata'].get('file_name', 'unknown')
            for doc in retrieved_docs
        ]))
        
        return {
            'answer': answer,
            'sources': sources,
            'num_sources': len(sources),
            'retrieved_chunks': len(retrieved_docs)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the indexed documents.
        
        Returns:
            Dictionary with statistics
        """
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'total_chunks': 0}


def main():
    """Test the RAG system."""
    rag = RAGSystem()
    
    # Check Ollama connection
    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            logger.info(f"Available Ollama models: {[m['name'] for m in models]}")
        else:
            logger.warning("Could not connect to Ollama. Make sure Ollama is running.")
            logger.info(f"Start Ollama with: ollama serve")
            logger.info(f"Then pull a model: ollama pull {config.OLLAMA_MODEL}")
            return
    except Exception as e:
        logger.error(f"Could not reach Ollama at {config.OLLAMA_BASE_URL}")
        logger.error("Make sure Ollama is installed and running.")
        logger.error("Download Ollama from: https://ollama.ai")
        return
    
    # Test query
    result = rag.query("What is this project about?")
    print(f"\nAnswer: {result['answer']}")
    print(f"Sources: {result['sources']}")


if __name__ == "__main__":
    main()
