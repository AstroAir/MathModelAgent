import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass
from app.utils.log_util import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitInfo:
    """Rate limiting information for a provider"""

    requests_per_minute: int
    requests_made: int = 0
    window_start: float = 0.0
    last_request_time: float = 0.0


class RateLimiter:
    """Rate limiter for search providers"""

    def __init__(self):
        self._limits: Dict[str, RateLimitInfo] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    def set_limit(self, provider: str, requests_per_minute: int):
        """Set rate limit for a provider

        Args:
            provider: Provider name
            requests_per_minute: Maximum requests per minute
        """
        self._limits[provider] = RateLimitInfo(
            requests_per_minute=requests_per_minute, window_start=time.time()
        )
        self._locks[provider] = asyncio.Lock()
        logger.info(
            f"Set rate limit for {provider}: {requests_per_minute} requests/minute"
        )

    async def acquire(self, provider: str) -> bool:
        """Acquire permission to make a request

        Args:
            provider: Provider name

        Returns:
            True if request is allowed, False if rate limited
        """
        if provider not in self._limits:
            return True  # No rate limit set

        async with self._locks[provider]:
            limit_info = self._limits[provider]
            current_time = time.time()

            # Reset window if more than a minute has passed
            if current_time - limit_info.window_start >= 60.0:
                limit_info.requests_made = 0
                limit_info.window_start = current_time

            # Check if we're within the rate limit
            if limit_info.requests_made >= limit_info.requests_per_minute:
                time_until_reset = 60.0 - (current_time - limit_info.window_start)
                logger.warning(
                    f"Rate limit exceeded for {provider}. Reset in {time_until_reset:.1f}s"
                )
                return False

            # Apply minimum interval between requests if needed
            min_interval = 60.0 / limit_info.requests_per_minute
            time_since_last = current_time - limit_info.last_request_time

            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                logger.debug(f"Rate limiting {provider}: sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

            # Record the request
            limit_info.requests_made += 1
            limit_info.last_request_time = time.time()

            logger.debug(
                f"Rate limit for {provider}: {limit_info.requests_made}/{limit_info.requests_per_minute}"
            )
            return True

    def get_remaining_requests(self, provider: str) -> Optional[int]:
        """Get remaining requests in current window

        Args:
            provider: Provider name

        Returns:
            Remaining requests or None if no limit set
        """
        if provider not in self._limits:
            return None

        limit_info = self._limits[provider]
        current_time = time.time()

        # Reset window if more than a minute has passed
        if current_time - limit_info.window_start >= 60.0:
            return limit_info.requests_per_minute

        return max(0, limit_info.requests_per_minute - limit_info.requests_made)

    def get_reset_time(self, provider: str) -> Optional[float]:
        """Get time until rate limit window resets

        Args:
            provider: Provider name

        Returns:
            Seconds until reset or None if no limit set
        """
        if provider not in self._limits:
            return None

        limit_info = self._limits[provider]
        current_time = time.time()

        return max(0, 60.0 - (current_time - limit_info.window_start))


# Global rate limiter instance
rate_limiter = RateLimiter()
