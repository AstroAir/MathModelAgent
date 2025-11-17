import pytest
from unittest.mock import AsyncMock, patch
from app.tools.search.search_manager import SearchManager
from app.tools.search.tavily_provider import TavilySearchProvider
from app.tools.search.exa_provider import ExaSearchProvider
from app.tools.web_search_tool import WebSearchTool
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchConfig,
    SearchProvider,
    SearchType,
    SearchError,
)


class TestSearchProviders:
    """Test individual search providers"""

    @pytest.fixture
    def tavily_config(self):
        return SearchConfig(
            provider=SearchProvider.TAVILY,
            api_key="tvly-test-key",
            timeout=30,
            max_results=10,
        )

    @pytest.fixture
    def exa_config(self):
        return SearchConfig(
            provider=SearchProvider.EXA,
            api_key="test-exa-key",
            timeout=30,
            max_results=10,
        )

    def test_tavily_config_validation(self, tavily_config):
        """Test Tavily configuration validation"""
        provider = TavilySearchProvider(tavily_config)
        assert provider.validate_config()  # nosec B101

        # Test invalid config
        invalid_config = SearchConfig(
            provider=SearchProvider.TAVILY,
            api_key="invalid-key",
            timeout=30,
            max_results=10,
        )
        invalid_provider = TavilySearchProvider(invalid_config)
        assert not invalid_provider.validate_config()  # nosec B101

    def test_exa_config_validation(self, exa_config):
        """Test Exa configuration validation"""
        provider = ExaSearchProvider(exa_config)
        assert provider.validate_config()  # nosec B101

        # Test invalid config
        invalid_config = SearchConfig(
            provider=SearchProvider.EXA, api_key="", timeout=30, max_results=10
        )
        invalid_provider = ExaSearchProvider(invalid_config)
        assert not invalid_provider.validate_config()  # nosec B101

    @pytest.mark.asyncio
    async def test_tavily_search_mock(self, tavily_config):
        """Test Tavily search with mocked response"""
        provider = TavilySearchProvider(tavily_config)

        # Mock response data
        mock_response = {
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "content": "Test content",
                    "score": 0.95,
                    "published_date": "2024-01-01T00:00:00Z",
                }
            ],
            "answer": "Test answer",
            "follow_up_questions": ["What is this?"],
        }

        with patch.object(
            provider, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            request = SearchRequest(
                query="test query", search_type=SearchType.GENERAL, max_results=5
            )

            response = await provider.search(request)

            assert isinstance(response, SearchResponse)  # nosec B101
            assert len(response.results) == 1  # nosec B101
            assert response.results[0].title == "Test Result"  # nosec B101
            assert response.results[0].url == "https://example.com"  # nosec B101
            assert response.provider == SearchProvider.TAVILY  # nosec B101

    @pytest.mark.asyncio
    async def test_exa_search_mock(self, exa_config):
        """Test Exa search with mocked response"""
        provider = ExaSearchProvider(exa_config)

        # Mock response data
        mock_response = {
            "results": [
                {
                    "title": "Exa Test Result",
                    "url": "https://exa-example.com",
                    "text": "Exa test content",
                    "score": 0.88,
                    "id": "test-id-123",
                }
            ],
            "autoprompt_string": "Enhanced query",
        }

        with patch.object(
            provider, "_make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            request = SearchRequest(
                query="exa test query", search_type=SearchType.ACADEMIC, max_results=3
            )

            response = await provider.search(request)

            assert isinstance(response, SearchResponse)  # nosec B101
            assert len(response.results) == 1  # nosec B101
            assert response.results[0].title == "Exa Test Result"  # nosec B101
            assert response.results[0].url == "https://exa-example.com"  # nosec B101
            assert response.provider == SearchProvider.EXA  # nosec B101


class TestSearchManager:
    """Test search manager functionality"""

    @pytest.fixture
    def mock_search_manager(self):
        """Create a search manager with mocked providers"""
        manager = SearchManager()

        # Mock providers
        mock_tavily = AsyncMock(spec=TavilySearchProvider)
        mock_exa = AsyncMock(spec=ExaSearchProvider)

        manager.providers = {
            SearchProvider.TAVILY: mock_tavily,
            SearchProvider.EXA: mock_exa,
        }

        return manager, mock_tavily, mock_exa

    @pytest.mark.asyncio
    async def test_search_with_default_provider(self, mock_search_manager):
        """Test search using default provider"""
        manager, mock_tavily, mock_exa = mock_search_manager

        # Mock successful response
        mock_response = SearchResponse(
            results=[
                SearchResult(
                    title="Test", url="https://test.com", content="Test content"
                )
            ],
            query="test",
            provider=SearchProvider.TAVILY,
            search_time=0.5,
        )
        mock_tavily.search.return_value = mock_response

        request = SearchRequest(query="test query")
        response = await manager.search(request)

        assert response == mock_response  # nosec B101
        mock_tavily.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_fallback(self, mock_search_manager):
        """Test search with fallback mechanism"""
        manager, mock_tavily, mock_exa = mock_search_manager
        manager.enable_fallback = True
        manager.fallback_providers = [SearchProvider.EXA]

        # Mock first provider failure and second provider success
        mock_tavily.search.side_effect = SearchError("API Error", "tavily", "API_ERROR")
        mock_response = SearchResponse(
            results=[
                SearchResult(
                    title="Fallback Test",
                    url="https://fallback.com",
                    content="Fallback content",
                )
            ],
            query="test",
            provider=SearchProvider.EXA,
            search_time=0.8,
        )
        mock_exa.search.return_value = mock_response

        request = SearchRequest(query="test query")
        response = await manager.search(request)

        assert response == mock_response  # nosec B101
        mock_tavily.search.assert_called_once()
        mock_exa.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_all_providers_fail(self, mock_search_manager):
        """Test search when all providers fail"""
        manager, mock_tavily, mock_exa = mock_search_manager
        manager.enable_fallback = True
        manager.fallback_providers = [SearchProvider.EXA]

        # Mock both providers failing
        mock_tavily.search.side_effect = SearchError(
            "Tavily Error", "tavily", "API_ERROR"
        )
        mock_exa.search.side_effect = SearchError("Exa Error", "exa", "API_ERROR")

        request = SearchRequest(query="test query")

        with pytest.raises(SearchError) as exc_info:
            await manager.search(request)

        assert "All search providers failed" in str(exc_info.value)  # nosec B101


class TestWebSearchTool:
    """Test the web search tool integration"""

    @pytest.fixture
    def web_search_tool(self):
        return WebSearchTool()

    @pytest.mark.asyncio
    async def test_web_search_tool_success(self, web_search_tool):
        """Test successful web search tool execution"""
        mock_response = SearchResponse(
            results=[
                SearchResult(
                    title="Python Tutorial",
                    url="https://python.org/tutorial",
                    content="Learn Python programming basics",
                )
            ],
            query="python tutorial",
            provider=SearchProvider.TAVILY,
            search_time=1.2,
        )

        with patch("app.tools.web_search_tool.search_manager") as mock_manager:
            mock_manager.search.return_value = mock_response

            result = await web_search_tool.search(
                query="python tutorial", search_type="general", max_results=5
            )

            assert result.result is not None  # nosec B101
            assert "Python Tutorial" in result.result  # nosec B101
            assert "https://python.org/tutorial" in result.result  # nosec B101
            assert result.error is None  # nosec B101

    @pytest.mark.asyncio
    async def test_web_search_tool_error(self, web_search_tool):
        """Test web search tool error handling"""
        with patch("app.tools.web_search_tool.search_manager") as mock_manager:
            mock_manager.search.side_effect = SearchError(
                "Network Error", "tavily", "NETWORK_ERROR"
            )

            result = await web_search_tool.search(
                query="test query", search_type="general"
            )

            assert result.error is not None  # nosec B101
            assert "Search failed" in result.error  # nosec B101
            assert "Network Error" in result.error  # nosec B101


class TestSearchIntegration:
    """Test integration with agent system"""

    @pytest.mark.asyncio
    async def test_search_result_formatting(self):
        """Test that search results are properly formatted for agents"""
        results = [
            SearchResult(
                title="Mathematical Modeling Techniques",
                url="https://math.example.com/modeling",
                content="This article covers various mathematical modeling techniques including differential equations, optimization methods, and statistical modeling approaches.",
            ),
            SearchResult(
                title="Python for Data Science",
                url="https://python.example.com/datascience",
                content="Learn how to use Python libraries like NumPy, Pandas, and Matplotlib for data analysis and visualization.",
            ),
        ]

        tool = WebSearchTool()
        formatted = tool._format_results(results)

        assert "1. Mathematical Modeling Techniques" in formatted  # nosec B101
        assert "2. Python for Data Science" in formatted  # nosec B101
        assert "https://math.example.com/modeling" in formatted  # nosec B101
        assert "https://python.example.com/datascience" in formatted  # nosec B101

    def test_empty_search_results(self):
        """Test handling of empty search results"""
        tool = WebSearchTool()
        formatted = tool._format_results([])

        assert formatted == "No results found."  # nosec B101


if __name__ == "__main__":
    pytest.main([__file__])
