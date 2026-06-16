from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def build_resume_pdf() -> Path:
    base = Path(__file__).resolve().parent
    out_path = base / "Saravanan_AI_Engineer_Resume_ATS.pdf"

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        spaceAfter=4,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        spaceBefore=6,
        spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
        spaceAfter=2,
    )

    story = []
    story.append(Paragraph("SARAVANAN P", title_style))
    story.append(
        Paragraph(
            "Bangalore, India | +91-8296563468 | saranpandi2378@gmail.com | "
            "linkedin.com/in/saravananp04 | github.com/P-saravanan-codes",
            body_style,
        )
    )
    story.append(Spacer(1, 4))

    story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    story.append(
        Paragraph(
            "AI Engineer with hands-on experience building production-ready ML and Generative AI applications "
            "using Python, NLP, RAG, and MLOps practices. Strong background in model development, document "
            "intelligence, vector search, API deployment, and cloud infrastructure. Built end-to-end AI systems "
            "with measurable gains in response quality, retrieval speed, and reliability.",
            body_style,
        )
    )

    story.append(Paragraph("TECHNICAL SKILLS", heading_style))
    skill_lines = [
        "<b>Languages:</b> Python, SQL",
        "<b>AI/ML:</b> Supervised Learning, Unsupervised Learning, NLP, Computer Vision, Feature Engineering, Model Evaluation",
        "<b>GenAI:</b> LLMs, LangChain, LangGraph, RAG, Prompt Engineering, Ollama, Hugging Face",
        "<b>Vector Databases:</b> Pinecone, FAISS, ChromaDB",
        "<b>Deployment:</b> Flask, FastAPI, REST APIs, Docker (Basics)",
        "<b>Cloud/Tools:</b> AWS (EC2, S3), Git, VS Code, Azure Machine Learning Studio",
    ]
    for line in skill_lines:
        story.append(Paragraph(f"- {line}", body_style))

    story.append(Paragraph("EXPERIENCE", heading_style))
    story.append(
        Paragraph(
            "<b>AI/ML Engineer Intern | ExcelR Solutions, Bangalore | Jun 2025 - Dec 2025</b>",
            body_style,
        )
    )
    exp_lines = [
        "Completed an intensive AI/ML training program with implementation across classification, regression, clustering, NLP, and deployment use cases.",
        "Developed and evaluated 5+ ML models using real-world datasets and delivered actionable performance insights.",
        "Built complete ML workflows including preprocessing, feature engineering, model tuning, validation, and API deployment.",
        "Improved project delivery quality through structured experimentation and reproducible development practices.",
    ]
    for line in exp_lines:
        story.append(Paragraph(f"- {line}", body_style))

    story.append(Paragraph("PROJECTS", heading_style))
    story.append(Paragraph("<b>1) AI Medical Chatbot (LLM + RAG Pipeline) | Dec 2025 - Feb 2026</b>", body_style))
    p1_lines = [
        "Built a medical Q&A assistant using LangChain, Ollama, and RAG with 10,000+ indexed medical documents.",
        "Improved answer accuracy by 30% and reduced response latency by 20% through retrieval and prompt optimization.",
        "Implemented Flask/FastAPI services, AWS EC2 deployment, and S3-backed document storage.",
        "Applied retrieval-grounded response logic to reduce hallucinations and improve answer trustworthiness.",
        "Tech: Python, LangChain, Ollama, Pinecone, FAISS, Flask, FastAPI, AWS EC2/S3, Docker",
    ]
    for line in p1_lines:
        story.append(Paragraph(f"- {line}", body_style))

    story.append(
        Paragraph("<b>2) Multi-Agent Document Processing System (LangGraph) | 2026</b>", body_style)
    )
    p2_lines = [
        "Designed and implemented a multi-agent pipeline for PDF processing: Orchestrator, OCR, Classifier, Metadata, Validation, Extraction, Summary, and RAG Q&A agents.",
        "Built structured extraction for contracts, invoices, resumes, and forms with JSON outputs using Pydantic schemas.",
        "Integrated ChromaDB + sentence-transformers for document-grounded question answering and retrieval.",
        "Added validation guardrails to improve factual consistency, reduce hallucination risk, and increase output reliability.",
        "Tech: Python, LangGraph, Gemini 2.5 Flash, PyMuPDF, ChromaDB, sentence-transformers, Streamlit, Flask-ready architecture",
    ]
    for line in p2_lines:
        story.append(Paragraph(f"- {line}", body_style))

    story.append(Paragraph("EDUCATION", heading_style))
    story.append(
        Paragraph(
            "B.Tech, Artificial Intelligence and Data Science | Sri Shakthi Institute of Engineering and Technology, Coimbatore | 2021 - 2025",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Relevant Coursework: Machine Learning, NLP, Computer Vision, Data Structures and Algorithms",
            body_style,
        )
    )

    story.append(Paragraph("CERTIFICATIONS", heading_style))
    story.append(Paragraph("- AI/ML Program, ExcelR Solutions (2025)", body_style))
    story.append(Paragraph("- Hugging Face NLP Course (iNeuron)", body_style))

    story.append(Paragraph("ADDITIONAL INFORMATION", heading_style))
    story.append(
        Paragraph(
            "- GitHub portfolio includes AI applications in LLMs, document intelligence, and computer vision.",
            body_style,
        )
    )
    story.append(
        Paragraph("- Languages: Tamil (Native), English (Fluent), Kannada (Conversational)", body_style)
    )

    doc.build(story)
    return out_path


if __name__ == "__main__":
    path = build_resume_pdf()
    print(path)
