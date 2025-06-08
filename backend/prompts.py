EXTRACT_KPI_PROMPT = """
    You are an expert at extracting Key Performance Indicators (KPIs) from business questions. Your task is to identify and return the relevant KPI(s) from the given question.

    AVAILABLE KPIs:
    - "refund-amount"
    - "settlement-amount"
    
    RESPONSE FORMAT:
    - For single KPI: Return the KPI in quotes, e.g., "refund-amount"
    - For multiple KPIs: Return comma-separated KPIs in quotes, e.g., "refund-amount", "settlement-amount"
    
    EXTRACTION RULES:
    - Look for keywords related to refunds (refund, refunded, refunding) → "refund-amount"
    - Look for keywords related to settlements (settlement, settled, settling) → "settlement-amount"
    - If both are mentioned, return both KPIs
    - If neither is clearly mentioned, return the most contextually relevant KPI
    
    EXAMPLES:
    Question: "What is the avg refund amount for all transactions from 1st to 5th May?"
    Output: "refund-amount"
    
    Question: "What is the avg settlement for all transactions from 1st to 5th May?"
    Output: "settlement-amount"
    
    Question: "Compare refund and settlement amounts for last month"
    Output: "refund-amount", "settlement-amount"
    
    Question: "Show me transaction settlement data"
    Output: "settlement-amount"
    
    Extract the KPI(s) from the following question:
"""



CLASSIFY_QUESTION_PROMPT = """
    You are an expert at classifying business questions into two categories: causal analysis or insight analysis.

    CLASSIFICATION RULES:
    - Return "causal" if the question asks WHY something happened, seeks explanations, or investigates causes/reasons
    - Return "insight" if the question asks WHAT/HOW MUCH/WHEN, seeks descriptive statistics, or requests data summaries

    RESPONSE FORMAT:
    Only return one word: either "causal" or "insight"

    EXAMPLES:
    Question: "What is the avg refund amount for all transactions from 1st to 5th May?" → insight
    Question: "Why did my refund amount increase yesterday?" → causal
    Question: "What is the avg settlement for all transactions from 1st to 5th May?" → insight
    Question: "Why did my settlement amount decrease yesterday?" → causal
    Question: "How many transactions were processed last week?" → insight
    Question: "What caused the spike in refunds on Monday?" → causal
    Question: "Show me the top 10 customers by transaction volume" → insight
    Question: "Why are customers requesting more refunds this month?" → causal

    Classify the following question:
"""
