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


class ExaSearchProvider(BaseSearchProvider):
    """Exa search provider implementation"""

    BASE_URL = "https://api.exa.ai"

    def __init__(self, config: SearchConfig):
        """Initialize Exa search provider

        Args:
            config: Search provider configuration
        """
        super().__init__(config)
        self.api_key = config.api_key

    def validate_config(self) -> bool:
        """Validate Exa configuration

        Returns:
            True if configuration is valid
        """
        return bool(self.api_key)

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Perform search using Exa API

        Args:
            request: Search request parameters

        Returns:
            Search response with results

        Raises:
            SearchError: If search fails
        """
        if not self.validate_config():
            raise SearchError(
                "Invalid Exa configuration. API key is required",
                provider=self.name,
                error_code="INVALID_CONFIG",
            )

        start_time = time.time()

        # Prepare request payload
        payload = {
            "query": request.query,
            "num_results": request.max_results or self.config.max_results,
            "text": request.include_content,
            "highlights": True,
            "summary": True if request.search_type == SearchType.RESEARCH else False,
        }

        # Add search type specific parameters
        if request.search_type == SearchType.ACADEMIC:
            payload["type"] = "neural"
            payload["category"] = "research paper"
        elif request.search_type == SearchType.NEWS:
            payload["type"] = "neural"
            payload["category"] = "news"
        elif request.search_type == SearchType.CODE:
            payload["type"] = "neural"
            payload["category"] = "github"
        else:
            payload["type"] = "auto"

        # Add domain filtering
        if request.domains:
            payload["include_domains"] = request.domains

        # Add date filtering
        if request.date_range:
            date_filter = self._parse_date_range(request.date_range)
            if date_filter:
                payload.update(date_filter)

        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

        try:
            # Determine endpoint based on content requirement
            if request.include_content:
                endpoint = "search_and_contents"
            else:
                endpoint = "search"

            url = f"{self.BASE_URL}/{endpoint}"
            response_data = await self._make_request(
                method="POST", url=url, headers=headers, json_data=payload
            )

            search_time = time.time() - start_time

            # Parse response
            results = self._parse_exa_response(response_data, request.include_content)

            return SearchResponse(
                results=results,
                query=request.query,
                provider=SearchProvider.EXA,
                total_results=len(results),
                search_time=search_time,
                metadata={
                    "search_type": payload.get("type"),
                    "category": payload.get("category"),
                    "autoprompt_string": response_data.get("autoprompt_string"),
                },
            )

        except SearchError:
            raise
        except Exception as e:
            logger.error(f"Exa search error: {str(e)}")
            raise SearchError(
                f"Exa search failed: {str(e)}",
                provider=self.name,
                error_code="SEARCH_FAILED",
            )

    def _parse_exa_response(
        self, response_data: Dict[str, Any], include_content: bool
    ) -> List[SearchResult]:
        """Parse Exa API response into SearchResult objects

        Args:
            response_data: Raw response from Exa API
            include_content: Whether content was requested

        Returns:
            List of parsed search results
        """
        results = []

        for item in response_data.get("results", []):
            # Parse published date if available
            published_date = None
            if item.get("published_date"):
                try:
                    published_date = datetime.fromisoformat(item["published_date"])
                except (ValueError, TypeError):
                    pass

            # Get content from different possible fields
            content = None
            if include_content:
                content = item.get("text") or item.get("content") or item.get("summary")

            result = SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=content,
                score=item.get("score"),
                published_date=published_date,
                source=self._extract_domain(item.get("url", "")),
                metadata={
                    "id": item.get("id"),
                    "author": item.get("author"),
                    "highlights": item.get("highlights", []),
                    "summary": item.get("summary"),
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

    def _parse_date_range(self, date_range: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Parse date range for Exa API

        Args:
            date_range: Date range dictionary

        Returns:
            Exa-compatible date filter or None
        """
        try:
            result = {}
            if "start_date" in date_range:
                result["start_published_date"] = date_range["start_date"]
            if "end_date" in date_range:
                result["end_published_date"] = date_range["end_date"]
            return result if result else None
        except (ValueError, TypeError, KeyError):
            return None

    async def get_content(self, urls: List[str]) -> Dict[str, str]:
        """Get content for specific URLs using Exa's contents endpoint

        Args:
            urls: List of URLs to get content for

        Returns:
            Dictionary mapping URLs to their content
        """
        if not self.validate_config():
            raise SearchError(
                "Invalid Exa configuration. API key is required",
                provider=self.name,
                error_code="INVALID_CONFIG",
            )

        payload = {"ids": urls, "text": True}

        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

        try:
            url = f"{self.BASE_URL}/contents"
            response_data = await self._make_request(
                method="POST", url=url, headers=headers, json_data=payload
            )

            content_map = {}
            for item in response_data.get("results", []):
                if item.get("url") and item.get("text"):
                    content_map[item["url"]] = item["text"]

            return content_map

        except Exception as e:
            logger.error(f"Exa content retrieval error: {str(e)}")
            raise SearchError(
                f"Exa content retrieval failed: {str(e)}",
                provider=self.name,
                error_code="CONTENT_RETRIEVAL_FAILED",
            )

    async def find_similar(self, url: str, num_results: int = 10) -> List[SearchResult]:
        """Find similar pages to a given URL

        Args:
            url: URL to find similar pages for
            num_results: Number of similar results to return

        Returns:
            List of similar search results
        """
        if not self.validate_config():
            raise SearchError(
                "Invalid Exa configuration. API key is required",
                provider=self.name,
                error_code="INVALID_CONFIG",
            )

        payload = {"url": url, "num_results": num_results}

        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

        try:
            api_url = f"{self.BASE_URL}/find_similar"
            response_data = await self._make_request(
                method="POST", url=api_url, headers=headers, json_data=payload
            )

            return self._parse_exa_response(response_data, False)

        except Exception as e:
            logger.error(f"Exa find similar error: {str(e)}")
            raise SearchError(
                f"Exa find similar failed: {str(e)}",
                provider=self.name,
                error_code="FIND_SIMILAR_FAILED",
            )

    async def health_check(self) -> SearchProviderStatus:
        """Check Exa API health and status

        Returns:
            Provider status information
        """
        try:
            # Perform a simple test search
            test_payload = {"query": "test", "num_results": 1}

            headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

            url = f"{self.BASE_URL}/search"
            await self._make_request(
                method="POST", url=url, headers=headers, json_data=test_payload
            )

            return SearchProviderStatus(
                provider=SearchProvider.EXA,
                available=True,
                configured=self.validate_config(),
                rate_limit_remaining=self._rate_limit_remaining,
                response_time=self.get_average_response_time(),
            )

        except SearchError as e:
            return SearchProviderStatus(
                provider=SearchProvider.EXA,
                available=False,
                configured=self.validate_config(),
                last_error=e.message,
                rate_limit_remaining=self._rate_limit_remaining,
                response_time=self.get_average_response_time(),
            )
        except Exception as e:
            return SearchProviderStatus(
                provider=SearchProvider.EXA,
                available=False,
                configured=self.validate_config(),
                last_error=str(e),
                rate_limit_remaining=self._rate_limit_remaining,
                response_time=self.get_average_response_time(),
            )
