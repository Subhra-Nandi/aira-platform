

import os
from tavily import TavilyClient  

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))   

def search_web(query: str, max_results: int = 5) -> list[dict]:
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True
        )
        return response.get("results", [])
    except Exception as e:
        return []