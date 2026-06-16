"""LangGraph document processing pipeline."""

from langgraph.graph import END, START, StateGraph

from agents.classifier_agent import classifier_agent
from agents.extraction_agent import extraction_agent
from agents.metadata_agent import metadata_agent
from agents.ocr_agent import ocr_agent
from agents.orchestrator import orchestrator_agent
from agents.rag_agent import rag_index_agent
from agents.summary_agent import summary_agent
from agents.validation_agent import validation_agent
from graph.state import DocumentState


def build_document_graph():
    """
    Pipeline:
    START → Orchestrator → OCR → Classifier → Metadata
         → Validation → Extraction → Summary → RAG Index → END
    """
    workflow = StateGraph(DocumentState)

    workflow.add_node("orchestrator", orchestrator_agent)
    workflow.add_node("ocr", ocr_agent)
    workflow.add_node("classifier", classifier_agent)
    workflow.add_node("metadata", metadata_agent)
    workflow.add_node("validation", validation_agent)
    workflow.add_node("extraction", extraction_agent)
    workflow.add_node("summary", summary_agent)
    workflow.add_node("rag_index", rag_index_agent)

    workflow.add_edge(START, "orchestrator")
    workflow.add_edge("orchestrator", "ocr")
    workflow.add_edge("ocr", "classifier")
    workflow.add_edge("classifier", "metadata")
    workflow.add_edge("metadata", "validation")
    workflow.add_edge("validation", "extraction")
    workflow.add_edge("extraction", "summary")
    workflow.add_edge("summary", "rag_index")
    workflow.add_edge("rag_index", END)

    return workflow.compile()


def run_pipeline(file_path: str, file_name: str) -> DocumentState:
    """Execute the full multi-agent pipeline on a PDF."""
    graph = build_document_graph()
    initial: DocumentState = {
        "file_path": file_path,
        "file_name": file_name,
        "errors": [],
        "debug": {},
        "pipeline_status": "pending",
    }
    return graph.invoke(initial)

