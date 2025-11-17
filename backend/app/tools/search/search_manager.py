from typing import List, Dict, Optional, Union
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchConfig,
    SearchError,
    SearchProviderStatus,
    SearchProvider,
)
from app.tools.search.base_provider import BaseSearchProvider
from app.tools.search.tavily_provider import TavilySearchProvider
from app.tools.search.exa_provider import ExaSearchProvider
from app.config.setting import settings
from app.utils.log_util import get_logger

logger = get_logger(__name__)


class SearchManager:
    """Manages multiple search providers with fallback support"""

    def __init__(self):
        """Initialize search manager with configured providers"""
        self.providers: Dict[SearchProvider, BaseSearchProvider] = {}
        self.default_provider = SearchProvider(settings.SEARCH_DEFAULT_PROVIDER)
        self.fallback_providers = self._parse_fallback_providers()
        self.enable_fallback = settings.SEARCH_ENABLE_FALLBACK

        # Initialize providers
        self._initialize_providers()

    def _parse_fallback_providers(self) -> List[SearchProvider]:
        """Parse fallback providers from settings

        Returns:
            List of fallback provider enums
        """
        fallback_setting = settings.SEARCH_FALLBACK_PROVIDERS
        if isinstance(fallback_setting, str):
            if fallback_setting == "*":
                return [
                    provider
                    for provider in SearchProvider
                    if provider != self.default_provider
                ]
            providers = [p.strip() for p in fallback_setting.split(",")]
        else:
            providers = fallback_setting

        return [
            SearchProvider(p) for p in providers if p != self.default_provider.value
        ]

    def _initialize_providers(self):
        """Initialize all configured search providers"""
        # Initialize Tavily if API key is available
        if settings.TAVILY_API_KEY:
            tavily_config = SearchConfig(
                provider=SearchProvider.TAVILY,
                api_key=settings.TAVILY_API_KEY,
                timeout=settings.SEARCH_TIMEOUT,
                max_results=settings.SEARCH_MAX_RESULTS,
            )
            self.providers[SearchProvider.TAVILY] = TavilySearchProvider(tavily_config)

        # Initialize Exa if API key is available
        if settings.EXA_API_KEY:
            exa_config = SearchConfig(
                provider=SearchProvider.EXA,
                api_key=settings.EXA_API_KEY,
                timeout=settings.SEARCH_TIMEOUT,
                max_results=settings.SEARCH_MAX_RESULTS,
            )
            self.providers[SearchProvider.EXA] = ExaSearchProvider(exa_config)

        logger.info(
            f"Initialized {len(self.providers)} search providers: {list(self.providers.keys())}"
        )

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Perform search with fallback support

        Args:
            request: Search request parameters

        Returns:
            Search response with results

        Raises:
            SearchError: If all providers fail
        """
        # Determine provider order
        target_provider = request.provider or self.default_provider
        providers_to_try = [target_provider]

        if self.enable_fallback:
            # Add fallback providers that aren't already in the list
            for fallback in self.fallback_providers:
                if fallback not in providers_to_try and fallback in self.providers:
                    providers_to_try.append(fallback)

        errors = []

        for provider_enum in providers_to_try:
            if provider_enum not in self.providers:
                error_msg = f"Provider {provider_enum.value} not configured"
                errors.append(error_msg)
                logger.warning(error_msg)
                continue

            provider = self.providers[provider_enum]

            try:
                logger.info(f"Attempting search with provider: {provider_enum.value}")
                response = await provider.search(request)
                logger.info(f"Search successful with provider: {provider_enum.value}")
                return response

            except SearchError as e:
                error_msg = f"Provider {provider_enum.value} failed: {e.message}"
                errors.append(error_msg)
                logger.warning(error_msg)

                # Don't try fallback for certain error types
                if e.error_code in ["INVALID_CONFIG", "AUTH_FAILED"]:
                    break

            except Exception as e:
                error_msg = f"Provider {provider_enum.value} unexpected error: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        # All providers failed
        raise SearchError(
            f"All search providers failed. Errors: {'; '.join(errors)}",
            provider="search_manager",
            error_code="ALL_PROVIDERS_FAILED",
        )

    async def get_provider_status(
        self, provider: Optional[SearchProvider] = None
    ) -> Union[SearchProviderStatus, Dict[SearchProvider, SearchProviderStatus]]:
        """Get status of one or all providers

        Args:
            provider: Specific provider to check, or None for all

        Returns:
            Provider status or dictionary of all statuses
        """
        if provider:
            if provider not in self.providers:
                return SearchProviderStatus(
                    provider=provider,
                    available=False,
                    configured=False,
                    last_error="Provider not configured",
                )
            return await self.providers[provider].health_check()

        # Get status for all providers
        statuses = {}
        for provider_enum, provider_instance in self.providers.items():
            try:
                statuses[provider_enum] = await provider_instance.health_check()
            except Exception as e:
                statuses[provider_enum] = SearchProviderStatus(
                    provider=provider_enum,
                    available=False,
                    configured=provider_instance.validate_config(),
                    last_error=str(e),
                )

        return statuses

    async def get_content(
        self, urls: List[str], provider: Optional[SearchProvider] = None
    ) -> Dict[str, str]:
        """Get content for specific URLs

        Args:
            urls: List of URLs to get content for
            provider: Preferred provider (defaults to Exa if available)

        Returns:
            Dictionary mapping URLs to their content

        Raises:
            SearchError: If content retrieval fails
        """
        # Prefer Exa for content retrieval as it has dedicated endpoint
        target_provider = provider or SearchProvider.EXA

        if target_provider not in self.providers:
            raise SearchError(
                f"Provider {target_provider.value} not available for content retrieval",
                provider="search_manager",
                error_code="PROVIDER_NOT_AVAILABLE",
            )

        provider_instance = self.providers[target_provider]

        if hasattr(provider_instance, "get_content"):
            return await provider_instance.get_content(urls)
        else:
            raise SearchError(
                f"Provider {target_provider.value} does not support content retrieval",
                provider="search_manager",
                error_code="FEATURE_NOT_SUPPORTED",
            )

    async def find_similar(
        self, url: str, num_results: int = 10, provider: Optional[SearchProvider] = None
    ) -> List[SearchResult]:
        """Find similar pages to a given URL

        Args:
            url: URL to find similar pages for
            num_results: Number of similar results to return
            provider: Preferred provider (defaults to Exa if available)

        Returns:
            List of similar search results

        Raises:
            SearchError: If similar search fails
        """
        # Prefer Exa for similarity search as it has dedicated endpoint
        target_provider = provider or SearchProvider.EXA

        if target_provider not in self.providers:
            raise SearchError(
                f"Provider {target_provider.value} not available for similarity search",
                provider="search_manager",
                error_code="PROVIDER_NOT_AVAILABLE",
            )

        provider_instance = self.providers[target_provider]

        if hasattr(provider_instance, "find_similar"):
            return await provider_instance.find_similar(url, num_results)
        else:
            raise SearchError(
                f"Provider {target_provider.value} does not support similarity search",
                provider="search_manager",
                error_code="FEATURE_NOT_SUPPORTED",
            )

    async def close(self):
        """Close all provider connections"""
        for provider in self.providers.values():
            try:
                await provider.close()
            except Exception as e:
                logger.warning(f"Error closing provider: {e}")

    def get_available_providers(self) -> List[SearchProvider]:
        """Get list of available providers

        Returns:
            List of configured provider enums
        """
        return list(self.providers.keys())

    def is_provider_available(self, provider: SearchProvider) -> bool:
        """Check if a provider is available

        Args:
            provider: Provider to check

        Returns:
            True if provider is configured and available
        """
        return provider in self.providers


# Global search manager instance
search_manager = SearchManager()
