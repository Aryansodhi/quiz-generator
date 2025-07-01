from transformers import AutoTokenizer, AutoModelForSeq2SeqLM # type: ignore

# Choose local path (outside C drive if needed, e.g., on E drive)
model_name = "iarfmoose/t5-base-question-generator"
target_path = "E:/Documents/quiz-generator/models/t5-base-qg"

# Download model and tokenizer to the target path
AutoTokenizer.from_pretrained(model_name, cache_dir=target_path)
AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=target_path)

print("✅ Model downloaded to:", target_path)
