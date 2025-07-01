# utils/qg_flan.py

import os, warnings, torch, random, difflib, re # type: ignore
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline # type: ignore
from nltk.corpus import wordnet # type: ignore
from utils.loader import load_text
from utils.concept_extractor import extract_topics

# Redirect cache location (optional)
os.environ["HF_HOME"] = r"E:\Documents\quiz-generator\models\models--google--flan-t5-large"
warnings.filterwarnings("ignore")
from transformers.utils import logging # type: ignore
logging.set_verbosity_error()

# Device
torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
pipe_device = 0 if torch.cuda.is_available() else -1

# Load model
model_name = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(torch_device)
gen = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=pipe_device, framework="pt")

def _get_text(input_):
    return load_text(input_) if os.path.isfile(input_) else input_

def generate_questions(text, n=3):
    prompt = (
        f"Generate {n} short factual quiz questions (not full MCQs) from this passage.\n"
        f"Only return the questions.\n\n{text[:3000]}"
    )
    out = gen(prompt, max_length=256, do_sample=True, top_p=0.9, num_return_sequences=1)
    return [line.strip("Q. ").strip() for line in out[0]["generated_text"].split("\n") if line.strip()]

def generate_answer(question):
    prompt = f"Answer this question accurately in one short sentence:\n\n{question}"
    out = gen(prompt, max_length=64, do_sample=False, num_return_sequences=1)
    return out[0]["generated_text"].strip().rstrip(".")

def get_wordnet_distractors(answer, max_extra=5):
    extras = set()
    for syn in wordnet.synsets(answer.split()[0]):
        for lemma in syn.lemmas():
            name = lemma.name().replace("_", " ")
            if name.lower() != answer.lower():
                extras.add(name)
        if len(extras) >= max_extra:
            break
    return list(extras)

def generate_distractors(question, correct, k=3):
    distractors = []
    # 1) Numeric fallback
    match = re.findall(r"\d+", correct)
    if match:
        try:
            correct_num = int(match[0])
            options = list(set([
                str(correct_num + 1),
                str(correct_num - 1),
                str(correct_num + 2),
                str(correct_num - 2),
                str(correct_num + 3)
            ]))
            options = [opt for opt in options if opt != str(correct_num)]
            distractors = options[:k]
        except:
            pass

    # 2) Ask Flan for distractors
    if len(distractors) < k:
        prompt = (
            f"Generate {k+3} plausible but incorrect answers to the question.\n"
            f"Avoid using or rephrasing the correct answer.\n"
            f"Question: {question}\n"
            f"Correct answer: {correct}\n"
            f"Distractors:"
        )
        out = gen(prompt, max_length=64, do_sample=True, top_p=0.9, top_k=50, num_return_sequences=1)
        lines = out[0]["generated_text"].split("\n")
        for line in lines:
            line = line.strip("-•1234567890. ").strip()
            sim = difflib.SequenceMatcher(None, line.lower(), correct.lower()).ratio()
            if (
                line
                and line.lower() != correct.lower()
                and line not in distractors
                and sim < 0.7
            ):
                distractors.append(line)
            if len(distractors) >= k:
                break

    # 3) WordNet fallback
    if len(distractors) < k:
        for ex in get_wordnet_distractors(correct, max_extra=5):
            sim = difflib.SequenceMatcher(None, ex.lower(), correct.lower()).ratio()
            if ex not in distractors and sim < 0.7:
                distractors.append(ex)
            if len(distractors) >= k:
                break

    # 4) extract_topics fallback
    if len(distractors) < k:
        for kw in extract_topics(question + " " + correct, top_n=5):
            sim = difflib.SequenceMatcher(None, kw.lower(), correct.lower()).ratio()
            if kw not in distractors and sim < 0.7:
                distractors.append(kw)
            if len(distractors) >= k:
                break

    # 5) Curated fallback
    fallback_map = {
        "photosynthesis": ["respiration", "chemosynthesis", "fermentation", "Calvin cycle"],
        "universal shift register": ["RAM module", "ALU unit", "decoder", "multiplexer"],
        "adder": ["subtractor", "multiplier", "counter", "flip-flop"]
    }
    for key in fallback_map:
        if key in correct.lower() and len(distractors) < k:
            for item in fallback_map[key]:
                if item not in distractors:
                    distractors.append(item)
                if len(distractors) >= k:
                    break

    # Pad
    while len(distractors) < k:
        distractors.append("N/A")
    return distractors[:k]

def generate_mcq_flan(input_text: str, num_questions: int = 3):
    """
    Accepts either raw text or a path to .txt/.pdf.
    Extracts the text, then generates MCQs with strong formatting.
    """
    text = _get_text(input_text)
    if len(text) > 1500:
        text = text[:1500]
    print("Generating questions... (this may take a while)\n")

    # Format prompt strictly
    prompt = f"""Generate {num_questions} multiple-choice questions (MCQs) from the following passage.
Each MCQ should be structured as follows:

Question: [Your question here]
Options:
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
Answer: [Letter of the correct answer]

Repeat this format exactly {num_questions} times. Only output the questions in this exact format.

Passage:
{text}
"""
    # Generate
    output = gen(prompt, max_length=512, do_sample=True, top_p=0.9, temperature=0.9, num_return_sequences=1)[0]["generated_text"]
    print("=== RAW OUTPUT ===")
    print(output.strip())
    print("==================\n")

    # Parse: improved regex to handle more flexible spacing and formatting
    pattern = re.compile(
        r"Question:\s*(.*?)\s*Options:\s*A\.\s*(.*?)\s*B\.\s*(.*?)\s*C\.\s*(.*?)\s*D\.\s*(.*?)\s*Answer:\s*([ABCD])",
        re.DOTALL | re.IGNORECASE
    )
    matches = pattern.findall(output)
    if not matches:
        print("⚠️ No valid MCQs parsed—see RAW OUTPUT above for troubleshooting.")
        return

    # Generate distractors for each question and print
    for i, (q, a, b, c, d, ans_letter) in enumerate(matches, 1):
        correct = eval(ans_letter.lower())  # get the correct answer text
        # For robustness, use the answer letter to get the correct option
        if ans_letter.upper() == 'A':
            correct = a.strip()
        elif ans_letter.upper() == 'B':
            correct = b.strip()
        elif ans_letter.upper() == 'C':
            correct = c.strip()
        elif ans_letter.upper() == 'D':
            correct = d.strip()
        else:
            correct = "N/A"

        # Generate distractors if needed (for dynamic distractor replacement, but here just print as-is)
        # For now, we use the model's distractors, but you can uncomment to use generate_distractors
        # distractors = generate_distractors(q, correct, k=3)
        # print(f"Distractors: {distractors}")  # Optional: print generated distractors

        print(f"\nQuestion {i}: {q.strip()}")
        print(f" A. {a.strip()}")
        print(f" B. {b.strip()}")
        print(f" C. {c.strip()}")
        print(f" D. {d.strip()}")
        print(f"Answer: {ans_letter.upper()} ({correct})")
