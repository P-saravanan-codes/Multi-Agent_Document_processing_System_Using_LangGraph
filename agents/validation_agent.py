"""Validation Agent — cross-check agent outputs against source text."""

from graph.state import DocumentState
from schemas.document import ValidationResult
from utils.llm import get_llm, truncate_for_llm

VALIDATION_PROMPT = """You are a strict validation agent. Verify that classification, metadata, and any claims
are grounded in the source document text.

Source document text:
{text}

Classification output:
{classification}

Metadata output:
{metadata}

Check for:
1. Document type matches actual content
2. Dates, author, title appear in text or PDF metadata
3. No fabricated entities
4. Page count is reasonable

Return is_valid=false if major hallucinations or mismatches exist.
grounded_score: 0.0 (not grounded) to 1.0 (fully grounded).
"""


def validation_agent(state: DocumentState) -> dict:
    errors = list(state.get("errors") or [])
    text = state.get("raw_text", "")
    classification = state.get("classification") or {}
    metadata = state.get("metadata") or {}

    if not text.strip():
        return {
            "validation": {
                "is_valid": False,
                "issues": [{"field": "raw_text", "issue": "Empty document text", "severity": "error"}],
                "grounded_score": 0.0,
            },
            "current_step": "validation",
            "errors": errors,
        }

    try:
        llm = get_llm().with_structured_output(ValidationResult)
        result: ValidationResult = llm.invoke(
            VALIDATION_PROMPT.format(
                text=truncate_for_llm(text, 16_000),
                classification=classification,
                metadata=metadata,
            )
        )
        validation = result.model_dump()
        if not result.is_valid:
            for issue in result.issues:
                if issue.severity == "error":
                    errors.append(f"Validation: {issue.field} — {issue.issue}")

        return {
            "validation": validation,
            "current_step": "validation",
            "errors": errors,
            "debug": {
                **(state.get("debug") or {}),
                "validation": f"valid={result.is_valid}, grounded={result.grounded_score:.2f}",
            },
        }
    except Exception as exc:
        errors.append(f"Validation failed: {exc}")
        return {
            "validation": {"is_valid": True, "issues": [], "grounded_score": 0.5},
            "current_step": "validation",
            "errors": errors,
        }
