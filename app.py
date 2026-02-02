"""Streamlit web interface for the Real-Time Documentation Assistant."""

import streamlit as st
import time
import threading
import tempfile
import shutil
from pathlib import Path

import config
from git_watcher import GitWatcher
from document_processor import DocumentProcessor
from rag_system import RAGSystem
from upload_handlers import GitHubRepoHandler, GoogleDriveHandler, DropboxHandler


# Page configuration
st.set_page_config(
    page_title="Real-Time Documentation Assistant",
    page_icon="📚",
    layout="wide"
)


def initialize_system():
    """Initialize the RAG system and Git watcher."""
    if 'initialized' not in st.session_state:
        with st.spinner("Initializing system..."):
            # Initialize RAG system
            st.session_state.rag = RAGSystem()
            st.session_state.processor = DocumentProcessor()
            
            # Initialize Git watcher
            st.session_state.git_watcher = GitWatcher(
                config.DOCS_REPO_URL if config.DOCS_REPO_URL else "",
                config.DOCS_REPO_PATH
            )
            
            # Setup repository
            if st.session_state.git_watcher.setup():
                # Initial indexing
                docs = st.session_state.processor.load_documents_from_directory(
                    config.DOCS_REPO_PATH
                )
                st.session_state.rag.index_documents(docs)
                st.session_state.last_update = time.time()
            else:
                st.error(f"Failed to setup repository at {config.DOCS_REPO_PATH}")
            
            st.session_state.initialized = True
            st.session_state.messages = []


def check_for_updates():
    """Check for Git updates and re-index if needed."""
    if 'git_watcher' in st.session_state:
        try:
            if st.session_state.git_watcher.check_for_updates():
                with st.spinner("Pulling updates..."):
                    if st.session_state.git_watcher.pull_updates():
                        # Re-index changed documents
                        changed_files = st.session_state.git_watcher.get_changed_files()
                        
                        # Remove old versions
                        st.session_state.rag.remove_documents(changed_files)
                        
                        # Index new versions
                        docs = st.session_state.processor.load_documents_from_directory(
                            config.DOCS_REPO_PATH
                        )
                        changed_docs = st.session_state.processor.filter_changed_documents(
                            docs, changed_files
                        )
                        st.session_state.rag.index_documents(changed_docs)
                        
                        st.session_state.last_update = time.time()
                        return True
        except Exception as e:
            st.error(f"Error checking for updates: {e}")
    
    return False


def process_uploaded_sources(uploaded_files=None, github_url=None, drive_url=None, dropbox_url=None):
    """Process documents from various upload sources."""
    all_docs = []
    
    # Process direct file uploads
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                docs = st.session_state.processor.load_uploaded_file(uploaded_file, uploaded_file.name)
                all_docs.extend(docs)
                st.success(f"✓ Processed {uploaded_file.name}: {len(docs)} chunks")
    
    # Process GitHub repository
    if github_url:
        with st.spinner(f"Cloning GitHub repository..."):
            temp_dir = GitHubRepoHandler.clone_repo(github_url)
            if temp_dir:
                docs = st.session_state.processor.load_documents_from_directory(temp_dir)
                all_docs.extend(docs)
                st.success(f"✓ Cloned and processed repository: {len(docs)} chunks")
                # Cleanup temp directory
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            else:
                st.error("Failed to clone GitHub repository")
    
    # Process Google Drive file
    if drive_url:
        with st.spinner("Downloading from Google Drive..."):
            file_path = GoogleDriveHandler.download_file(drive_url)
            if file_path:
                docs = st.session_state.processor.load_document(file_path)
                all_docs.extend(docs)
                st.success(f"✓ Downloaded and processed Drive file: {len(docs)} chunks")
                # Cleanup temp file
                try:
                    file_path.unlink()
                except:
                    pass
            else:
                st.error("Failed to download from Google Drive")
    
    # Process Dropbox file
    if dropbox_url:
        with st.spinner("Downloading from Dropbox..."):
            file_path = DropboxHandler.download_file(dropbox_url)
            if file_path:
                docs = st.session_state.processor.load_document(file_path)
                all_docs.extend(docs)
                st.success(f"✓ Downloaded and processed Dropbox file: {len(docs)} chunks")
                # Cleanup temp file
                try:
                    file_path.unlink()
                except:
                    pass
            else:
                st.error("Failed to download from Dropbox")
    
    # Index all documents
    if all_docs:
        st.session_state.rag.index_documents(all_docs)
        st.session_state.last_update = time.time()
        st.success(f"🎉 Successfully indexed {len(all_docs)} total chunks!")
    
    return len(all_docs)


