"""OCR Agent — extract text from PDF using open-source PyMuPDF."""

from graph.state import DocumentState
from utils.pdf_loader import extract_text_from_pdf, get_pdf_metadata


def ocr_agent(state: DocumentState) -> dict:
    """Extract text per page; store PDF embedded metadata for the metadata agent."""
    file_path = state["file_path"]
    errors = list(state.get("errors") or [])

    try:
        raw_text, pages = extract_text_from_pdf(file_path)
        pdf_meta = get_pdf_metadata(file_path)

        if not raw_text.strip():
            errors.append(
                "OCR: No text extracted. The PDF may be scanned/image-only. "
                "Consider OCR with Tesseract for image PDFs."
            )

        return {
            "raw_text": raw_text,
            "pages": [p.model_dump() for p in pages],
            "pdf_metadata": pdf_meta,
            "ocr_complete": True,
            "current_step": "ocr",
            "errors": errors,
            "debug": {
                **(state.get("debug") or {}),
                "ocr": f"Extracted {len(pages)} page(s), {len(raw_text)} characters.",
            },
        }
    except Exception as exc:
        errors.append(f"OCR failed: {exc}")
        return {"errors": errors, "current_step": "ocr", "ocr_complete": False}
