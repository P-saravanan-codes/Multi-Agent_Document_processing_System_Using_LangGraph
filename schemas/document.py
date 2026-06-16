"""Pydantic schemas for structured agent outputs."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class PageText(BaseModel):
    page_number: int = Field(description="1-based page number")
    text: str = Field(description="Extracted text for this page")


class ClassificationResult(BaseModel):
    document_type: Literal["contract", "invoice", "resume", "form", "other"] = Field(
        description="Primary document category"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    reasoning: str = Field(description="Brief evidence from the document text")


class MetadataResult(BaseModel):
    page_count: int = Field(ge=1)
    detected_date: Optional[str] = Field(
        default=None, description="Primary date found (ISO format if possible)"
    )
    author: Optional[str] = Field(default=None, description="Author or issuer if found")
    document_type: str = Field(description="Document type label")
    title: Optional[str] = Field(default=None, description="Title or subject if found")
    language: Optional[str] = Field(default=None, description="Detected language")


class ValidationIssue(BaseModel):
    field: str
    issue: str
    severity: Literal["error", "warning"]


class ValidationResult(BaseModel):
    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    grounded_score: float = Field(
        ge=0.0, le=1.0, description="How well outputs match source text"
    )


class ExtractedFields(BaseModel):
    """Flexible JSON extraction — keys depend on document type."""

    document_type: str
    entities: dict = Field(default_factory=dict, description="Key-value extracted fields")
    tables: list[dict] = Field(default_factory=list, description="Tabular data if any")
    key_dates: list[str] = Field(default_factory=list)
    parties: list[str] = Field(default_factory=list)
    amounts: list[str] = Field(default_factory=list)


class SummaryResult(BaseModel):
    executive_summary: str = Field(description="2-4 sentence summary grounded in the document")
    key_points: list[str] = Field(description="3-7 bullet points from the document")
    action_items: list[str] = Field(default_factory=list)
