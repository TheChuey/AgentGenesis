from duckduckgo_search import DDGS
from moduels.tools import tool

@tool(name="search_internet", description="Searches DuckDuckGo and returns a list of results. Each result is a dict with 'title', 'href', and 'body'.")
def search_internet(query, max_results=5):
    """
    Searches DuckDuckGo and returns a list of results.
    Each result is a dict with 'title', 'href', and 'body'.
    """
    print(f"[TEST POINT] TOOL EXECUTED: search_internet | Query: '{query}'")
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(r)
        return results
    except Exception as e:
        print(f"[ERROR] DuckDuckGo search failed: {e}")
        return []
