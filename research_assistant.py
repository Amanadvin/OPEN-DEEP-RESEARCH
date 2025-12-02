from tavily import TavilyClient
import os

TAVILY_API_KEY = "YOUR_REAL_TAVILY_API_KEY"
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def searcher_agent(question: str):
    try:
        response = tavily.search(
            query=question,
            include_answer=True,
            max_results=5
        )

        results_list = []
        for item in response.get("results", []):
            results_list.append({
                "content": item.get("content", ""),
                "url": item.get("url", "")
            })

        return {
            "answer": response.get("answer", ""),
            "sources": results_list
        }

    except Exception as e:
        return {
            "answer": f"Error: {e}",
            "sources": []
        }
