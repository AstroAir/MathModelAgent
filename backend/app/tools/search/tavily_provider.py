from typing import List, Dict, Any, Optional
import time
from datetime import datetime
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchConfig,
    SearchError,
    SearchProviderStatus,
    SearchProvider,
    SearchType,
)
from app.tools.search.base_provider import BaseSearchProvider
from app.utils.log_util import get_logger

logger = get_logger(__name__)


class TavilySearchProvider(BaseSearchProvider):
    """Tavily search provider implementation"""

    BASE_URL = "https://api.tavily.com"

    def __init__(self, config: SearchConfig):
        """Initialize Tavily search provider

        Args:
            config: Search provider configuration
        """
        super().__init__(config)
        self.api_key = config.api_key

    def validate_config(self) -> bool:
        """Validate Tavily configuration

        Returns:
            True if configuration is valid
        """
        return bool(self.api_key and self.api_key.startswith("tvly-"))

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Perform search using Tavily API

        Args:
            request: Search request parameters

        Returns:
            Search response with results

        Raises:
            SearchError: If search fails
        """
        if not self.validate_config():
            raise SearchError(
                "Invalid Tavily configuration. API key must start with 'tvly-'",
                provider=self.name,
                error_code="INVALID_CONFIG",
            )

        start_time = time.time()

        # Prepare request payload
        payload = {
            "api_key": self.api_key,
            "query": request.query,
            "search_depth": "advanced"
            if request.search_type == SearchType.RESEARCH
            else "basic",
            "include_answer": True,
            "include_raw_content": request.include_content,
            "max_results": request.max_results or self.config.max_results,
            "include_domains": request.domains or [],
        }

        # Add search type specific parameters
        if request.search_type == SearchType.NEWS:
            payload["topic"] = "news"
        elif request.search_type == SearchType.ACADEMIC:
            payload["topic"] = "research"

        # Add date range if specified
        if request.date_range:
            payload["days"] = self._parse_date_range(request.date_range)

        try:
            # Make API request
            url = f"{self.BASE_URL}/search"
            response_data = await self._make_request(
                method="POST", url=url, json_data=payload
            )

            search_time = time.time() - start_time

            # Parse response
            results = self._parse_tavily_response(response_data)

            return SearchResponse(
                results=results,
                query=request.query,
                provider=SearchProvider.TAVILY,
                total_results=len(results),
                search_time=search_time,
                metadata={
                    "answer": response_data.get("answer"),
                    "search_depth": payload["search_depth"],
                    "follow_up_questions": response_data.get("follow_up_questions", []),
                },
            )

        except SearchError:
            raise
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            raise SearchError(
                f"Tavily search failed: {str(e)}",
                provider=self.name,
                error_code="SEARCH_FAILED",
            )

    def _parse_tavily_response(
        self, response_data: Dict[str, Any]
    ) -> List[SearchResult]:
        """Parse Tavily API response into SearchResult objects

        Args:
            response_data: Raw response from Tavily API

        Returns:
            List of parsed search results
        """
        results = []

        for item in response_data.get("results", []):
            # Parse published date if available
            published_date = None
            if item.get("published_date"):
                try:
                    published_date = datetime.fromisoformat(
                        item["published_date"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            result = SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content") or item.get("raw_content"),
                score=item.get("score"),
                published_date=published_date,
                source=self._extract_domain(item.get("url", "")),
                metadata={
                    "raw_content": item.get("raw_content"),
                    "snippet": item.get("content"),
                    "published_date_raw": item.get("published_date"),
                },
            )
            results.append(result)

        return results

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL

        Args:
            url: Full URL

        Returns:
            Domain name or None
        """
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None

    def _parse_date_range(self, date_range: Dict[str, str]) -> Optional[int]:
        """Parse date range into days parameter for Tavily

        Args:
            date_range: Date range dictionary

        Returns:
            Number of days or None
        """
        try:
            if "days" in date_range:
                return int(date_range["days"])
            elif "start_date" in date_range and "end_date" in date_range:
                start = datetime.fromisoformat(date_range["start_date"])
                end = datetime.fromisoformat(date_range["end_date"])
                return (end - start).days
        except (ValueError, TypeError, KeyError):
            pass
        return None

    async def health_check(self) -> SearchProviderStatus:
        """Check Tavily API health and status

        Returns:
            Provider status information
        """
        try:
            # Perform a simple test search
            test_payload = {"api_key": self.api_key, "query": "test", "max_results": 1}

            url = f"{self.BASE_URL}/search"
            await self._make_request(method="POST", url=url, json_data=test_payload)

            return SearchProviderStatus(
                provider=SearchProvider.TAVILY,
                available=True,
                configured=self.validate_config(),
                rate_limit_remaining=self._rate_limit_remaining,
                response_time=self.get_average_response_time(),
            )

        except SearchError as e:
            return SearchProviderStatus(
                provider=SearchProvider.TAVILY,
                available=False,
                configured=self.validate_config(),
                last_error=e.message,
                rate_limit_remaining=self._rate_limit_remaining,
                response_time=self.get_average_response_time(),
            )
        except Exception as e:
            return SearchProviderStatus(
                provider=SearchProvider.TAVILY,
                available=False,
                configured=self.validate_config(),
                last_error=str(e),
                rate_limit_remaining=self._rate_limit_remaining,
                response_time=self.get_average_response_time(),
            )
