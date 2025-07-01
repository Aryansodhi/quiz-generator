import os
import random
import warnings
import torch # type: ignore
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline, logging # type: ignore

# Silence warnings
os.environ["HF_HOME"] = "E:/Documents/quiz-generator/models/t5-base-qg"
warnings.filterwarnings("ignore")
logging.set_verbosity_error()

# Device
device = 0 if torch.cuda.is_available() else -1
print("Device set to:", "cuda" if device == 0 else "cpu")

# Locate the correct snapshot folder
base = r"E:\Documents\quiz-generator\models\t5-base-qg\models--iarfmoose--t5-base-question-generator"
snapshots = sorted(os.listdir(os.path.join(base, "snapshots")))
snapshot_dir = os.path.join(base, "snapshots", snapshots[0])
print("Model path is:", repr(snapshot_dir))

# Load model & tokenizer
tokenizer = AutoTokenizer.from_pretrained(snapshot_dir, use_fast=False)
model = AutoModelForSeq2SeqLM.from_pretrained(snapshot_dir)
qg = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=device)

def generate_questions(text, num_questions=3):
    out = qg(f"generate questions: {text}", max_length=256,
             do_sample=True, top_k=50, top_p=0.95, num_return_sequences=num_questions)
    return [item["generated_text"].strip() for item in out]

def generate_answer(question):
    out = qg(f"answer question: {question}", max_length=64,
             do_sample=True, top_k=50, top_p=0.95, num_return_sequences=1)
    return out[0]["generated_text"].strip()

def generate_options(question, correct_answer, max_distractors=3, max_retries=5):
    distractors = []
    attempts = 0
    while len(distractors) < max_distractors and attempts < max_retries:
        attempts += 1
        d = generate_answer(question)
        if d and d != correct_answer and d not in distractors:
            distractors.append(d)
    # Fill with placeholders if needed
    if len(distractors) < max_distractors:
        distractors.extend(["N/A"] * (max_distractors - len(distractors)))
    return distractors

def generate_mcq(text, num_questions=3):
    questions = generate_questions(text, num_questions)
    for idx, q in enumerate(questions, 1):
        # skip if model misfires
        if len(q.split()) < 3 or q.lower() in {"true","false"}:
            continue

        ans = generate_answer(q)
        # fallback if answer is bad
        if not ans or ans.lower() in {"true","false"}:
            ans = "Not available"

        opts = generate_options(q, ans) + [ans]
        opts = opts[:4]
        random.shuffle(opts)

        print(f"\nQuestion {idx}: {q}")
        for j, opt in enumerate(opts):
            print(f"  {chr(65+j)}. {opt}")
        print(f"Answer: {ans}")