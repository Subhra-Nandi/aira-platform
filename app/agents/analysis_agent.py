

from app.services.llm_service import generate_response


def run_analysis(goal: str, user_profile: dict = {}):

    prompt = f"""
You are a data analyst.

Analyze the following:
{goal}

Provide:
- patterns
- insights
- conclusions
"""

    result = generate_response(prompt)

    return {
    "agent": "analysis-agent",
    "result": result,
    "type": "text"
}