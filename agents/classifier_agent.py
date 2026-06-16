"""Classifier Agent — categorize document type with grounded reasoning."""

from graph.state import DocumentState
from schemas.document import ClassificationResult
from utils.llm import get_llm, truncate_for_llm

CLASSIFIER_PROMPT = """You are a document classifier. Classify the document into exactly one category:
contract, invoice, resume, form, or other.

RULES (anti-hallucination):
- Base your decision ONLY on the document text below.
- If uncertain, choose "other" and lower confidence.
- Cite specific phrases from the text in your reasoning.
- Do NOT invent content not present in the text.

Document text:
{text}
"""


def classifier_agent(state: DocumentState) -> dict:
    errors = list(state.get("errors") or [])
    text = state.get("raw_text", "")

    if not text.strip():
        return {
            "classification": {
                "document_type": "other",
                "confidence": 0.0,
                "reasoning": "No text available for classification.",
            },
            "current_step": "classifier",
            "errors": errors,
        }

    try:
        llm = get_llm().with_structured_output(ClassificationResult)
        result: ClassificationResult = llm.invoke(
            CLASSIFIER_PROMPT.format(text=truncate_for_llm(text, 20_000))
        )
        return {
            "classification": result.model_dump(),
            "current_step": "classifier",
            "errors": errors,
            "debug": {
                **(state.get("debug") or {}),
                "classifier": f"Type={result.document_type}, confidence={result.confidence:.2f}",
            },
        }
    except Exception as exc:
        errors.append(f"Classifier failed: {exc}")
        return {
            "classification": {"document_type": "other", "confidence": 0.0, "reasoning": str(exc)},
            "current_step": "classifier",
            "errors": errors,
        }
