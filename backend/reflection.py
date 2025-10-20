def reflect_answer(answer: str, query: str, ctx: str) -> str:
    """
    Reflects on the answer: Checks for clarity, relevance, and suggests improvements.
    Yeh function answer ko query aur context se compare karta hai.
    """
    # Simple checks: Length, keywords, aur context tie-in
    if len(answer) < 100:
        return "❌ Reflection: Jawab thoda chhota hai—agla baar zyada examples add karo!"
    
    query_lower = query.lower()
    answer_lower = answer.lower()
    
    # Relevance check: Query ke key words answer mein hain?
    if any(word in answer_lower for word in query_lower.split()[:3]):
        relevance = "✅ High relevance"
    else:
        relevance = "⚠️ Low relevance—query ke main points miss ho gaye."
    
    # Context usage
    if len(ctx) > 0 and any("past" in answer_lower or "earlier" in answer_lower):
        context_use = "✅ Good use of past context!"
    else:
        context_use = "💡 Suggestion: Agli baar past learning ko reference karo."
    
    return f"{relevance} | {context_use} | Overall: User ko step-by-step guide mila '{query[:30]}...' pe."