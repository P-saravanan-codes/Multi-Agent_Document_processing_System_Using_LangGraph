"""Orchestrator — initializes pipeline and coordinates sub-agents."""

from graph.state import DocumentState


def orchestrator_agent(state: DocumentState) -> dict:
    """Prepare document for downstream agents; set routing metadata."""
    errors = list(state.get("errors") or [])
    if not state.get("file_path"):
        errors.append("No PDF file path in state.")
        return {"errors": errors, "pipeline_status": "failed", "current_step": "orchestrator"}

    return {
        "pipeline_status": "processing",
        "current_step": "orchestrator",
        "ocr_complete": False,
        "rag_ready": False,
        "errors": errors,
        "debug": {
            **(state.get("debug") or {}),
            "orchestrator": "Pipeline started — routing to OCR, Classifier, Metadata agents.",
        },
    }
