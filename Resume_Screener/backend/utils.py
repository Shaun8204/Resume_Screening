import tempfile
import shutil
from pathlib import Path
from typing import List

import pdfplumber
from docx import Document


def save_upload_to_temp(upload_file) -> Path:
    suffix = Path(upload_file.filename).suffix or ""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with open(path, "wb") as out:
        shutil.copyfileobj(upload_file.file, out)
    return Path(path)


def extract_text_from_pdf(path: Path) -> str:
    text_parts = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception:
        return ""
    return "\n".join(text_parts)


def extract_text_from_docx(path: Path) -> str:
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text)
    except Exception:
        return ""


def extract_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix in (".docx", ".doc"):
        return extract_text_from_docx(path)
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def cleanup_path(path: Path):
    try:
        path.unlink()
    except Exception:
        pass
