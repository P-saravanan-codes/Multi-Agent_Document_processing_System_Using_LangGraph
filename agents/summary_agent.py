"""Summary Agent — grounded executive summary and key points."""

from graph.state import DocumentState
from schemas.document import SummaryResult
from utils.llm import get_llm, truncate_for_llm

SUMMARY_PROMPT = """Summarize this document for a business user.

RULES:
- Every statement must be supported by the document text.
- Do not add external knowledge or assumptions.
- If the document is short or sparse, say so honestly.
- key_points must be direct paraphrases of document content.

Document type: {doc_type}

Document text:
{text}
"""


def summary_agent(state: DocumentState) -> dict:
    errors = list(state.get("errors") or [])
    text = state.get("raw_text", "")
    doc_type = (state.get("classification") or {}).get("document_type", "other")

    if not text.strip():
        return {
            "summary": {
                "executive_summary": "No text available to summarize.",
                "key_points": [],
                "action_items": [],
            },
            "current_step": "summary",
            "pipeline_status": "completed",
            "errors": errors,
        }

    try:
        llm = get_llm().with_structured_output(SummaryResult)
        result: SummaryResult = llm.invoke(
            SUMMARY_PROMPT.format(doc_type=doc_type, text=truncate_for_llm(text, 22_000))
        )
        return {
            "summary": result.model_dump(),
            "current_step": "summary",
            "pipeline_status": "completed",
            "errors": errors,
            "debug": {**(state.get("debug") or {}), "summary": "Summary generated."},
        }
    except Exception as exc:
        errors.append(f"Summary failed: {exc}")
        return {
            "summary": {"executive_summary": f"Summary failed: {exc}", "key_points": []},
            "current_step": "summary",
            "pipeline_status": "completed",
            "errors": errors,
        }
