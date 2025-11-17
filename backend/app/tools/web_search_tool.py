from typing import List, Optional
from app.tools.base import BaseTool, tool
from app.tools.search.search_manager import search_manager
from app.schemas.search import (
    SearchRequest,
    SearchResult,
    SearchProvider,
    SearchType,
    SearchError,
)
from app.schemas.tool_result import ToolResult


class WebSearchTool(BaseTool):
    name: str = "web_search"

    @tool(
        name="web_search",
        description="Performs a web search using a configured provider (Tavily or Exa). Use this to find up-to-date information, code examples, documentation, or research papers.",
        parameters={
            "query": {"type": "string", "description": "The search query string."},
            "search_type": {
                "type": "string",
                "description": "The type of search to perform. Options: 'general', 'academic', 'code', 'news', 'research'. Defaults to 'general'.",
                "enum": [e.value for e in SearchType],
            },
            "provider": {
                "type": "string",
                "description": "The preferred search provider. Options: 'tavily', 'exa'. Defaults to the system's configured default.",
                "enum": [e.value for e in SearchProvider],
            },
            "max_results": {
                "type": "integer",
                "description": "The maximum number of results to return. Defaults to 10.",
            },
        },
        required=["query"],
    )
    async def search(
        self,
        query: str,
        search_type: str = "general",
        provider: Optional[str] = None,
        max_results: int = 10,
    ) -> ToolResult:
        """
        Performs a web search.
        """
        try:
            request = SearchRequest(
                query=query,
                search_type=SearchType(search_type),
                provider=SearchProvider(provider) if provider else None,
                max_results=max_results,
            )
            response = await search_manager.search(request)

            # Format the response for the agent
            formatted_results = self._format_results(response.results)

            return ToolResult(
                result=f"Search successful. Found {len(response.results)} results.\n\n{formatted_results}",
                metadata=response.model_dump(),
            )
        except SearchError as e:
            return ToolResult(
                error=f"Search failed: {e.message}",
                metadata={"provider": e.provider, "error_code": e.error_code},
            )
        except Exception as e:
            return ToolResult(
                error=f"An unexpected error occurred during search: {str(e)}"
            )

    @tool(
        name="get_web_content",
        description="Retrieves the full text content for a list of URLs. Currently only supported by the Exa provider.",
        parameters={
            "urls": {
                "type": "array",
                "description": "A list of URLs to retrieve content for.",
                "items": {"type": "string"},
            }
        },
        required=["urls"],
    )
    async def get_content(self, urls: List[str]) -> ToolResult:
        """
        Retrieves content for a list of URLs.
        """
        try:
            content_map = await search_manager.get_content(urls)
            formatted_content = "\n\n".join(
                [
                    f"URL: {url}\nContent:\n{content[:2000]}..."
                    for url, content in content_map.items()
                ]
            )
            return ToolResult(
                result=f"Successfully retrieved content for {len(content_map)} URLs.\n\n{formatted_content}",
                metadata=content_map,
            )
        except SearchError as e:
            return ToolResult(
                error=f"Failed to get content: {e.message}",
                metadata={"provider": e.provider, "error_code": e.error_code},
            )
        except Exception as e:
            return ToolResult(
                error=f"An unexpected error occurred while getting content: {str(e)}"
            )

    def _format_results(self, results: List[SearchResult]) -> str:
        """
        Formats search results into a readable string.
        """
        if not results:
            return "No results found."

        formatted = []
        for i, res in enumerate(results, 1):
            snippet = res.content or "No snippet available."
            # Truncate snippet for display
            if len(snippet) > 300:
                snippet = snippet[:300] + "..."

            formatted.append(
                f"{i}. {res.title}\n   URL: {res.url}\n   Snippet: {snippet}"
            )

        return "\n".join(formatted)
