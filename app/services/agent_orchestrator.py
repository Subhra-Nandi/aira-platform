from app.agents.research_agent import run_research
from app.agents.analysis_agent import run_analysis
from app.agents.coding_agent import run_code


def planner(goal: str):
    goal = goal.lower()

    use_research = True  

    use_analysis = any(word in goal for word in [
    "analyze", "analysis", "compare", "evaluate",
    "strategy", "risk", "best", "recommend", "suggest"
])

    use_coding = any(word in goal for word in [
        "code", "build", "implement", "write", "develop", "app", "api"
    ])

    return {
        "research": use_research,
        "analysis": use_analysis,
        "coding": use_coding
    }


def execute_task(goal: str, user_profile: dict = {}, mode: str = "auto"):

    print("MODE:", mode)

   
    plan = planner(goal)
    print("PLAN:", plan)

    results = []

    
    if plan["research"]:
        research = run_research(goal, user_profile=user_profile)
        research_output = research.get("result", "")

        results.append({
            "agent": "research",
            "output": research
        })
    else:
        research_output = goal  

    
    if plan["analysis"]:
        analysis_input = research_output[:4000]

        analysis = run_analysis(analysis_input, user_profile=user_profile)
        analysis_output = analysis.get("result", "")

        results.append({
            "agent": "analysis",
            "output": analysis
        })
    else:
        analysis_output = research_output

    
    if plan["coding"]:
        coding_input = analysis_output[:3000]

        coding = run_code(coding_input, user_profile=user_profile)

        results.append({
            "agent": "coding",
            "output": coding
        })

    return {
    "version": "v1",
    "status": "success",
    "goal": goal,
    "plan": plan,
    "results": [
        {
            "agent": r["agent"],
            "type": r["output"].get("type", "text"),
            "content": r["output"].get("result"),
            "language": r["output"].get("language", None)
        }
        for r in results
    ]
}