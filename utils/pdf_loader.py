"""Open-source PDF text extraction using PyMuPDF."""

from pathlib import Path

import fitz  # PyMuPDF

from schemas.document import PageText


def extract_text_from_pdf(file_path: str | Path) -> tuple[str, list[PageText]]:
    """Extract text per page and as a single concatenated string."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages: list[PageText] = []
    parts: list[str] = []

    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            pages.append(PageText(page_number=i, text=text))
            if text:
                parts.append(f"--- Page {i} ---\n{text}")

    full_text = "\n\n".join(parts)
    return full_text, pages


def get_pdf_metadata(file_path: str | Path) -> dict:
    """Read embedded PDF metadata (author, dates, title)."""
    path = Path(file_path)
    with fitz.open(path) as doc:
        meta = doc.metadata or {}
        return {
            "title": meta.get("title") or None,
            "author": meta.get("author") or None,
            "subject": meta.get("subject") or None,
            "creator": meta.get("creator") or None,
            "creation_date": meta.get("creationDate") or None,
            "modification_date": meta.get("modDate") or None,
            "page_count": doc.page_count,
        }
