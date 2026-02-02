"""
Simplified Demo Script - Add New Content to Existing Files
This demonstrates real-time updates by modifying documentation
"""

import os
import subprocess
from datetime import datetime

DOCS_DIR = r"c:\Users\swathi sri\Desktop\RagPath\test_docs"
os.chdir(DOCS_DIR)

print("=" * 60)
print("REAL-TIME DOCUMENTATION ASSISTANT - DEMO")
print("=" * 60)
print("\nThis will add new content to your documentation")
print("Watch the Streamlit app detect and index changes!\n")

def add_changelog():
    """Add a changelog file"""
    with open("CHANGELOG.md", "w", encoding="utf-8") as f:
        f.write(f"""# Changelog

## [2.1.0] - {datetime.now().strftime("%Y-%m-%d")}

### Added
- Real-time documentation synchronization
- Semantic search capabilities
- Natural language query interface
- Git-backed version control integration
- Automatic incremental indexing

### Improved
- Query response time reduced by 60%
- Memory usage optimized
- Better error handling and logging
- Enhanced source attribution

### Fixed
- Race condition in concurrent document updates
- Memory leak in long-running sessions
- Timeout issues with large repositories

## [2.0.0] - 2025-12-15

### Breaking Changes
- New configuration format (YAML)
- API endpoint restructure
- Authentication method updated

### Added
- Multi-tenant support
- Advanced analytics dashboard
- Kubernetes deployment templates

## [1.5.0] - 2025-10-01

### Added
- Docker support
- Caching layer
- Monitoring integration
""")
    subprocess.run(["git", "add", "CHANGELOG.md"], check=True)
    subprocess.run(["git", "commit", "-m", "Add version changelog"], check=True)
    print("✓ Added CHANGELOG.md")

def add_architecture():
    """Add architecture document"""
    with open("ARCHITECTURE.md", "w", encoding="utf-8") as f:
        f.write("""# System Architecture

## Overview

The Real-Time Documentation Assistant is built on a modern, scalable architecture that ensures low-latency responses and real-time synchronization.

## Core Components

### 1. Git Watcher
- Monitors documentation repositories for changes
- Polling interval: 30 seconds
- Supports both local and remote repositories
- Detects additions, modifications, and deletions

### 2. Document Processor
- Extracts text from multiple formats (MD, TXT, PY, JS, JSON, YAML)
- Intelligent chunking with context preservation
- Chunk size: 1000 characters with 200 character overlap
- Metadata extraction for enhanced search

### 3. Vector Database (ChromaDB)
- Persistent storage for embeddings
- Fast similarity search
- Automatic index updates
- Collection-based organization

### 4. Embedding Engine
- OpenAI text-embedding-3-small model
- 1536-dimensional vectors
- Semantic similarity computation
- Batch processing for efficiency

### 5. LLM Integration
- OpenAI GPT-3.5-turbo for generation
- Context-aware prompt construction
- Source attribution and citation
- Configurable temperature and max tokens

### 6. Web Interface (Streamlit)
- Real-time chat interface
- Source document display
- System statistics dashboard
- Manual update trigger

## Data Flow

```
Git Repository
    |
    v
Git Watcher (detects changes)
    |
    v
Document Processor (chunk documents)
    |
    v
Embedding Engine (generate vectors)
    |
    v
ChromaDB (store embeddings)
    |
    v
User Query --> Vector Search --> Top-K Results --> LLM --> Answer
```

## Scalability Considerations

- **Horizontal Scaling**: Multiple instances can share ChromaDB
- **Caching**: Query results cached for repeated questions
- **Incremental Updates**: Only changed documents re-indexed
- **Connection Pooling**: Efficient API usage

## Security

- API keys stored in environment variables
- No sensitive data in version control
- Rate limiting on API calls
- Input validation and sanitization

## Monitoring

- Query latency tracking
- Index size monitoring
- API usage metrics
- Error rate tracking
""")
    subprocess.run(["git", "add", "ARCHITECTURE.md"], check=True)
    subprocess.run(["git", "commit", "-m", "Add architecture documentation"], check=True)
    print("✓ Added ARCHITECTURE.md")

