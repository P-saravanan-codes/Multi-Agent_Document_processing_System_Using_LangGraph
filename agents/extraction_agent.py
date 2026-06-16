"""Extraction Agent — structured JSON output by document type."""

from graph.state import DocumentState
from schemas.document import ExtractedFields
from utils.llm import get_llm, truncate_for_llm

EXTRACTION_PROMPT = """Extract structured fields from this {doc_type} document into JSON.

RULES (critical — reduce hallucination):
- Extract ONLY values explicitly present in the text.
- Use null or omit fields when not found.
- For amounts, copy exact strings from the document.
- Do not infer parties, dates, or amounts not stated.

Document text:
{text}

Metadata context:
{metadata}
"""


def extraction_agent(state: DocumentState) -> dict:
    errors = list(state.get("errors") or [])
    text = state.get("raw_text", "")
    metadata = state.get("metadata") or {}
    doc_type = (state.get("classification") or {}).get("document_type", "other")

    if not text.strip():
        return {
            "extracted_json": {"document_type": doc_type, "entities": {}, "note": "No text to extract"},
            "current_step": "extraction",
            "errors": errors,
        }

    try:
        llm = get_llm().with_structured_output(ExtractedFields)
        result: ExtractedFields = llm.invoke(
            EXTRACTION_PROMPT.format(
                doc_type=doc_type,
                text=truncate_for_llm(text, 22_000),
                metadata=metadata,
            )
        )
        extracted = result.model_dump()
        extracted["document_type"] = doc_type

        return {
            "extracted_json": extracted,
            "current_step": "extraction",
            "errors": errors,
            "debug": {**(state.get("debug") or {}), "extraction": "Structured JSON extraction complete."},
        }
    except Exception as exc:
        errors.append(f"Extraction failed: {exc}")
        return {
            "extracted_json": {"document_type": doc_type, "error": str(exc)},
            "current_step": "extraction",
            "errors": errors,
        }
