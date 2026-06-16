"""LangGraph shared state."""

from typing import Annotated, Any, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class DocumentState(TypedDict, total=False):
    file_path: str
    file_name: str
    raw_text: str
    pages: list[dict]
    pdf_metadata: dict

    # Orchestrator
    pipeline_status: str
    current_step: str

    # Agent outputs
    ocr_complete: bool
    classification: dict
    metadata: dict
    validation: dict
    extracted_json: dict
    summary: dict

    # RAG
    rag_ready: bool
    chat_history: Annotated[list, add_messages]

    errors: list[str]
    debug: dict[str, Any]
