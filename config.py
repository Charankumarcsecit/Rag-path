"""Configuration settings for the Real-Time Documentation Assistant."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
DOCS_REPO_PATH = Path(os.getenv("DOCS_REPO_PATH", PROJECT_ROOT / "test_docs"))
CHROMA_DB_PATH = PROJECT_ROOT / "chroma_db"

# Ollama Local LLM Configuration
OLLAMA_MODEL = "tinyllama"  # Fast lightweight model
EMBEDDING_MODEL = "local"  # Using fallback embeddings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Git Repository Configuration
DOCS_REPO_URL = os.getenv("DOCS_REPO_URL", "")
GIT_POLL_INTERVAL = 30  # seconds

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5

# Server Configuration
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 8501))

# Pathway Configuration
PATHWAY_PERSISTENCE = True
PATHWAY_CACHE_DIR = PROJECT_ROOT / ".pathway"
