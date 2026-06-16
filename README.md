# Multi-Agent Document Processing System

A **LangGraph**-powered pipeline that processes PDF documents through specialized AI agents, using **Google Gemini** (via AI Studio) and fully **open-source** libraries for PDF extraction, embeddings, and vector search.

## Architecture

```
Upload PDF
    │
    ▼
┌─────────────────┐
│  Orchestrator   │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
  OCR      Classifier   Metadata
 (text)   (type)       (pages/date/author)
    │         │            │
    └────┬────┴────────────┘
         ▼
   Validation Agent  ← checks outputs against source text
         ▼
   Extraction Agent  ← structured JSON
         ▼
   Summary Agent
         ▼
   RAG Index         ← Chroma + sentence-transformers
         ▼
   User Q&A
```

## Anti-hallucination measures

- **Low temperature** (0.1) on Gemini
- **PyMuPDF** for deterministic text extraction (not LLM-generated OCR)
- **Structured outputs** via Pydantic schemas
- **Validation agent** cross-checks classification & metadata against source
- **RAG** answers only from retrieved chunks with explicit “not found” fallback
- Prompts instruct agents to return `null` instead of guessing

## Tech stack

| Component | Library |
|-----------|---------|
| Orchestration | LangGraph |
| LLM | Gemini 2.5 Flash (Google AI Studio) |
| PDF text | PyMuPDF |
| Embeddings | sentence-transformers (local) |
| Vector DB | ChromaDB |
| UI | Streamlit |

## Quick start

### 1. Clone and install

```bash
cd Multi_Document_Processing_System
python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure API key

Copy `.env.example` to `.env` and set your key:

```bash
copy .env.example .env
```

Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey).

### 3. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501`, upload a PDF, and click **Process Document**.

## Project structure

```
├── app.py                  # Streamlit UI
├── agents/
│   ├── orchestrator.py     # Pipeline coordinator
│   ├── ocr_agent.py        # PDF text extraction
│   ├── classifier_agent.py # Document type classification
│   ├── metadata_agent.py   # Page/date/author/type
│   ├── validation_agent.py # Ground-truth validation
│   ├── extraction_agent.py # JSON structured extraction
│   ├── summary_agent.py    # Executive summary
│   └── rag_agent.py        # Vector index + Q&A
├── graph/
│   ├── state.py            # Shared LangGraph state
│   └── workflow.py         # Graph definition
├── schemas/
│   └── document.py         # Pydantic output schemas
├── utils/
│   ├── pdf_loader.py       # PyMuPDF helpers
│   ├── embeddings.py       # HuggingFace embeddings
│   ├── vector_store.py     # Chroma helpers
│   └── llm.py              # Gemini client
└── config/
    └── settings.py
```

## Document types

The classifier recognizes:

- **contract**
- **invoice**
- **resume**
- **form**
- **other**

## Notes

- **Scanned PDFs**: PyMuPDF extracts text from digital PDFs. Image-only scans need Tesseract OCR (not included by default).
- **First run**: sentence-transformers downloads `all-MiniLM-L6-v2` (~90 MB) on first use.
- **Flask**: This project uses Streamlit for faster iteration. A Flask API can wrap `graph.workflow.run_pipeline` if needed.

## License

MIT — use freely with open-source dependencies listed in `requirements.txt`.
