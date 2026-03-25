def detect_intent(goal: str):

    goal_lower = goal.lower()

    if any(word in goal_lower for word in ["future", "next", "predict", "upcoming"]):
        return "future"

    elif any(word in goal_lower for word in ["latest", "current", "now", "trend"]):
        return "current"

    elif any(word in goal_lower for word in ["history", "past", "successful", "case study"]):
        return "past"

    else:
        return "general"