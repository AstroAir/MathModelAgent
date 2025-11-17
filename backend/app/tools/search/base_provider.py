from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
import time
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchConfig,
    SearchError,
    SearchProviderStatus,
)
from app.tools.search.rate_limiter import rate_limiter
from app.utils.log_util import get_logger

logger = get_logger(__name__)


class BaseSearchProvider(ABC):
    """Abstract base class for search providers"""

    def __init__(self, config: SearchConfig):
        """Initialize the search provider with configuration

        Args:
            config: Search provider configuration
        """
        self.config = config
        self.name = config.provider.value
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_remaining: Optional[int] = None
        self._last_request_time: float = 0
        self._response_times: List[float] = []

        # Set up rate limiting if configured
        if config.rate_limit:
            rate_limiter.set_limit(self.name, config.rate_limit)

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _ensure_session(self):
        """Ensure aiohttp session is created"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close the aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()

    @abstractmethod
    async def search(self, request: SearchRequest) -> SearchResponse:
        """Perform search using the provider

        Args:
            request: Search request parameters

        Returns:
            Search response with results

        Raises:
            SearchError: If search fails
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration

        Returns:
            True if configuration is valid
        """
        pass

    @abstractmethod
    async def health_check(self) -> SearchProviderStatus:
        """Check provider health and status

        Returns:
            Provider status information
        """
        pass

    def _record_response_time(self, response_time: float):
        """Record response time for monitoring

        Args:
            response_time: Response time in seconds
        """
        self._response_times.append(response_time)
        # Keep only last 100 response times
        if len(self._response_times) > 100:
            self._response_times = self._response_times[-100:]

    def get_average_response_time(self) -> Optional[float]:
        """Get average response time

        Returns:
            Average response time in seconds, or None if no data
        """
        if not self._response_times:
            return None
        return sum(self._response_times) / len(self._response_times)

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and monitoring

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            params: URL parameters
            json_data: JSON request body

        Returns:
            Response JSON data

        Raises:
            SearchError: If request fails
        """
        if not await rate_limiter.acquire(self.name):
            raise SearchError(
                f"Rate limit exceeded for {self.name}",
                provider=self.name,
                error_code="RATE_LIMIT_EXCEEDED",
            )

        await self._ensure_session()

        start_time = time.time()

        try:
            async with self._session.request(
                method=method, url=url, headers=headers, params=params, json=json_data
            ) as response:
                response_time = time.time() - start_time
                self._record_response_time(response_time)

                # Update rate limit info if available
                if "x-ratelimit-remaining" in response.headers:
                    self._rate_limit_remaining = int(
                        response.headers["x-ratelimit-remaining"]
                    )
                else:
                    self._rate_limit_remaining = rate_limiter.get_remaining_requests(
                        self.name
                    )

                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    raise SearchError(
                        f"Rate limit exceeded for {self.name}",
                        provider=self.name,
                        error_code="RATE_LIMIT_EXCEEDED",
                    )
                elif response.status == 401:
                    raise SearchError(
                        f"Authentication failed for {self.name}",
                        provider=self.name,
                        error_code="AUTH_FAILED",
                    )
                elif response.status == 403:
                    raise SearchError(
                        f"Access forbidden for {self.name}",
                        provider=self.name,
                        error_code="ACCESS_FORBIDDEN",
                    )
                else:
                    error_text = await response.text()
                    raise SearchError(
                        f"HTTP {response.status}: {error_text}",
                        provider=self.name,
                        error_code=f"HTTP_{response.status}",
                    )

        except aiohttp.ClientError as e:
            response_time = time.time() - start_time
            self._record_response_time(response_time)
            raise SearchError(
                f"Network error for {self.name}: {str(e)}",
                provider=self.name,
                error_code="NETWORK_ERROR",
            )
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self._record_response_time(response_time)
            raise SearchError(
                f"Request timeout for {self.name}",
                provider=self.name,
                error_code="TIMEOUT",
            )

    def get_status(self) -> SearchProviderStatus:
        """Get current provider status

        Returns:
            Current provider status
        """
        return SearchProviderStatus(
            provider=self.config.provider,
            available=True,  # Override in subclasses based on actual checks
            configured=self.validate_config(),
            rate_limit_remaining=self._rate_limit_remaining,
            response_time=self.get_average_response_time(),
        )
