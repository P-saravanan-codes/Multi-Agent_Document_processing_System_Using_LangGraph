"""Shared Gemini LLM factory."""

import os

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_MODEL, LLM_TEMPERATURE

_llm_instance: ChatGoogleGenerativeAI | None = None
_llm_key_used: str | None = None


def get_llm() -> ChatGoogleGenerativeAI:
    """Return a cached Gemini client; re-create if the API key changes."""
    global _llm_instance, _llm_key_used
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is not set. Add it to .env or the Streamlit sidebar."
        )
    if _llm_instance is None or _llm_key_used != api_key:
        _llm_instance = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=api_key,
            temperature=LLM_TEMPERATURE,
        )
        _llm_key_used = api_key
    return _llm_instance


def truncate_for_llm(text: str, max_chars: int = 28_000) -> str:
    """Keep prompts within model context while preserving head and tail."""
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + "\n\n[... truncated for context ...]\n\n" + text[-half:]
