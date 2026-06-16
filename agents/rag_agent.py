"""RAG Agent — build vector index and answer questions from document chunks."""

from langchain_core.messages import AIMessage, HumanMessage

from graph.state import DocumentState
from utils.llm import get_llm, truncate_for_llm
from utils.vector_store import build_vector_store, load_vector_store

RAG_ANSWER_PROMPT = """Answer the user's question using ONLY the retrieved document context below.

RULES:
- If the answer is not in the context, say "I cannot find this information in the document."
- Quote or paraphrase closely from the context.
- Do not use outside knowledge.

Retrieved context:
{context}

Question: {question}
"""


def rag_index_agent(state: DocumentState) -> dict:
    """Build Chroma index after pipeline completes."""
    errors = list(state.get("errors") or [])
    text = state.get("raw_text", "")
    file_path = state.get("file_path", "")

    if not text.strip() or not file_path:
        return {"rag_ready": False, "errors": errors, "current_step": "rag_index"}

    try:
        build_vector_store(text, file_path)
        return {
            "rag_ready": True,
            "current_step": "rag_index",
            "errors": errors,
            "debug": {**(state.get("debug") or {}), "rag": "Vector index built."},
        }
    except Exception as exc:
        errors.append(f"RAG indexing failed: {exc}")
        return {"rag_ready": False, "errors": errors, "current_step": "rag_index"}


def answer_question(file_path: str, question: str, k: int = 4) -> str:
    """Retrieve relevant chunks and generate a grounded answer."""
    store = load_vector_store(file_path)
    if store is None:
        return "Document index not found. Please process the PDF first."

    docs = store.similarity_search(question, k=k)
    if not docs:
        return "No relevant passages found in the document."

    context = "\n\n---\n\n".join(d.page_content for d in docs)
    llm = get_llm()
    response = llm.invoke(
        RAG_ANSWER_PROMPT.format(
            context=truncate_for_llm(context, 12_000),
            question=question,
        )
    )
    return response.content if hasattr(response, "content") else str(response)


def rag_chat_node(state: DocumentState) -> dict:
    """Optional graph node for chat messages in state."""
    messages = state.get("chat_history") or []
    if not messages:
        return {}

    last = messages[-1]
    if not isinstance(last, HumanMessage):
        return {}

    answer = answer_question(state["file_path"], last.content)
    return {"chat_history": [AIMessage(content=answer)]}
