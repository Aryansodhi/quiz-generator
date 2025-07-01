# MCQ Generator with Ollama + Streamlit

This project allows users to generate multiple-choice questions (MCQs) from `.txt`, `.pdf`, and `.docx` files using a local LLM via Ollama (Mistral) and a user-friendly Streamlit interface.

## Features

- Supports `.pdf`, `.docx`, `.txt` files
- Automatically generates questions, options, and answers
- Clean web interface using Streamlit
- No OpenAI API key required — runs fully locally using Ollama
- Hide/show answers for self-testing

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com/download)
- `mistral` model (default, you can use others)
- Streamlit

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate # On Linux/MacOS
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the Mistral model with Ollama:
   ```bash
   ollama run mistral
   ```

5. Run the app:
   ```bash
   python start.py
   ```
   This will open the web UI in your browser at http://localhost:8501

## Folder Structure

```
.
├── app.py
├── requirements.txt
├── start.py
├── utils/
│   ├── qg_ollama.py
│   ├── loader.py
│   └── concept_extractor.py
└── ollama/
```
