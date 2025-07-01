from utils.loader import load_text_from_txt, load_text_from_pdf

# 1. Test .txt loader
sample_txt = b"Hello world!\nThis is a test."
print("TXT loader output:", load_text_from_txt(sample_txt))

# 2. Test PDF loader
with open("utils/sample.pdf", "rb") as f:
    data = f.read()
print("PDF loader output:", load_text_from_pdf(data)[:100], "…")
