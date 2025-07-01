# utils/qg_ollama.py

import os
import re
import requests  # type: ignore
from utils.loader import load_text


# Ollama config
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "mistral"  # You can use llama3/gemma if installed


def call_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Call local Ollama server and return the generated response."""
    try:
        res = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        return res.json()["response"].strip()
    except Exception as e:
        print(f"[ERROR] Ollama request failed: {e}")
        return ""


def parse_mcqs(text: str):
    """Extract MCQs from raw Ollama output."""
    quizzes = []
    q_blocks = re.split(r'\bQuestion\b\s*\d*[:\-]?', text, flags=re.IGNORECASE)
    for block in q_blocks:
        lines = block.strip().split('\n')
        if not lines or len(lines) < 2:
            continue
        question_line = lines[0].strip()
        options = []
        answer = ""
        for line in lines[1:]:
            line = line.strip()
            if re.match(r"^[A-Da-d]\.", line):
                options.append(line)
            elif line.lower().startswith("answer:"):
                answer = line.split(":", 1)[-1].strip()
        if options and answer:
            quizzes.append({
                "question": question_line,
                "options": options,
                "answer": answer
            })
    return quizzes if quizzes else None


def generate_mcq_ollama(input_text, num_questions: int = 3):
    """
    Generate MCQs using Ollama from a string or a file path (.txt/.pdf/.docx).
    """
    # Handle path or uploaded file object
    if isinstance(input_text, (str, os.PathLike)):
        text = load_text(input_text)  # from path
    else:
        text = load_text(input_text)  # from UploadFile-like object

    if not text.strip():
        print("⚠️ Input file is empty or unreadable.")
        return []

    print("Generating questions... (via Ollama)")

    prompt = f"""
You are a quiz-making assistant. From the following passage, generate {num_questions} multiple-choice questions.
Each question must have four options labeled A. B. C. D. and an answer line like "Answer: <text or letter>".
Use this format:

Question 1: <question>
A. <option A>
B. <option B>
C. <option C>
D. <option D>
Answer: <correct option letter or full text>

Passage:
{text}
    """.strip()

    raw_output = call_ollama(prompt)
    print("\n=== RAW OUTPUT ===")
    print(raw_output or "[EMPTY]")
    print("==================")

    parsed = parse_mcqs(raw_output)
    if not parsed:
        print("⚠️ No valid MCQs parsed—see RAW OUTPUT above for troubleshooting.")
        return []

    print("\n=== PARSED QUIZZES ===")
    for i, q in enumerate(parsed, 1):
        print(f"\nQuestion {i}: {q['question']}")
        for opt in q["options"]:
            print(f"  {opt}")
        print(f"Answer: {q['answer']}")

    return parsed
