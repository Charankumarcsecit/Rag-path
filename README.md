# Real-Time Documentation Assistant with Pathway

A Retrieval-Augmented Generation (RAG) system that provides real-time answers from continuously evolving documentation. Built with Pathway framework for the hackathon.

## 🎯 Problem Statement

Engineering teams rely on continuously evolving documentation (API references, design specs, runbooks) that changes frequently. Traditional AI assistants index documentation periodically, causing them to provide outdated or incorrect answers shortly after documents are updated.

## 💡 Solution

This project implements a real-time RAG assistant using Pathway framework that:

- ✅ Continuously ingests documentation updates from a Git repository
- ✅ Automatically updates its knowledge base as documents are added, edited, or removed
- ✅ Provides accurate answers that always reflect the latest version of documentation
- ✅ Requires NO manual restarts or re-indexing

## 🏗️ Architecture

```
Git Repository (Dynamic Docs) → Pathway Stream → Vector Database → RAG System → Web UI
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Git
- OpenAI API key

### Installation

1. Clone this repository:

```bash
git clone <your-repo-url>
cd RagPath
```

2. Create virtual environment:

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment:

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. Run the application:

```bash
streamlit run app.py
```

## 📁 Project Structure

```
RagPath/
├── app.py                 # Streamlit web interface
├── pathway_pipeline.py    # Core Pathway streaming logic
├── rag_system.py         # RAG implementation
├── git_watcher.py        # Git repository monitoring
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## 🎮 Usage

1. Configure your documentation Git repository in `.env`
2. Start the application
3. The system will continuously monitor the Git repo for changes
4. Ask questions through the web interface
5. Get real-time answers based on the latest documentation

## 🛠️ Technology Stack

- **Pathway**: Real-time data processing framework
- **OpenAI**: LLM for answer generation
- **ChromaDB**: Vector database for embeddings
- **Streamlit**: Web interface
- **GitPython**: Git repository monitoring

## 📝 License

MIT License

## 👥 Team

Built for the hackathon by [Your Team Name]
