"""Metadata Agent — extract page count, date, author, and document type."""

from graph.state import DocumentState
from schemas.document import MetadataResult
from utils.llm import get_llm, truncate_for_llm

METADATA_PROMPT = """Extract metadata from the document. Use ONLY information present in the text or PDF metadata.

PDF embedded metadata (may be empty):
{pdf_meta}

Classifier suggestion (use as hint only — verify against text):
{classification}

Document text:
{text}

RULES:
- If a field is not found, return null — do NOT guess.
- page_count must match the number of pages in the text markers or PDF metadata.
- detected_date: use ISO format (YYYY-MM-DD) when possible.
"""


def metadata_agent(state: DocumentState) -> dict:
    errors = list(state.get("errors") or [])
    text = state.get("raw_text", "")
    pdf_meta = state.get("pdf_metadata") or {}
    classification = state.get("classification") or {}

    page_count = len(state.get("pages") or []) or pdf_meta.get("page_count", 1)

    if not text.strip():
        return {
            "metadata": {
                "page_count": page_count,
                "detected_date": pdf_meta.get("creation_date"),
                "author": pdf_meta.get("author"),
                "document_type": classification.get("document_type", "other"),
                "title": pdf_meta.get("title"),
                "language": None,
            },
            "current_step": "metadata",
            "errors": errors,
        }

    try:
        llm = get_llm().with_structured_output(MetadataResult)
        result: MetadataResult = llm.invoke(
            METADATA_PROMPT.format(
                pdf_meta=pdf_meta,
                classification=classification,
                text=truncate_for_llm(text, 18_000),
            )
        )
        # Enforce page count from actual extraction
        meta = result.model_dump()
        meta["page_count"] = max(result.page_count, page_count)
        if not meta.get("author") and pdf_meta.get("author"):
            meta["author"] = pdf_meta["author"]
        if not meta.get("title") and pdf_meta.get("title"):
            meta["title"] = pdf_meta["title"]

        return {
            "metadata": meta,
            "current_step": "metadata",
            "errors": errors,
            "debug": {**(state.get("debug") or {}), "metadata": "Metadata extraction complete."},
        }
    except Exception as exc:
        errors.append(f"Metadata agent failed: {exc}")
        return {
            "metadata": {
                "page_count": page_count,
                "author": pdf_meta.get("author"),
                "document_type": classification.get("document_type", "other"),
            },
            "current_step": "metadata",
            "errors": errors,
        }
