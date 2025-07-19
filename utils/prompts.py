"""
prompts.py
Module for constructing LLM prompts with retrieved context.
"""
from typing import List, Dict, Any

def build_prompt(question: str, context_chunks: List[Any]) -> str:
    """
    Build a prompt for LLM with context chunks.
    Args:
        question: The business analysis question
        context_chunks: List of context chunks (can be strings or dicts with 'text' key)
    Returns:
        Formatted prompt string
    """
    # Extract text from context chunks
    context_texts = []
    for i, chunk in enumerate(context_chunks):
        if isinstance(chunk, dict):
            text = chunk.get('text', str(chunk))
        else:
            text = str(chunk)
        context_texts.append(text)
    
    # Join all context into a single block
    context_block = "\n\n".join(context_texts)
    
    # Determine industry from context to provide more specific guidance
    industry = "business"
    if any('customer' in text.lower() or 'item' in text.lower() or 'category' in text.lower() for text in context_texts):
        industry = "retail"
    elif any('date' in text.lower() or 'open' in text.lower() or 'close' in text.lower() or 'volume' in text.lower() for text in context_texts):
        industry = "finance"
    
    # Industry-specific instructions
    if industry == "retail":
        industry_guidance = """
- Focus on customer behavior, product performance, and sales patterns
- Analyze purchasing trends, customer demographics, and regional differences
- Provide actionable insights for inventory management and marketing strategies
- Consider customer satisfaction, payment preferences, and shipping patterns
- If specific data is limited, provide insights based on available patterns and trends"""
    elif industry == "finance":
        industry_guidance = """
- Focus on market trends, price movements, and trading patterns
- Analyze volatility, volume trends, and market sentiment
- Provide insights for investment decisions and risk assessment
- Consider market timing, price correlations, and trading opportunities
- If specific data is limited, provide insights based on available market indicators"""
    else:
        industry_guidance = """
- Focus on key business metrics and performance indicators
- Analyze trends, patterns, and correlations in the data
- Provide actionable insights for strategic decision-making
- Consider implications for business growth and optimization
- If specific data is limited, provide insights based on available patterns"""
    
    # Enhanced prompt with better guidance for limited data scenarios
    prompt = f"""You are an expert {industry} analyst with deep knowledge of data analysis and business intelligence. Your task is to provide comprehensive, actionable insights based on the provided data.

IMPORTANT: Even if the data doesn't perfectly match the question, provide the best possible analysis using available information. Focus on extracting meaningful insights rather than stating "not found."

Context Data:
{context_block}

Business Question: {question}

Analysis Requirements:
1. **Direct Answer**: Provide a clear, specific answer to the question using the available data
2. **Quantitative Analysis**: Include specific numbers, percentages, and calculations when possible
3. **Business Insights**: Explain what the data means for business decision-making
4. **Strategic Implications**: Provide actionable recommendations based on your analysis
5. **Data Limitations**: Acknowledge any limitations in the available data, but still provide insights
6. **Industry Context**: Consider {industry}-specific factors and market dynamics
7. **Alternative Analysis**: If the exact question cannot be answered, provide related insights

{industry_guidance}

Response Guidelines:
- **Always provide value**: Even with limited data, extract meaningful insights
- **Be specific**: Use exact numbers and calculations when available
- **Think strategically**: Connect data to business implications
- **Acknowledge limitations**: Be transparent about data constraints while still providing analysis
- **Provide context**: Explain what the findings mean in practical terms

Response Structure:
1. **Direct Answer**: Answer the question as best as possible with available data
2. **Supporting Evidence**: Present relevant data, calculations, and patterns
3. **Business Implications**: Explain what this means for decision-making
4. **Strategic Recommendations**: Offer actionable next steps
5. **Data Context**: Note any limitations while emphasizing available insights

Your response should be comprehensive (minimum 200 words) and demonstrate analytical thinking. Focus on providing business value rather than stating what cannot be done.

Answer:"""
    
    return prompt 