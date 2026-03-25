from app.services.llm_service import generate_response


def run_code(goal: str, user_profile: dict = {}):

    prompt = f"""
You are a senior backend engineer.

TASK:
{goal}

Return:

1. Project structure
2. Complete code files

STRICT RULES:
- No explanation
- Only code
- Use clear file separation like:

# filename: app.py
<code>

# filename: requirements.txt
<code>
"""

    try:
        result = generate_response(prompt)
    except Exception as e:
        result = f"Error generating code: {str(e)}"

    clean_result = result.strip() if result else ""

    return {
    "agent": "coding-agent",
    "result": clean_result,   
    "type": "code",
    "language": "python"
}