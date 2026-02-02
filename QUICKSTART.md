# QUICKSTART - Running the RAG System

## Prerequisites

- Ollama installed and phi model downloaded
- Python virtual environment activated
- All dependencies installed (from `requirements.txt`)

---

## Starting the System

### Terminal 1: Start Ollama Server

```powershell
$env:OLLAMA_HOST = "127.0.0.1:11435"
& "C:\Users\swathi sri\AppData\Local\Programs\Ollama\ollama.exe" serve
```

**Expected output:**

```
Listening on 127.0.0.1:11435
```

**Keep this terminal open!**

---

### Terminal 2: Start Streamlit Web Interface

```powershell
cd "c:\Users\swathi sri\Desktop\RagPath"
.\venv\Scripts\activate
$env:OLLAMA_BASE_URL = "http://127.0.0.1:11435"
streamlit run app.py
```

**Expected output:**

```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Open your browser to `http://localhost:8501` and start querying!

---

## Testing the System (Optional)

### Terminal 3: Run Test Script

```powershell
cd "c:\Users\swathi sri\Desktop\RagPath"
.\venv\Scripts\activate
$env:OLLAMA_BASE_URL = "http://127.0.0.1:11435"
python test_gemini.py
```

This will:

- Load 16 document chunks
- Index them with embeddings
- Run a test query
- Display results with sources

---

## Shutting Down

1. Stop Streamlit: Press `Ctrl+C` in Terminal 2
2. Stop Ollama: Press `Ctrl+C` in Terminal 1

---

## Troubleshooting

**Port 11435 already in use?**

```powershell
netstat -ano | findstr 11435
taskkill /PID <PID> /F
```

**Ollama command not found?**
Use full path:

```powershell
& "C:\Users\swathi sri\AppData\Local\Programs\Ollama\ollama.exe" serve
```

**"No module named streamlit"?**
Ensure venv is activated:

```powershell
.\venv\Scripts\activate
```

**Memory error?**
Close unnecessary applications (especially browsers) to free RAM.

---

## Sample Queries to Test

1. "What is this project about?"
2. "How does the system work?"
3. "What is the architecture?"
4. "What are the main features?"
5. "How do I troubleshoot issues?"

Each query should return an answer with 5 relevant document sources.
