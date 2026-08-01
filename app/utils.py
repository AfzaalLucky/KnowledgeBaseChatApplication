from pypdf import PdfReader
from docx import Document

def load_file(path: str):
    if path.endswith(".pdf"):
        reader = PdfReader(path)
        return "\n".join([p.extract_text() for p in reader.pages])

    if path.endswith(".docx"):
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])

    if path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    raise Exception("Unsupported file type")