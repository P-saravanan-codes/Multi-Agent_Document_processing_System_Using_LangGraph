"""Streamlit UI for the Multi-Agent Document Processing System."""

import json
import os
import sys
from pathlib import Path

import streamlit as st

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.rag_agent import answer_question
from config.settings import GEMINI_MODEL, UPLOAD_DIR
from graph.workflow import run_pipeline

st.set_page_config(
    page_title="Multi-Agent Document Processor",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Multi-Agent Document Processing System")
st.caption(
    "LangGraph pipeline · Gemini · OCR → Classify → Metadata → Validate → Extract → Summarize → RAG Q&A"
)

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input(
        "Google AI Studio API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Get a free key at https://aistudio.google.com/app/apikey",
    )
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    st.divider()
    st.markdown(f"**Model:** `{GEMINI_MODEL}`")
    st.markdown("**Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (local)")
    st.markdown("**PDF extraction:** PyMuPDF (open source)")

    st.divider()
    st.markdown("### Agent Pipeline")
    st.markdown(
        """
        1. **Orchestrator** — coordinates workflow
        2. **OCR** — extract text from PDF
        3. **Classifier** — contract / invoice / resume / form
        4. **Metadata** — pages, date, author, type
        5. **Validation** — ground-truth check
        6. **Extraction** — structured JSON
        7. **Summary** — executive summary
        8. **RAG** — ask questions on the document
        """
    )

# --- Upload ---
uploaded = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded:
    save_path = UPLOAD_DIR / uploaded.name
    save_path.write_bytes(uploaded.getvalue())
    st.success(f"Saved: `{uploaded.name}`")

    if st.button("🚀 Process Document", type="primary", use_container_width=True):
        if not api_key and not os.getenv("GOOGLE_API_KEY"):
            st.error("Please enter your Google AI API key in the sidebar.")
        else:
            with st.spinner("Running multi-agent pipeline…"):
                try:
                    result = run_pipeline(str(save_path), uploaded.name)
                    st.session_state["pipeline_result"] = result
                    st.session_state["processed_file"] = str(save_path)
                except Exception as exc:
                    st.error(f"Pipeline failed: {exc}")

# --- Results ---
result = st.session_state.get("pipeline_result")
if result:
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    classification = result.get("classification") or {}
    metadata = result.get("metadata") or {}
    validation = result.get("validation") or {}

    col1.metric("Document Type", classification.get("document_type", "—").title())
    col2.metric("Confidence", f"{classification.get('confidence', 0):.0%}")
    col3.metric("Pages", metadata.get("page_count", "—"))
    col4.metric("Grounded Score", f"{validation.get('grounded_score', 0):.0%}")

    tab_summary, tab_json, tab_meta, tab_text, tab_validate, tab_chat = st.tabs(
        ["Summary", "Extracted JSON", "Metadata", "Raw Text", "Validation", "Ask Questions (RAG)"]
    )

    with tab_summary:
        summary = result.get("summary") or {}
        st.subheader("Executive Summary")
        st.write(summary.get("executive_summary", "—"))
        st.subheader("Key Points")
        for point in summary.get("key_points") or []:
            st.markdown(f"- {point}")
        if summary.get("action_items"):
            st.subheader("Action Items")
            for item in summary["action_items"]:
                st.markdown(f"- {item}")

    with tab_json:
        extracted = result.get("extracted_json") or {}
        st.json(extracted)

    with tab_meta:
        st.json(metadata)
        st.subheader("Classification Reasoning")
        st.info(classification.get("reasoning", "—"))

    with tab_text:
        raw = result.get("raw_text", "")
        st.text_area("Extracted Text", raw, height=400)

    with tab_validate:
        st.json(validation)
        issues = validation.get("issues") or []
        if issues:
            for issue in issues:
                icon = "🔴" if issue.get("severity") == "error" else "🟡"
                st.markdown(f"{icon} **{issue.get('field')}**: {issue.get('issue')}")
        else:
            st.success("No validation issues reported.")

    with tab_chat:
        st.subheader("Ask questions about this document")
        if not result.get("rag_ready"):
            st.warning("RAG index not ready. Re-process the document.")

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        question = st.chat_input("Ask a question about the document…")
        if question:
            st.session_state.chat_messages.append({"role": "user", "content": question})
            file_path = st.session_state.get("processed_file", "")
            with st.spinner("Searching document…"):
                answer = answer_question(file_path, question)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()

    if result.get("errors"):
        with st.expander("⚠️ Pipeline warnings"):
            for err in result["errors"]:
                st.warning(err)

    with st.expander("🔧 Debug info"):
        st.json(result.get("debug") or {})

else:
    st.info("Upload a PDF and click **Process Document** to start the agent pipeline.")
