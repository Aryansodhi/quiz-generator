import os
import io
from PyPDF2 import PdfReader  # type: ignore

try:
    from docx import Document  # type: ignore
except ImportError:
    Document = None


def load_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8")


def load_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [p.extract_text() for p in reader.pages if p.extract_text()]
    return "\n\n".join(pages)


def load_text_from_docx(path: str) -> str:
    if Document is None:
        raise ImportError("Please install `python-docx` for .docx support: pip install python-docx")
    doc = Document(path)
    texts = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(texts)


def load_text(input_) -> str:
    if isinstance(input_, str):
        ext = os.path.splitext(input_)[1].lower()
        if ext == ".txt":
            with open(input_, "rb") as f:
                return load_text_from_txt(f.read())
        elif ext == ".pdf":
            with open(input_, "rb") as f:
                return load_text_from_pdf(f.read())
        elif ext == ".docx":
            return load_text_from_docx(input_)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
    elif hasattr(input_, "type") and hasattr(input_, "getvalue"):
        # e.g. for Streamlit UploadFile
        content = input_.getvalue()
        if input_.type == "text/plain":
            return load_text_from_txt(content)
        elif input_.type == "application/pdf":
            return load_text_from_pdf(content)
        else:
            raise ValueError(f"Unsupported MIME type: {input_.type}")
    else:
        raise TypeError("Unsupported input: must be file path (str) or uploaded file-like object")
