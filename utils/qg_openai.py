# utils/qg_openai.py

import os
import openai # type: ignore
from utils.loader import load_text

# Set your OpenAI API key (use environment variable for security)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Or replace with your key as a string

def call_openai(prompt, model="gpt-3.5-turbo"):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024
    )
    return response.choices[0].message.content.strip()

def generate_mcq_openai(input_path_or_text: str, num_questions: int = 3, model="gpt-3.5-turbo"):
    if os.path.exists(input_path_or_text):
        text = load_text(input_path_or_text)
    else:
        text = input_path_or_text

    prompt = (
        f"Generate {num_questions} multiple-choice questions from the following text. "
        f"For each question, provide 4 options labeled A to D, and indicate the correct answer.\n\n"
        f"Text:\n{text}\n\n"
        f"Format:\n"
        f"Question 1: ...\n"
        f"  A. ...\n"
        f"  B. ...\n"
        f"  C. ...\n"
        f"  D. ...\n"
        f"Answer: ...\n\n"
        f"(Continue in this format for all {num_questions} questions.)"
    )

    result = call_openai(prompt, model=model)
    print(result)
