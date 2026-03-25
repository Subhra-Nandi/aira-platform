

from app.services.llm_service import generate_response
from app.tools.web_search import search_web
from app.services.intent_detector import detect_intent
from app.memory.vector_store import VectorStore
from datetime import datetime
import re

vector_db = VectorStore()

MAX_INPUT_TOKENS = 7500

def estimate_tokens(text: str) -> int:
    return len(text) // 4

def smart_truncate(results: list[dict], token_budget: int) -> str:
    output = []
    used = 0
    sorted_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

    for r in sorted_results:
        block = (
            f"SOURCE: {r.get('title', '')}\n"
            f"URL: {r.get('url', '')}\n"
            f"CONTENT: {r.get('content', '')[:300]}\n"
        )
        tokens = estimate_tokens(block)
        if used + tokens > token_budget:
            break
        output.append(block)
        used += tokens

    return "\n---\n".join(output)


def build_profile_block(user_profile: dict) -> str:
    """ Converts user profile into a prompt block."""
    if not user_profile:
        return ""

    return f"""
FOUNDER PROFILE:
- Background: {user_profile.get('background', 'unknown')}
- Industry: {user_profile.get('industry', 'general')}
- Risk Appetite: {user_profile.get('risk_appetite', 'medium')}
- Technical Level: {user_profile.get('technical_level', 'intermediate')}
- Location: {user_profile.get('location', 'unknown')}
- Budget: {user_profile.get('budget', 'unknown')}
- Team Size: {user_profile.get('team_size', 'solo')}

PERSONALIZATION RULES:
- Tailor ALL 3 ideas specifically to this founder
- If solo + bootstrap → avoid capital-heavy ideas
- If non-technical → avoid deep R&D ideas, prefer no-code or partnership-based solutions
- If India-based → add India-specific market angle for each idea
- If domain expert → prioritize ideas in their industry first
"""


def run_research(goal: str, user_profile: dict = {}):
    current_year = datetime.now().year
    intent = detect_intent(goal)
    goal_clean = re.sub(r"\b20\d{2}\b", str(current_year), goal)

    past_data = vector_db.search(goal_clean)
    past_context = " ".join(past_data)[:400] if past_data else ""

    if intent == "future":
        query1 = f"{goal_clean} AI startup opportunities {current_year + 1}"
        query2 = f"{goal_clean} funding rounds competitors market size"
    elif intent == "past":
        query1 = "successful AI startups lessons learned case studies"
        query2 = f"{goal_clean} startup failures mistakes"
    else:
        query1 = f"{goal_clean} AI startup trends {current_year}"
        query2 = f"{goal_clean} market gaps competitors funding"

    raw1 = search_web(query1)
    raw2 = search_web(query2)

    data1 = smart_truncate(raw1, token_budget=1800)
    data2 = smart_truncate(raw2, token_budget=1600)

    #  Build profile block from user_profile
    profile_block = build_profile_block(user_profile)

    prompt = f"""You are a startup strategist. Be specific and cite sources.

INTENT: {intent} | YEAR: {current_year}

{profile_block}

RESEARCH DATA:
{data1}

MARKET & COMPETITOR DATA:
{data2}

PRIOR CONTEXT: {past_context}

TASK: {goal_clean}

Respond with exactly:
## Insights (3 bullet points, cite sources by URL)
## Idea 1: [Name] — Problem / Solution / Why Now / Real Competitors / Market Size (cited) / Business Model / Difficulty
## Idea 2: [Name] — same format  
## Idea 3: [Name] — same format
## Biggest Risk for each idea (1 line each)
## Your Best First Step (1 actionable step per idea tailored to this founder)"""

    
    prompt_tokens = estimate_tokens(prompt)

    if prompt_tokens > MAX_INPUT_TOKENS:
        return {
            "agent": "research-agent",
            "intent": intent,
            "result": None,
            "error": "token_limit_exceeded",
            "message": f" Token limit exceeded: prompt is ~{prompt_tokens} tokens, max is {MAX_INPUT_TOKENS}. Try a shorter goal.",
            "prompt_tokens": prompt_tokens
        }

    result = generate_response(prompt)
    vector_db.add_document(result)

    return {
    "agent": "research-agent",
    "intent": intent,
    "result": result,
    "type": "text",
    "prompt_tokens": prompt_tokens
}