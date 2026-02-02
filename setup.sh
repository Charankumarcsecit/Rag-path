#!/bin/bash
# Setup script for the Real-Time Documentation Assistant

echo "Setting up Real-Time Documentation Assistant..."

# Create .env from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it and add your OpenAI API key and Git repository URL."
fi

# Install dependencies (run this after activation)
# pip install -r requirements.txt

echo ""
echo "Setup complete! Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Edit .env and add your DOCS_REPO_URL (Git repository with documentation)"
echo "3. Activate virtual environment: .\\venv\\Scripts\\activate"
echo "4. Install dependencies: pip install -r requirements.txt"
echo "5. Run the app: streamlit run app.py"
