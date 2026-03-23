from app.domain.models import RetrievedChunk

SYSTEM_PROMPT = """You are a precise banking assistant for a financial institution.
Your role is to answer questions about banking products, services, and account terms.

STRICT RULES:
1. Answer ONLY using the information provided in the CONTEXT section below.
2. If the context does not contain sufficient information to answer the question,
   respond with exactly: "I don't have enough information in the available documents to answer this question."
3. Never invent, infer, or assume information that is not explicitly present in the context.
4. Always cite the source document name when providing an answer.
5. Be concise, factual, and professional.
6. Do not provide financial advice beyond what is stated in the documents.
"""


def build_rag_prompt(query: str, chunks: list[RetrievedChunk]) -> list[dict]:
    """
    Build the message list for the LLM using retrieved context.

    Returns a 2-element list: [system_message, user_message]
    The user message embeds the retrieved context and the query.
    """
    if not chunks:
        context = "No relevant documents found."
    else:
        parts = []
        for i, chunk in enumerate(chunks, start=1):
            page_info = f" (page {chunk.page_number})" if chunk.page_number else ""
            parts.append(f"[Source {i}: {chunk.source_file}{page_info}]\n{chunk.text}")
        context = "\n\n---\n\n".join(parts)

    user_message = (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {query}\n\n"
        "Answer based solely on the context above. "
        "If you use information from the context, mention the source document."
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]


def assess_confidence(chunks: list[RetrievedChunk]) -> str:
    """
    Derive a confidence level from retrieval scores.

    Returns: "high" | "medium" | "low" | "insufficient"
    """
    if not chunks:
        return "insufficient"

    avg_score = sum(c.score for c in chunks) / len(chunks)

    if avg_score >= 0.85:
        return "high"
    if avg_score >= 0.70:
        return "medium"
    return "low"
