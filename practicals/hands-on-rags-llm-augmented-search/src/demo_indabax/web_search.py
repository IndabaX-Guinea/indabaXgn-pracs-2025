"""
Web Search Tool
Provides web search capabilities as fallback when RAG doesn't have the answer
"""

from typing import Any

from duckduckgo_search import DDGS


class WebSearchTool:
    """Simple web search using DuckDuckGo"""

    def __init__(self, max_results: int = 3):
        self.max_results = max_results
        self.ddgs = DDGS()

    def search(self, query: str, max_results: int | None = None) -> list[dict[str, Any]]:
        """
        Search the web and return results

        Args:
            query: Search query
            max_results: Number of results to return (default: self.max_results)

        Returns:
            List of search results with title, snippet, and link
        """
        max_results = max_results or self.max_results

        try:
            results = []
            search_results = self.ddgs.text(query, max_results=max_results)

            for result in search_results:
                results.append(
                    {
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "link": result.get("href", ""),
                    }
                )

            return results

        except Exception as e:
            print(f"Web search error: {e}")
            return []

    def format_results_for_context(self, results: list[dict[str, Any]]) -> str:
        """
        Format search results for LLM context

        Args:
            results: List of search results

        Returns:
            Formatted string with search results
        """
        if not results:
            return "No web search results found."

        context = "Web search results:\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['title']}\n"
            context += f"   {result['snippet']}\n"
            context += f"   Source: {result['link']}\n\n"

        return context
