
def route_question(question: str) -> str:
    """Route a business question to SQL, RAG, or BOTH."""

    q = question.lower().strip()

    combined_phrases = (
        "explain and calculate",
        "define and calculate",
        "rules and calculate",
        "explain with data",
        "based on the rules, calculate",
    )

    if any(phrase in q for phrase in combined_phrases):
        return "BOTH"

    # Definition questions should go to RAG first.
    rag_phrases = (
        "what does",
        "what is",
        "what are",
        "define",
        "definition",
        "meaning",
        "policy",
        "policies",
        "rule",
        "rules",
        "guideline",
        "guidelines",
        "how do we define",
        "business terms",
    )

    if any(phrase in q for phrase in rag_phrases):
        return "RAG"

    sql_keywords = (
        "how many", "how much", "total", "average",
        "highest", "lowest", "most", "least",
        "revenue", "sales", "orders", "products",
        "category", "count", "compare", "top",
        "sum", "price", "quantity", "percentage",
        "calculate",
    )

    if any(word in q for word in sql_keywords):
        return "SQL"

    return "RAG"
