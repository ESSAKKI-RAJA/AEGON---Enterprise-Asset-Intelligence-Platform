import os
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
from typing import Dict, Any

async def analyze_cost_trend(trend_data: list) -> Dict[str, Any]:
    """Takes financial analytics output and generates structured budget insights."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    narrative = (
        "MOCK: Based on the provided trend, maintenance costs have shown volatility. "
        "We recommend reviewing aging assets to flatten the cost curve."
    )
    
    if api_key and ANTHROPIC_AVAILABLE:
        try:
            client = anthropic.AsyncAnthropic(api_key=api_key)
            prompt = (
                "You are an enterprise financial analyst. "
                f"Given the following monthly maintenance costs for our assets: {trend_data}, "
                "write a 2-sentence executive summary identifying the trend direction and one area of concern."
            )
            response = await client.messages.create(
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
                model="claude-3-haiku-20240307",
            )
            narrative = response.content[0].text
        except Exception as e:
            narrative = f"AI Generation Failed: {str(e)}"
            
    # Return structured intelligence
    return {
        "insight_type": "budget_trend",
        "narrative": narrative,
        "confidence": 0.85,
        "supporting_analytics": trend_data,
        "suggested_actions": ["Review Q3 CAPEX allocation", "Audit high-cost maintenance vendors"]
    }