def add_troubleshooting():
    """Add troubleshooting guide"""
    with open("TROUBLESHOOTING.md", "w", encoding="utf-8") as f:
        f.write("""# Troubleshooting Guide

## Common Issues and Solutions

### Issue: "API Rate Limit Exceeded"

**Symptoms**: Queries fail with rate limit errors

**Cause**: Too many API calls to OpenAI in short time period

**Solution**:
1. Reduce query frequency
2. Implement caching for repeated questions
3. Upgrade to higher tier API plan
4. Add exponential backoff retry logic

### Issue: "Documents Not Being Indexed"

**Symptoms**: New documents don't appear in search results

**Cause**: Git watcher not detecting changes or indexing failure

**Solution**:
1. Check Git repository is properly initialized
2. Verify DOCS_REPO_PATH in configuration
3. Click "Check for Updates Now" manually
4. Check console logs for errors
5. Verify file formats are supported

### Issue: "Poor Search Results"

**Symptoms**: Queries return irrelevant documents

**Cause**: Improper chunking or embedding issues

**Solution**:
1. Adjust CHUNK_SIZE and CHUNK_OVERLAP in config
2. Verify documents have clear structure
3. Check embedding model is working correctly
4. Increase TOP_K_RESULTS for more context
5. Review document quality and clarity

### Issue: "Slow Query Response"

**Symptoms**: Long wait times for answers

**Cause**: Large document corpus or network latency

**Solution**:
1. Enable query result caching
2. Optimize chunk size
3. Reduce TOP_K_RESULTS if too high
4. Check network connection to OpenAI
5. Consider using faster embedding model

### Issue: "ChromaDB Connection Errors"

**Symptoms**: Cannot connect to vector database

**Cause**: Database corruption or permission issues

**Solution**:
1. Delete chroma_db/ directory and restart
2. Check disk space availability
3. Verify write permissions
4. Ensure no other process using the database
5. Check ChromaDB logs for details

### Issue: "Out of Memory"

**Symptoms**: Application crashes with memory errors

**Cause**: Too many documents or large chunk size

**Solution**:
1. Reduce CHUNK_SIZE in configuration
2. Limit number of documents indexed
3. Increase system memory
4. Enable garbage collection optimization
5. Process documents in batches

## Getting Help

If none of these solutions work:

1. Check the logs in the console
2. Review configuration in .env file
3. Test with minimal setup (fewer documents)
4. Verify all dependencies are installed
5. Check GitHub issues for similar problems

## Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about:
- Git operations
- Document processing
- Embedding generation
- Database operations
- API calls
""")
    subprocess.run(["git", "add", "TROUBLESHOOTING.md"], check=True)
    subprocess.run(["git", "commit", "-m", "Add troubleshooting guide"], check=True)
    print("✓ Added TROUBLESHOOTING.md")

def main():
    print("Demo will add 3 new documentation files:\n")
    print("1. CHANGELOG.md - Version history")
    print("2. ARCHITECTURE.md - System design")
    print("3. TROUBLESHOOTING.md - Common issues")
    
    input("\nPress ENTER to start...")
    
    print("\n" + "="*60)
    print("STEP 1: Adding CHANGELOG.md")
    print("="*60)
    add_changelog()
    input("\n✓ Done! Press ENTER to continue...")
    print("\n💡 NOW: Click 'Check for Updates Now' in the app")
    print("💡 QUERY: 'What's in the latest release?' or 'What was fixed in v2.1?'")
    input("\nPress ENTER for next step...")
    
    print("\n" + "="*60)
    print("STEP 2: Adding ARCHITECTURE.md")
    print("="*60)
    add_architecture()
    input("\n✓ Done! Press ENTER to continue...")
    print("\n💡 NOW: Click 'Check for Updates Now' in the app")
    print("💡 QUERY: 'How does the system architecture work?' or 'What database is used?'")
    input("\nPress ENTER for next step...")
    
    print("\n" + "="*60)
    print("STEP 3: Adding TROUBLESHOOTING.md")
    print("="*60)
    add_troubleshooting()
    input("\n✓ Done! Press ENTER to continue...")
    print("\n💡 NOW: Click 'Check for Updates Now' in the app")
    print("💡 QUERY: 'How do I fix slow queries?' or 'What if documents aren't indexed?'")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE!")
    print("="*60)
    print("\nYou successfully demonstrated:")
    print("✓ Real-time documentation updates")
    print("✓ Automatic Git synchronization")
    print("✓ Instant knowledge availability")
    print("✓ Semantic search on new content")
    print("\n🎉 Perfect for your hackathon demo!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Demo cancelled")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
