# MCQ Generator with Ollama + Streamlit

This project allows users to generate multiple-choice questions (MCQs) from `.txt`, `.pdf`, and `.docx` files using a local LLM via Ollama (Mistral) and a user-friendly Streamlit interface.

## Features

- Supports `.txt`, `.pdf`, `.docx`
- Locally runs using Ollama (no API needed)
- Interactive Streamlit UI
- Toggle answers for self-assessment

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
   streamlit run app.py
   ```

## Folder Structure

```
.
├── app.py
├── requirements.txt
├── start_and_watch.py
├── utils/
│   ├── qg_ollama.py
│   ├── loader.py
│   └── ...
└── ollama/
```

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com/)
- Streamlit
