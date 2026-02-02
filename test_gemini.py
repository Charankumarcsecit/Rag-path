"""Test the Gemini RAG system."""

from rag_system import RAGSystem
from document_processor import DocumentProcessor
from pathlib import Path

def main():
    rag = RAGSystem()
    processor = DocumentProcessor()
    
    # Load documents from test_docs
    docs_path = Path('test_docs')
    if docs_path.exists():
        documents = processor.load_documents_from_directory(docs_path)
        print(f'Loaded {len(documents)} document chunks')
        
        # Index them
        indexed = rag.index_documents(documents)
        print(f'Indexed {indexed} documents')
        
        # Get stats
        stats = rag.get_stats()
        print(f'Stats: {stats}')
        
        # Test a query
        print('\n' + '='*50)
        print('Testing RAG Query')
        print('='*50)
        result = rag.query('What is this project about?')
        print(f'Answer: {result["answer"]}')
        print(f'Sources: {result["sources"]}')
        print(f'Retrieved chunks: {result["retrieved_chunks"]}')
    else:
        print("test_docs directory not found")

if __name__ == "__main__":
    main()