def main():
    """Main application."""
    
    # Initialize system
    initialize_system()
    
    # Sidebar
    with st.sidebar:
        st.title("📚 Real-Time Docs Assistant")
        st.markdown("---")
        
        # Upload Section
        st.subheader("📤 Upload Documents")
        
        upload_method = st.radio(
            "Choose upload method:",
            ["Direct Upload", "GitHub Repository", "Google Drive", "Dropbox"],
            label_visibility="collapsed"
        )
        
        if upload_method == "Direct Upload":
            uploaded_files = st.file_uploader(
                "Upload documents (PDF, DOCX, TXT, MD, etc.)",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'pptx', 'txt', 'md', 'py', 'js', 'json', 'yaml', 'yml', 'html', 'csv']
            )
            
            if st.button("📁 Process Files", use_container_width=True, disabled=not uploaded_files):
                process_uploaded_sources(uploaded_files=uploaded_files)
        
        elif upload_method == "GitHub Repository":
            github_url = st.text_input(
                "GitHub Repository URL",
                placeholder="https://github.com/owner/repo or owner/repo"
            )
            
            if st.button("📦 Clone & Index Repo", use_container_width=True, disabled=not github_url):
                process_uploaded_sources(github_url=github_url)
        
        elif upload_method == "Google Drive":
            drive_url = st.text_input(
                "Google Drive File URL",
                placeholder="https://drive.google.com/file/d/..."
            )
            st.caption("💡 Make sure the file is publicly accessible")
            
            if st.button("☁️ Download & Index", use_container_width=True, disabled=not drive_url):
                process_uploaded_sources(drive_url=drive_url)
        
        elif upload_method == "Dropbox":
            dropbox_url = st.text_input(
                "Dropbox File URL",
                placeholder="https://www.dropbox.com/..."
            )
            
            if st.button("📥 Download & Index", use_container_width=True, disabled=not dropbox_url):
                process_uploaded_sources(dropbox_url=dropbox_url)
        
        st.markdown("---")
        
        # System status
        st.subheader("System Status")
        
        if 'rag' in st.session_state:
            stats = st.session_state.rag.get_stats()
            st.metric("Indexed Chunks", stats['total_chunks'])
        
        if 'last_update' in st.session_state:
            time_ago = int(time.time() - st.session_state.last_update)
            st.metric("Last Update", f"{time_ago}s ago")
        
        st.markdown("---")
        
        # Configuration
        st.subheader("Configuration")
        
        if 'git_watcher' in st.session_state and st.session_state.git_watcher.repo:
            st.success("✓ Git repository configured")
            st.text(f"Path: {config.DOCS_REPO_PATH.name}")
            if config.DOCS_REPO_URL:
                st.text(f"URL: {config.DOCS_REPO_URL[:50]}...")
        else:
            st.info("ℹ️ No Git repository configured")
        
        st.success("✓ Ollama LLM configured (local, no API key needed)")
        st.text(f"Model: {config.OLLAMA_MODEL}")
        st.text(f"Base URL: {config.OLLAMA_BASE_URL}")
        
        st.markdown("---")
        
        # Manual update button
        if st.button("🔄 Check for Updates", use_container_width=True):
            if check_for_updates():
                st.success("✓ Updates pulled and indexed!")
            else:
                st.info("No updates available")
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Main content
    st.title("Real-Time Documentation Assistant")
    st.markdown("Ask questions about your documentation. The system automatically stays up-to-date!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📄 Sources"):
                    for source in message["sources"]:
                        st.text(f"• {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documentation..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching documentation..."):
                result = st.session_state.rag.query(prompt)
                
                st.markdown(result['answer'])
                
                # Show sources
                if result['sources']:
                    with st.expander("📄 Sources"):
                        for source in result['sources']:
                            st.text(f"• {source}")
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "sources": result['sources']
                })
    
    # Auto-check for updates (every 30 seconds)
    if 'last_auto_check' not in st.session_state:
        st.session_state.last_auto_check = time.time()
    
    time_since_check = time.time() - st.session_state.last_auto_check
    if time_since_check > 30:
        check_for_updates()
        st.session_state.last_auto_check = time.time()


if __name__ == "__main__":
    main()
